"""kc food inspections views

Revision ID: 002
Revises: 001
Create Date: 2025-01-01 01:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_kc_food_inspections_lat_lon",
        "kc_food_inspections",
        ["latitude", "longitude"],
        unique=False,
        schema="staging",
    )
    op.create_index(
        "idx_kc_food_inspections_inspection_date",
        "kc_food_inspections",
        ["inspection_date"],
        unique=False,
        schema="staging",
    )

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


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS staging.v_kc_latest")
    op.execute("DROP VIEW IF EXISTS staging.v_kc_norm")
    op.drop_index(
        "idx_kc_food_inspections_inspection_date",
        table_name="kc_food_inspections",
        schema="staging",
    )
    op.drop_index(
        "idx_kc_food_inspections_lat_lon", table_name="kc_food_inspections", schema="staging"
    )
