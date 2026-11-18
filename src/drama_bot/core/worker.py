"""One-step durable worker. Run repeatedly from a separate process; no in-memory queue."""
import threading
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from drama_bot.contracts import (
    GenerationRequest,
    Identity,
    PaidCallsDisabled,
    QualityEvidence,
    RenderRequest,
    ShotSpec,
)

from .models import Asset, Budget, Delivery, Job, Shot, Version
from .service import Conflict, LeaseLost, uid


class Worker:
    def __init__(self, service, provider, renderer, transport, settings, owner=None,
                 lease_seconds=120):
        self.service, self.provider, self.renderer = service, provider, renderer
        self.transport, self.settings = transport, settings
        self.owner, self.lease_seconds = owner or uid(), lease_seconds

    @contextmanager
    def _heartbeat(self, job):
        stop = threading.Event()
        lost = []

        def beat():
            while not stop.wait(max(0.1, self.lease_seconds / 3)):
                try:
                    self.service.heartbeat(job.id, job.lease_token, self.lease_seconds)
                except Exception as exc:
                    lost.append(exc)
                    return
        thread = threading.Thread(target=beat, daemon=True)
        thread.start()
        try:
            yield
            if lost:
                raise LeaseLost("heartbeat failed") from lost[0]
        finally:
            stop.set()
            thread.join()

    def _reserve_budget(self, db):
        s = self.settings
        if not (s.paid_calls_enabled and s.paid_authorization_id and s.max_paid_submissions > 0
                and s.ppapi_api_key and s.ppapi_api_key.get_secret_value()):
            raise PaidCallsDisabled("付费生成禁用：需要独立授权、凭据与预算")
        # The initial budget row is seeded before claiming work, avoiding insert races here.
        n = db.execute(update(Budget).where(Budget.authorization_id == s.paid_authorization_id,
                                           Budget.used < s.max_paid_submissions)
                       .values(used=Budget.used + 1)).rowcount
        if n != 1:
            raise PaidCallsDisabled("授权次数预算已用尽")

    def _seed_budget(self):
        if self.settings.paid_authorization_id:
            try:
                with self.service.sessions.begin() as db:
                    if not db.get(Budget, self.settings.paid_authorization_id):
                        db.add(Budget(authorization_id=self.settings.paid_authorization_id, used=0))
            except IntegrityError:
                pass  # another worker seeded the same authorization

    def run_once(self):
        self._seed_budget()
        job = self.service.claim(self.owner, self.lease_seconds)
        if not job:
            return self.deliver_once()
        resume = job.state
        try:
            with self._heartbeat(job):
                if job.kind == "generate":
                    self._generate(job)
                else:
                    self._render(job)
        except LeaseLost:
            pass  # a stale worker must not overwrite the new owner
        except PaidCallsDisabled as exc:
            self._fail(job, "blocked", type(exc).__name__, "queued")
        except Exception as exc:
            # Persist only exception type: third-party strings may contain credentials/URLs.
            with self.service.sessions() as db:
                current = db.get(Job, job.id)
                resume = current.state
            if resume == "submitting":
                self._fail(job, "unknown_submission", type(exc).__name__, "unknown_submission")
            else:
                self._fail(job, "failed", type(exc).__name__, resume)
        return True

    def _fail(self, job, state, error_type, resume):
        try:
            self.service.save_job(job.id, job.lease_token, state=state,
                                  error_json={"type": error_type, "resume_state": resume},
                                  lease_token=None, lease_expires_at=0)
        except LeaseLost:
            pass

    def _release(self, job, **values):
        self.service.save_job(job.id, job.lease_token, lease_token=None,
                              lease_expires_at=0, **values)

    def _attempt_output(self, job):
        """Never reuse a published path after a crash or lease takeover.

        Unregistered outputs remain immutable orphans for operator inspection.
        Asset registration and fenced job success commit together; a stale worker
        may publish its own file but cannot register it or overwrite a successor.
        """
        if not job.lease_token:
            raise LeaseLost("output requires an active attempt")
        return self.service.asset_root / f"{job.id}-{job.attempts}-{job.lease_token}.mp4"

    def _generate(self, job):
        with self.service.sessions() as db:
            shot = ShotSpec.model_validate(db.get(Shot, (job.version_id, job.shot_id)).spec_json)
            settings = db.get(Version, job.version_id).settings_json
            references = []
            for aid in shot.reference_asset_ids:
                asset = db.get(Asset, aid)
                references.append({"asset_id": aid, "path": asset.path, "sha256": asset.sha256})
        if not job.provider_task_id:
            with self.service.sessions.begin() as db:
                self.service.fenced(db, job.id, job.lease_token, state="submitting",
                                    submission_intent={"version_id": job.version_id, "shot_id": job.shot_id})
                self._reserve_budget(db)
            # Every ambiguous exception after this point is unknown, never automatic submit retry.
            submission = self.provider.submit(GenerationRequest(job_id=job.id, version_id=job.version_id,
                                            shot=shot, aspect_ratio=settings["aspect_ratio"], references=tuple(references)))
            self.service.save_job(job.id, job.lease_token, state="generating",
                                  provider_task_id=submission.provider_task_id)
            job.provider_task_id = submission.provider_task_id
        with self.service.sessions() as db:
            current = db.get(Job, job.id)
            saved = current.result_json
        if saved.get("download_url"):
            url = saved["download_url"]
        else:
            poll = self.provider.poll(job.provider_task_id)
            if poll.state == "pending":
                self._release(job, state="generating", next_run_at=self.service.clock() + 5)
                return
            if poll.state == "failed":
                self._fail(job, "failed", "ProviderFailed", "generating")
                return
            if not poll.download_url:
                raise ValueError("provider success without URL")
            url = poll.download_url
            self.service.save_job(job.id, job.lease_token, state="downloading", result_json={"download_url": url})
        result = self.provider.download(url, self._attempt_output(job))
        with self.service.sessions.begin() as db:
            asset = self.service.register_asset(db, job.project_id, result, job.provider_task_id)
            self.service.fenced(db, job.id, job.lease_token, state="succeeded",
                                result_json={"asset_id": asset.id, "sha256": asset.sha256},
                                lease_token=None, lease_expires_at=0, error_json=None)

    def _render(self, job):
        with self.service.sessions() as db:
            version = db.get(Version, job.version_id)
            settings = version.settings_json
            shots = list(db.scalars(select(Shot).where(Shot.version_id == job.version_id).order_by(Shot.position)))
            assets = []
            for shot in shots:
                source = db.scalar(select(Job).where(Job.version_id == job.version_id, Job.shot_id == shot.shot_id))
                if source.state != "succeeded":
                    self._release(job, state="queued", next_run_at=self.service.clock() + 5)
                    return
                asset = db.get(Asset, source.result_json["asset_id"])
                # Hash verification also catches local tampering before composition.
                import hashlib
                if hashlib.sha256(Path(asset.path).read_bytes()).hexdigest() != asset.sha256:
                    raise ValueError("source hash mismatch")
                assets.append(self.service.asset_result(asset))
        self.service.save_job(job.id, job.lease_token, state="rendering")
        result = self.renderer.render(RenderRequest(version_id=job.version_id, assets=tuple(assets),
                        output_path=self._attempt_output(job), **settings))
        with self.service.sessions.begin() as db:
            asset = self.service.register_asset(db, job.project_id, result)
            self.service.fenced(db, job.id, job.lease_token, state="succeeded",
                                result_json={"asset_id": asset.id, "sha256": asset.sha256,
                                             "quality_status": "unverified", "preview": settings["preview"]},
                                lease_token=None, lease_expires_at=0, error_json=None)
            identity = Identity.model_validate(job.identity_json)
            purpose = "draft_preview" if settings["preview"] else "final"
            db.add(Delivery(id=uid(), version_id=job.version_id, asset_id=asset.id,
                            identity_json=identity.model_dump(), target_key=f"{identity.tenant_id}:{identity.chat_id}:{identity.user_id}",
                            purpose=purpose, state="queued" if purpose == "draft_preview" else "quality_blocked"))

    def release_reviewed_delivery(self, delivery_id):
        """Trusted operator hook after reviewing the exact rendered asset."""
        with self.service.sessions.begin() as db:
            delivery = db.get(Delivery, delivery_id)
            asset = db.get(Asset, delivery.asset_id)
            if asset.provenance == "synthetic" or not QualityEvidence.model_validate(asset.quality_json).approved:
                raise Conflict("成片质量尚未审核通过")
            if delivery.purpose == "draft_preview":
                existing = db.scalar(select(Delivery).where(Delivery.version_id == delivery.version_id,
                                      Delivery.target_key == delivery.target_key, Delivery.purpose == "final"))
                if existing:
                    return existing.id
                final = Delivery(id=uid(), version_id=delivery.version_id, asset_id=delivery.asset_id,
                                 identity_json=delivery.identity_json, target_key=delivery.target_key,
                                 purpose="final", state="queued")
                db.add(final)
                return final.id
            if delivery.state != "quality_blocked":
                raise Conflict("not quality blocked")
            delivery.state = "queued"
            return delivery.id

    def _delivery_update(self, did, token, **values):
        with self.service.sessions.begin() as db:
            n = db.execute(update(Delivery).where(Delivery.id == did, Delivery.lease_token == token,
                                                  Delivery.lease_expires_at > self.service.clock()).values(**values)).rowcount
            if n != 1:
                raise LeaseLost("delivery lease expired")

    def _delivery_call(self, delivery_id, token, fn, *args):
        stop = threading.Event()
        lost = []

        def beat():
            while not stop.wait(max(0.1, self.lease_seconds / 3)):
                try:
                    self._delivery_update(delivery_id, token,
                                          lease_expires_at=self.service.clock() + self.lease_seconds)
                except Exception as exc:
                    lost.append(exc)
                    return
        thread = threading.Thread(target=beat, daemon=True)
        thread.start()
        try:
            result = fn(*args)
            if lost:
                raise LeaseLost("delivery heartbeat failed") from lost[0]
            return result
        finally:
            stop.set()
            thread.join()

    def deliver_once(self):
        now, token = self.service.clock(), uid()
        with self.service.sessions.begin() as db:
            db.execute(update(Delivery).where(Delivery.state == "sending", Delivery.lease_expires_at <= now)
                       .values(state="unknown_delivery", lease_token=None))
            ids = list(db.scalars(select(Delivery.id).where(Delivery.state.in_(["queued", "uploading", "uploaded", "retry_wait"]),
                                                           Delivery.lease_expires_at <= now)))
            delivery = None
            for did in ids:
                n = db.execute(update(Delivery).where(Delivery.id == did, Delivery.lease_expires_at <= now,
                                                      Delivery.state.in_(["queued", "uploading", "uploaded", "retry_wait"]))
                               .values(lease_owner=self.owner, lease_token=token,
                                       lease_expires_at=now + self.lease_seconds, attempts=Delivery.attempts + 1)).rowcount
                if n:
                    delivery = db.get(Delivery, did)
                    asset = db.get(Asset, delivery.asset_id)
                    break
        if delivery is None:
            return False
        sending = False
        try:
            quality = QualityEvidence.model_validate(asset.quality_json)
            if delivery.purpose != "draft_preview" and (asset.provenance == "synthetic" or not quality.approved):
                self._delivery_update(delivery.id, token, state="quality_blocked", lease_token=None, lease_expires_at=0)
                return True
            import hashlib
            if hashlib.sha256(Path(asset.path).read_bytes()).hexdigest() != asset.sha256:
                raise ValueError("delivery asset hash mismatch")
            if not delivery.file_key:
                self._delivery_update(delivery.id, token, state="uploading")
                file_key = self._delivery_call(delivery.id, token, self.transport.upload, self.service.asset_result(asset))
                self._delivery_update(delivery.id, token, state="uploaded", file_key=file_key)
            else:
                file_key = delivery.file_key
            # Delivery ID includes explicit draft marker, available to protocol transports for labeling.
            # Transports MUST support this draft path; absent support fails closed.
            if delivery.purpose == "draft_preview" and not hasattr(self.transport, "send_preview"):
                self._delivery_update(delivery.id, token, state="preview_transport_blocked", lease_token=None, lease_expires_at=0)
                return True
            self._delivery_update(delivery.id, token, state="sending")
            sending = True
            identity = Identity.model_validate(delivery.identity_json)
            if delivery.purpose == "draft_preview":
                message_id = self._delivery_call(delivery.id, token, self.transport.send_preview, identity, file_key, delivery.id)
            else:
                message_id = self._delivery_call(delivery.id, token, self.transport.send, identity, file_key, delivery.id)
            self._delivery_update(delivery.id, token, state="succeeded", message_id=message_id,
                                  lease_token=None, lease_expires_at=0, error_json=None)
        except LeaseLost:
            pass
        except Exception as exc:
            try:
                self._delivery_update(delivery.id, token, state="unknown_delivery" if sending else "failed",
                                      error_json={"type": type(exc).__name__}, lease_token=None, lease_expires_at=0)
            except LeaseLost:
                pass
        return True

    def retry_delivery(self, identity, delivery_id):
        with self.service.sessions.begin() as db:
            delivery = db.get(Delivery, delivery_id)
            if not delivery:
                raise Conflict("delivery not found")
            version = db.get(Version, delivery.version_id)
            self.service._project(db, identity, version.project_id)
            if delivery.state not in {"failed", "preview_transport_blocked"}:
                raise Conflict("不确定发送不可盲目重试")
            delivery.state, delivery.lease_expires_at = "queued", 0
