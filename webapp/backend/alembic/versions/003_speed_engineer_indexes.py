"""Add speed-engineer default sort composite index on reviews(created_at, id)

Revision ID: 003_speed_engineer_indexes
Revises: 002_supabase_perf_indexes
Create Date: 2026-11-23 08:44:00.000000
"""
from typing import Sequence, Union
from alembic import op


revision: str = "003_speed_engineer_indexes"
down_revision: Union[str, None] = "002_supabase_perf_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_reviews_created_at_id",
        "reviews",
        ["created_at", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reviews_created_at_id", table_name="reviews")
