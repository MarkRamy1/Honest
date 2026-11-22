"""Add Supabase/Postgres composite and FK performance indexes

Revision ID: 002_supabase_perf_indexes
Revises: 001_initial_schema
Create Date: 2026-11-22 17:02:00.000000
"""
from typing import Sequence, Union
from alembic import op


revision: str = "002_supabase_perf_indexes"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"], unique=False)
    op.create_index(
        "ix_reviews_product_tier_created",
        "reviews",
        ["product_name", "tier", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_stores_trust_platform",
        "stores_reputation",
        ["trust_score", "platform"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stores_trust_platform", table_name="stores_reputation")
    op.drop_index("ix_reviews_product_tier_created", table_name="reviews")
    op.drop_index("ix_reviews_user_id", table_name="reviews")
