"""create assignment tables

Revision ID: 0001_create_assignment_tables
Revises:
Create Date: 2026-05-09
"""

from collections.abc import Sequence

from alembic import op

import mega_ai.db.pgv.models  # noqa: F401
from mega_ai.db.pgv.db import Base

revision: str = "0001_create_assignment_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
