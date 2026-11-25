"""Audio of each class and the Idempotency-Key of its submission (add-class-reception).

Revision ID: 0002
Revises: 0001

Classes created before this revision have no audio: the migration leaves them as they are.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID = sa.String(128)


def upgrade() -> None:
    op.add_column("classes", sa.Column("idempotency_key", sa.String(128)))
    op.add_column("classes", sa.Column("request_fingerprint", sa.String(64)))
    op.create_unique_constraint(
        "classes_idempotency_key", "classes", ["submitted_by", "idempotency_key"]
    )
    op.create_table(
        "audio_assets",
        sa.Column("audio_id", ID, primary_key=True),
        sa.Column(
            "class_id",
            ID,
            sa.ForeignKey("classes.class_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("storage_key", ID, nullable=False, unique=True),
        sa.Column("format", sa.String(16), nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("duration_seconds", sa.Double, nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("size_bytes >= 0", name="audio_assets_size_non_negative"),
        sa.CheckConstraint("duration_seconds >= 0", name="audio_assets_duration_non_negative"),
    )
    op.create_index("ix_audio_assets_expires_at", "audio_assets", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_audio_assets_expires_at", table_name="audio_assets")
    op.drop_table("audio_assets")
    op.drop_constraint("classes_idempotency_key", "classes", type_="unique")
    op.drop_column("classes", "request_fingerprint")
    op.drop_column("classes", "idempotency_key")
