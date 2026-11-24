"""Classes, participants, jobs and results of the walking skeleton.

Revision ID: 0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID = sa.String(128)


def _timestamp(name: str) -> sa.Column:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def _class_fk() -> sa.ForeignKey:
    return sa.ForeignKey("classes.class_id", ondelete="CASCADE")


def upgrade() -> None:
    op.create_table(
        "classes",
        sa.Column("class_id", ID, primary_key=True),
        sa.Column("external_class_id", ID, nullable=False),
        sa.Column("participant_count", sa.Integer, nullable=False),
        sa.Column("consent_reference", sa.String(128), nullable=False),
        sa.Column("submitted_by", ID, nullable=False),
        _timestamp("created_at"),
    )
    op.create_table(
        "participants",
        sa.Column("class_id", ID, _class_fk(), primary_key=True),
        sa.Column("participant_id", ID, primary_key=True),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("display_name", sa.String(200)),
    )
    op.create_table(
        "jobs",
        sa.Column("job_id", ID, primary_key=True),
        sa.Column("class_id", ID, _class_fk(), nullable=False, unique=True),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("stage", sa.String(32)),
        sa.Column("attempt", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(64)),
        sa.Column("error_message", sa.Text),
        sa.Column("error_retryable", sa.Boolean),
        _timestamp("created_at"),
        _timestamp("queued_at"),
        _timestamp("updated_at"),
        sa.CheckConstraint("attempt >= 0", name="jobs_attempt_non_negative"),
    )
    op.create_index("ix_jobs_state", "jobs", ["state"])
    op.create_table(
        "results",
        sa.Column("class_id", ID, _class_fk(), primary_key=True),
        sa.Column("result_version", sa.Integer, nullable=False),
        sa.Column("body", postgresql.JSONB, nullable=False),
        _timestamp("created_at"),
    )


def downgrade() -> None:
    op.drop_table("results")
    op.drop_index("ix_jobs_state", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("participants")
    op.drop_table("classes")
