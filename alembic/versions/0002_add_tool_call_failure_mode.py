"""add tool call failure mode

Revision ID: 0002_add_tool_call_failure_mode
Revises: 0001_create_assignment_tables
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_tool_call_failure_mode"
down_revision: str | None = "0001_create_assignment_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tool_calls", sa.Column("failure_mode", sa.String(length=80), nullable=True))
    op.create_index("ix_tool_calls_failure_mode", "tool_calls", ["failure_mode"])


def downgrade() -> None:
    op.drop_index("ix_tool_calls_failure_mode", table_name="tool_calls")
    op.drop_column("tool_calls", "failure_mode")
