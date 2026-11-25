"""Tables of classes, participants, jobs, results and audio. Migrations: backend/migrations."""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Double,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()

ID = String(128)

classes = Table(
    "classes",
    metadata,
    Column("class_id", ID, primary_key=True),
    Column("external_class_id", ID, nullable=False),
    Column("participant_count", Integer, nullable=False),
    Column("consent_reference", String(128), nullable=False),
    Column("submitted_by", ID, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Idempotency-Key of the submission and the sha256 of its audio and metadata (spec
    # class-processing). NULL keys never collide, so submissions without the header are new.
    Column("idempotency_key", String(128)),
    Column("request_fingerprint", String(64)),
    UniqueConstraint("submitted_by", "idempotency_key", name="classes_idempotency_key"),
)

participants = Table(
    "participants",
    metadata,
    Column("class_id", ID, ForeignKey("classes.class_id", ondelete="CASCADE"), primary_key=True),
    Column("participant_id", ID, primary_key=True),
    Column("position", Integer, nullable=False),
    Column("role", String(16), nullable=False),
    Column("display_name", String(200)),
)

jobs = Table(
    "jobs",
    metadata,
    Column("job_id", ID, primary_key=True),
    Column(
        "class_id",
        ID,
        ForeignKey("classes.class_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    Column("state", String(32), nullable=False, index=True),
    Column("stage", String(32)),
    Column("attempt", Integer, nullable=False, server_default="0"),
    Column("error_code", String(64)),
    Column("error_message", Text),
    Column("error_retryable", Boolean),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    # Last time the job entered the queue: claim_next takes the oldest (FIFO, ADR-0002).
    Column("queued_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("attempt >= 0", name="jobs_attempt_non_negative"),
)

results = Table(
    "results",
    metadata,
    Column("class_id", ID, ForeignKey("classes.class_id", ondelete="CASCADE"), primary_key=True),
    Column("result_version", Integer, nullable=False),
    Column("body", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

audio_assets = Table(
    "audio_assets",
    metadata,
    Column("audio_id", ID, primary_key=True),
    Column(
        "class_id",
        ID,
        ForeignKey("classes.class_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    # Opaque name of the file in the AudioStorage: never sent to a client or a log.
    Column("storage_key", ID, nullable=False, unique=True),
    Column("format", String(16), nullable=False),
    Column("size_bytes", BigInteger, nullable=False),
    Column("duration_seconds", Double, nullable=False),
    Column("sha256", String(64), nullable=False),
    Column("received_at", DateTime(timezone=True), nullable=False),
    # Purge date (spec audio-retention): maintenance looks for the expired ones.
    Column("expires_at", DateTime(timezone=True), nullable=False, index=True),
    Column("deleted_at", DateTime(timezone=True)),
    CheckConstraint("size_bytes >= 0", name="audio_assets_size_non_negative"),
    CheckConstraint("duration_seconds >= 0", name="audio_assets_duration_non_negative"),
)
