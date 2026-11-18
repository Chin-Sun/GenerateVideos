"""Portable relational persistence; create_all is the initial schema migration."""
from sqlalchemy import JSON, Column, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    owner_user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    head_version_id = Column(String, nullable=False)
    created_at = Column(Float, nullable=False)


class Version(Base):
    __tablename__ = "versions"
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    parent_id = Column(String)
    number = Column(Integer, nullable=False)
    request_text = Column(String, nullable=False)
    patch_json = Column(JSON, nullable=False)
    settings_json = Column(JSON, nullable=False)
    created_at = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint("project_id", "number"),)


class Shot(Base):
    __tablename__ = "shots"
    version_id = Column(String, primary_key=True)
    shot_id = Column(String, primary_key=True)
    position = Column(Integer, nullable=False)
    spec_json = Column(JSON, nullable=False)


class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    sha256 = Column(String, nullable=False)
    path = Column(String, nullable=False)
    mime = Column(String, nullable=False, default="video/mp4")
    duration_seconds = Column(Float, nullable=False)
    has_audio = Column(Integer, nullable=False)
    provenance = Column(String, nullable=False)
    provider_task_id = Column(String)
    quality_json = Column(JSON, nullable=False)
    license_json = Column(JSON, nullable=False, default=dict)


class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    version_id = Column(String, nullable=False, index=True)
    shot_id = Column(String)
    kind = Column(String, nullable=False)
    state = Column(String, nullable=False, index=True)
    identity_json = Column(JSON, nullable=False)
    provider_task_id = Column(String)
    submission_intent = Column(JSON)
    lease_owner = Column(String)
    lease_token = Column(String)
    lease_expires_at = Column(Float, nullable=False, default=0)
    attempts = Column(Integer, nullable=False, default=0)
    next_run_at = Column(Float, nullable=False, default=0)
    error_json = Column(JSON)
    result_json = Column(JSON, nullable=False, default=dict)


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(String, primary_key=True)
    version_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    identity_json = Column(JSON, nullable=False)
    target_key = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    state = Column(String, nullable=False)
    file_key = Column(String)
    message_id = Column(String)
    attempts = Column(Integer, nullable=False, default=0)
    lease_owner = Column(String)
    lease_token = Column(String)
    lease_expires_at = Column(Float, nullable=False, default=0)
    error_json = Column(JSON)
    __table_args__ = (UniqueConstraint("version_id", "target_key", "purpose"),)


class EventReceipt(Base):
    __tablename__ = "event_receipts"
    tenant_id = Column(String, primary_key=True)
    event_id = Column(String, primary_key=True)
    job_id = Column(String, nullable=False)


class Budget(Base):
    __tablename__ = "budgets"
    authorization_id = Column(String, primary_key=True)
    used = Column(Integer, nullable=False, default=0)
