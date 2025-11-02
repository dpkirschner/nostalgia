"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS staging")

    op.create_table(
        'kc_food_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip', sa.String(length=10), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('inspection_date', sa.Date(), nullable=True),
        sa.Column('raw_line', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='staging'
    )

    op.create_table(
        'locations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('parcel_pin', sa.String(length=50), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('last_seen', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_locations_lat_lon', 'locations', ['lat', 'lon'], unique=False)

    op.create_table(
        'tenancies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.String(length=64), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, server_default='restaurant'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sources', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tenancies_location_id', 'tenancies', ['location_id'], unique=False)

    op.create_table(
        'memory_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.String(length=64), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('start_year', sa.Integer(), nullable=True),
        sa.Column('end_year', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('proof_url', sa.String(length=500), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='anon'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_memory_submissions_location_id', 'memory_submissions', ['location_id'], unique=False)
    op.create_index('idx_memory_submissions_status', 'memory_submissions', ['status'], unique=False)

    op.execute("""
        CREATE OR REPLACE VIEW v_latest_tenancy AS
        SELECT DISTINCT ON (location_id)
            location_id,
            business_name,
            category,
            is_current
        FROM tenancies
        ORDER BY location_id, is_current DESC, end_date DESC NULLS FIRST, created_at DESC
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_latest_tenancy")
    op.drop_index('idx_memory_submissions_status', table_name='memory_submissions')
    op.drop_index('idx_memory_submissions_location_id', table_name='memory_submissions')
    op.drop_table('memory_submissions')
    op.drop_index('idx_tenancies_location_id', table_name='tenancies')
    op.drop_table('tenancies')
    op.drop_index('idx_locations_lat_lon', table_name='locations')
    op.drop_table('locations')
    op.drop_table('kc_food_inspections', schema='staging')
    op.execute("DROP SCHEMA IF EXISTS staging CASCADE")
