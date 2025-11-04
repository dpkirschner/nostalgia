"""full precision coordinates

Revision ID: 003
Revises: 002
Create Date: 2025-11-03 22:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing views before recreating with new column names
    op.execute("DROP VIEW IF EXISTS staging.v_kc_latest")
    op.execute("DROP VIEW IF EXISTS staging.v_kc_norm")

    op.execute(
        """
        CREATE VIEW staging.v_kc_norm AS
        SELECT
            UPPER(TRIM(business_name)) AS biz,
            UPPER(TRIM(address)) AS street,
            UPPER(COALESCE(NULLIF(TRIM(city), ''), 'SEATTLE')) AS city,
            COALESCE(NULLIF(TRIM(state), ''), 'WA') AS state,
            NULLIF(TRIM(zip), '') AS zip,
            latitude AS lat,
            longitude AS lon,
            inspection_date AS inspection_dt,
            id AS row_id
        FROM staging.kc_food_inspections
        WHERE
            business_name IS NOT NULL
            AND TRIM(business_name) != ''
            AND address IS NOT NULL
            AND TRIM(address) != ''
            AND latitude IS NOT NULL
            AND longitude IS NOT NULL
    """
    )

    op.execute(
        """
        CREATE VIEW staging.v_kc_latest AS
        SELECT DISTINCT ON (ROUND(lat::numeric, 6), ROUND(lon::numeric, 6), street)
            biz,
            street,
            city,
            state,
            zip,
            lat,
            lon,
            inspection_dt,
            row_id
        FROM staging.v_kc_norm
        ORDER BY
            ROUND(lat::numeric, 6),
            ROUND(lon::numeric, 6),
            street,
            inspection_dt DESC NULLS LAST,
            row_id DESC
    """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS staging.v_kc_latest")
    op.execute("DROP VIEW IF EXISTS staging.v_kc_norm")
    op.execute(
        """
        CREATE OR REPLACE VIEW staging.v_kc_norm AS
        SELECT
            UPPER(TRIM(business_name)) AS biz,
            UPPER(TRIM(address)) AS street,
            UPPER(COALESCE(NULLIF(TRIM(city), ''), 'SEATTLE')) AS city,
            COALESCE(NULLIF(TRIM(state), ''), 'WA') AS state,
            NULLIF(TRIM(zip), '') AS zip,
            ROUND(latitude::numeric, 6) AS lat6,
            ROUND(longitude::numeric, 6) AS lon6,
            inspection_date AS inspection_dt,
            id AS row_id
        FROM staging.kc_food_inspections
        WHERE
            business_name IS NOT NULL
            AND TRIM(business_name) != ''
            AND address IS NOT NULL
            AND TRIM(address) != ''
            AND latitude IS NOT NULL
            AND longitude IS NOT NULL
    """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW staging.v_kc_latest AS
        SELECT DISTINCT ON (lat6, lon6, street)
            biz,
            street,
            city,
            state,
            zip,
            lat6,
            lon6,
            inspection_dt,
            row_id
        FROM staging.v_kc_norm
        ORDER BY
            lat6,
            lon6,
            street,
            inspection_dt DESC NULLS LAST,
            row_id DESC
    """
    )
