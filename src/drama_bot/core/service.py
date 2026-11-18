"""Transactional application service. Identities must come from verified ingress."""
import hashlib
import time
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import Field, model_validator
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from drama_bot.contracts import AssetResult, FrozenModel, Identity, QualityEvidence, ShotSpec

from .models import Asset, Base, EventReceipt, Job, Project, Shot, Version


def uid():
    return uuid4().hex


class Forbidden(PermissionError):
    pass


class Conflict(RuntimeError):
    pass


class LeaseLost(RuntimeError):
    pass


class CreationRequest(FrozenModel):
    name: str = Field(min_length=1)
    request_text: str = ""
    shots: tuple[ShotSpec, ...] = Field(min_length=1, max_length=30)
    aspect_ratio: Literal["9:16", "16:9", "1:1"] = "9:16"
    target_seconds: float = Field(default=60, gt=0)
    tolerance_seconds: float = Field(default=5, ge=0)
    preview: bool = True

    @model_validator(mode="after")
    def validate_shots(self):
        if len({s.shot_id for s in self.shots}) != len(self.shots):
            raise ValueError("duplicate shot_id")
        if not any(s.dialogue for s in self.shots):
            raise ValueError("中文对白剧情必须包含角色台词；请提交结构化分镜")
        if any(s.selected_asset_id for s in self.shots):
            raise ValueError("asset selection is managed internally")
        return self


class PatchRequest(FrozenModel):
    expected_head_version_id: str
    shot_id: str
    patch: dict


class CoreService:
    def __init__(self, database_url, allowed_user_ids=(), allowed_tenant_ids=(),
                 asset_root=Path("var/assets"), clock=time.time):
        if database_url.startswith("sqlite:///") and database_url != "sqlite:///:memory:":
            Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        self.users, self.tenants = set(allowed_user_ids), set(allowed_tenant_ids)
        self.asset_root = Path(asset_root).resolve()
        self.asset_root.mkdir(parents=True, exist_ok=True)
        self.clock = clock

    def authorize(self, identity):
        if identity.user_id not in self.users or identity.tenant_id not in self.tenants:
            raise Forbidden("身份不在白名单")

    def _project(self, db, identity, project_id):
        self.authorize(identity)
        project = db.get(Project, project_id)
        if not project or (project.tenant_id, project.owner_user_id) != (identity.tenant_id, identity.user_id):
            raise Forbidden("项目不可访问")
        return project

    def _jobs(self, db, project_id, version_id, identity, shots, reused=None):
        reused = reused or {}
        ids = []
        for shot in shots:
            job = Job(id=uid(), project_id=project_id, version_id=version_id,
                      shot_id=shot.shot_id, kind="generate", state="succeeded" if shot.shot_id in reused else "queued",
                      identity_json=identity.model_dump(), result_json=reused.get(shot.shot_id, {}))
            db.add(job)
            ids.append(job.id)
        render = Job(id=uid(), project_id=project_id, version_id=version_id,
                     kind="render", state="queued", identity_json=identity.model_dump(), result_json={})
        db.add(render)
        ids.append(render.id)
        return ids

    def _receipt(self, db, identity, event_id):
        receipt = db.get(EventReceipt, (identity.tenant_id, event_id))
        if receipt:
            job = db.get(Job, receipt.job_id)
            self._project(db, identity, job.project_id)
            if job.identity_json != identity.model_dump():
                raise Forbidden("事件身份不匹配")
            return {"project_id": job.project_id, "version_id": job.version_id,
                    "job_ids": list(db.scalars(select(Job.id).where(Job.version_id == job.version_id)))}

    def create_project(self, identity: Identity, request: CreationRequest, event_id=None):
        self.authorize(identity)
        try:
            with self.sessions.begin() as db:
                if event_id and (existing := self._receipt(db, identity, event_id)):
                    return existing
                pid, vid = uid(), uid()
                db.add(Project(id=pid, tenant_id=identity.tenant_id, owner_user_id=identity.user_id,
                               name=request.name, head_version_id=vid, created_at=self.clock()))
                settings = request.model_dump(mode="json", exclude={"shots", "name", "request_text"})
                db.add(Version(id=vid, project_id=pid, number=1, request_text=request.request_text,
                               patch_json={}, settings_json=settings, created_at=self.clock()))
                for pos, shot in enumerate(request.shots):
                    self._check_references(db, pid, shot)
                    db.add(Shot(version_id=vid, shot_id=shot.shot_id, position=pos, spec_json=shot.model_dump(mode="json")))
                ids = self._jobs(db, pid, vid, identity, request.shots)
                if event_id:
                    db.add(EventReceipt(tenant_id=identity.tenant_id, event_id=event_id, job_id=ids[-1]))
                return {"project_id": pid, "version_id": vid, "job_ids": ids}
        except IntegrityError:
            if event_id:
                with self.sessions() as db:
                    if existing := self._receipt(db, identity, event_id):
                        return existing
            raise Conflict("并发创建冲突") from None

    def _check_references(self, db, pid, shot):
        for aid in shot.reference_asset_ids:
            asset = db.get(Asset, aid)
            if not asset or asset.project_id != pid:
                raise Forbidden("引用素材不可访问")

    def patch_version(self, identity, project_id, request: PatchRequest):
        if not request.patch or set(request.patch) - {"prompt", "dialogue", "duration_seconds", "reference_asset_ids"}:
            raise ValueError("只允许结构化镜头 patch；自然语言理解未配置，请确认字段")
        try:
            with self.sessions.begin() as db:
                project = self._project(db, identity, project_id)
                old = request.expected_head_version_id
                if project.head_version_id != old:
                    raise Conflict("版本已更新，请重新读取")
                version = db.get(Version, old)
                shots = list(db.scalars(select(Shot).where(Shot.version_id == old).order_by(Shot.position)))
                if request.shot_id not in {s.shot_id for s in shots}:
                    raise ValueError("镜头不存在")
                vid = uid()
                changed = db.execute(update(Project).where(Project.id == project_id, Project.head_version_id == old)
                                     .values(head_version_id=vid)).rowcount
                if changed != 1:
                    raise Conflict("并发修订冲突")
                db.add(Version(id=vid, project_id=project_id, parent_id=old, number=version.number + 1,
                               request_text=version.request_text, patch_json=request.model_dump(mode="json"),
                               settings_json=version.settings_json, created_at=self.clock()))
                specs, reused = [], {}
                for shot in shots:
                    spec = ShotSpec.model_validate({**shot.spec_json, **(request.patch if shot.shot_id == request.shot_id else {})})
                    self._check_references(db, project_id, spec)
                    specs.append(spec)
                    db.add(Shot(version_id=vid, shot_id=spec.shot_id, position=shot.position, spec_json=spec.model_dump(mode="json")))
                    if shot.shot_id != request.shot_id:
                        previous = db.scalar(select(Job).where(Job.version_id == old, Job.shot_id == shot.shot_id, Job.state == "succeeded"))
                        if previous:
                            reused[shot.shot_id] = previous.result_json
                if not any(s.dialogue for s in specs):
                    raise ValueError("必须保留中文对白")
                ids = self._jobs(db, project_id, vid, identity, specs, reused)
                return {"project_id": project_id, "version_id": vid, "job_ids": ids}
        except IntegrityError:
            raise Conflict("并发修订冲突") from None

    def get_project(self, identity, project_id):
        with self.sessions() as db:
            p = self._project(db, identity, project_id)
            versions = list(db.scalars(select(Version).where(Version.project_id == p.id).order_by(Version.number)))
            return {"id": p.id, "name": p.name, "head_version_id": p.head_version_id,
                    "versions": [{"id": v.id, "number": v.number, "parent_id": v.parent_id,
                                  "settings": v.settings_json, "shots": [s.spec_json for s in db.scalars(select(Shot).where(Shot.version_id == v.id).order_by(Shot.position))]}
                                 for v in versions]}

    def get_job(self, identity, job_id):
        with self.sessions() as db:
            j = db.get(Job, job_id)
            if not j:
                raise Forbidden("任务不可访问")
            self._project(db, identity, j.project_id)
            return {"id": j.id, "state": j.state, "kind": j.kind, "version_id": j.version_id,
                    "provider_task_id": j.provider_task_id, "error": j.error_json,
                    "result": {k: v for k, v in j.result_json.items() if k != "download_url"}}

    def claim(self, owner, lease_seconds=120):
        now = self.clock()
        with self.sessions.begin() as db:
            # A crash between external submit and ID persistence must never cause resubmission.
            db.execute(update(Job).where(Job.state == "submitting", Job.provider_task_id.is_(None),
                                         Job.lease_expires_at <= now).values(state="unknown_submission", lease_token=None))
            candidates = list(db.scalars(select(Job.id).where(Job.state.in_(["queued", "generating", "downloading", "rendering", "retry_wait"]),
                                                                Job.lease_expires_at <= now, Job.next_run_at <= now).order_by(Job.kind, Job.id)))
            for jid in candidates:
                token = uid()
                changed = db.execute(update(Job).where(Job.id == jid, Job.lease_expires_at <= now,
                                                        Job.state.in_(["queued", "generating", "downloading", "rendering", "retry_wait"]))
                                     .values(lease_owner=owner, lease_token=token, lease_expires_at=now + lease_seconds, attempts=Job.attempts + 1)).rowcount
                if changed:
                    return db.get(Job, jid)
        return None

    def fenced(self, db, job_id, token, **values):
        n = db.execute(update(Job).where(Job.id == job_id, Job.lease_token == token,
                                        Job.lease_expires_at > self.clock()).values(**values)).rowcount
        if n != 1:
            raise LeaseLost("worker lease expired or replaced")

    def save_job(self, job_id, token, **values):
        with self.sessions.begin() as db:
            self.fenced(db, job_id, token, **values)

    def heartbeat(self, job_id, token, seconds=120):
        self.save_job(job_id, token, lease_expires_at=self.clock() + seconds)

    def retry_job(self, identity, job_id):
        with self.sessions.begin() as db:
            job = db.get(Job, job_id)
            if not job:
                raise Forbidden("任务不可访问")
            self._project(db, identity, job.project_id)
            if job.state not in {"failed", "blocked"}:
                raise Conflict("仅明确失败/禁用任务可重试；未知受理必须先对账")
            job.state = (job.error_json or {}).get("resume_state", "queued")
            job.error_json = None
            job.next_run_at = 0

    def reconcile_submission(self, identity, job_id, provider_task_id):
        if not provider_task_id:
            raise ValueError("必须提供经供应商确认的任务 ID")
        with self.sessions.begin() as db:
            job = db.get(Job, job_id)
            if not job:
                raise Forbidden("任务不可访问")
            self._project(db, identity, job.project_id)
            if job.state != "unknown_submission":
                raise Conflict("不是待对账任务")
            job.provider_task_id, job.state, job.lease_expires_at = provider_task_id, "generating", 0

    def register_asset(self, db, project_id, result: AssetResult, provider_task_id=None):
        path = result.path.resolve()
        if not path.is_relative_to(self.asset_root):
            raise ValueError("asset outside controlled root")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != result.sha256:
            raise ValueError("asset missing or hash mismatch")
        # Provider/renderer assertions never count as trusted human review.
        quality = QualityEvidence(synthetic=result.provenance == "synthetic").model_dump(mode="json")
        asset = Asset(id=uid(), project_id=project_id, sha256=result.sha256, path=str(path),
                      duration_seconds=result.duration_seconds, has_audio=result.has_audio,
                      provenance=result.provenance, provider_task_id=provider_task_id,
                      quality_json=quality, license_json={})
        db.add(asset)
        return asset

    @staticmethod
    def asset_result(asset):
        return AssetResult(path=Path(asset.path), sha256=asset.sha256, duration_seconds=asset.duration_seconds,
                           has_audio=bool(asset.has_audio), provenance=asset.provenance,
                           quality=QualityEvidence.model_validate(asset.quality_json))

    def record_review(self, asset_id, evidence: QualityEvidence):
        """Trusted operator-only hook, intentionally not exposed via HTTP or user commands."""
        with self.sessions.begin() as db:
            asset = db.get(Asset, asset_id)
            if not asset or asset.provenance == "synthetic" or evidence.synthetic:
                raise ValueError("synthetic/missing asset cannot receive real review")
            asset.quality_json = evidence.model_dump(mode="json")

    def export_project(self, identity, project_id, version_id=None):
        manifest = self.get_project(identity, project_id)
        vid = version_id or manifest["head_version_id"]
        if vid not in {v["id"] for v in manifest["versions"]}:
            raise Forbidden("版本不可访问")
        with self.sessions() as db:
            jobs = list(db.scalars(select(Job).where(Job.version_id == vid)))
            if any(j.state != "succeeded" for j in jobs):
                raise Conflict("素材/渲染尚未齐备，不能导出完整工程")
            assets = []
            for j in jobs:
                a = db.get(Asset, j.result_json.get("asset_id"))
                if not a or not Path(a.path).is_file() or hashlib.sha256(Path(a.path).read_bytes()).hexdigest() != a.sha256:
                    raise Conflict("素材缺失或校验失败")
                assets.append({"id": a.id, "shot_id": j.shot_id, **self.asset_result(a).model_dump(mode="json")})
            return {"project": manifest, "version_id": vid, "assets": assets}
