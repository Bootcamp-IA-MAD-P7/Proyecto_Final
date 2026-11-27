"""Time of the next attempt of a job in retry_wait (add-diarized-transcription).

Revision ID: 0003
Revises: 0002

Existing jobs are left as they are: none of them is waiting for a retry.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("next_attempt_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("jobs", "next_attempt_at")
