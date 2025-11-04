"""add unit and display_slot

Revision ID: 004
Revises: 003
Create Date: 2025-11-03 23:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("locations", sa.Column("unit", sa.String(), nullable=True))
    op.add_column(
        "locations",
        sa.Column("display_slot", sa.SmallInteger(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("locations", "display_slot")
    op.drop_column("locations", "unit")
