"""Tables of classes, participants, jobs and results. Migrations live in backend/migrations."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
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
    Column("class_id", ID, ForeignKey("classes.class_id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("storage_path", String(512), nullable=False),
    Column("original_filename", String(255), nullable=False),
    Column("content_type", String(64), nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("received_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("expires_at", DateTime(timezone=True), nullable=False),  # RD-01: 14 días desde recepción
    Column("purged_at", DateTime(timezone=True)),  # NULL hasta que se purga
)
