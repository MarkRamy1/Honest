"""Initial schema for users, verified_products, stores_reputation, and reviews

Revision ID: 001_initial
Revises: 
Create Date: 2026-10-16 12:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Verified Products
    op.create_table(
        'verified_products',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('original_msrp', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('high_copy_avg_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('copy_avg_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('authentic_materials', sa.Text(), nullable=False),
        sa.Column('fake_materials', sa.Text(), nullable=False),
        sa.Column('verification_telltales', sa.JSON(), nullable=True),
        sa.Column('recommended_sources', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index(op.f('ix_verified_products_id'), 'verified_products', ['id'], unique=False)
    op.create_index(op.f('ix_verified_products_name'), 'verified_products', ['name'], unique=False)
    op.create_index(op.f('ix_verified_products_brand'), 'verified_products', ['brand'], unique=False)
    op.create_index(op.f('ix_verified_products_category'), 'verified_products', ['category'], unique=False)

    # 3. Stores Reputation
    op.create_table(
        'stores_reputation',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('store_name', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=100), nullable=False),
        sa.Column('specialty_tier', sa.String(length=50), nullable=False),
        sa.Column('trust_score', sa.SmallInteger(), nullable=False),
        sa.Column('material_honesty_rating', sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column('verified_url', sa.String(length=1000), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index(op.f('ix_stores_reputation_id'), 'stores_reputation', ['id'], unique=False)

    # 4. Reviews
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tier', sa.String(length=50), nullable=False),
        sa.Column('rating', sa.SmallInteger(), nullable=False),
        sa.Column('material_accuracy_rating', sa.SmallInteger(), nullable=False),
        sa.Column('price_paid', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('store_purchased_from', sa.String(length=255), nullable=True),
        sa.Column('product_url', sa.String(length=1000), nullable=True),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('is_verified_buyer', sa.Boolean(), nullable=False),
        sa.Column('upvotes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_product_name'), 'reviews', ['product_name'], unique=False)
    op.create_index(op.f('ix_reviews_tier'), 'reviews', ['tier'], unique=False)


def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('stores_reputation')
    op.drop_table('verified_products')
    op.drop_table('users')
