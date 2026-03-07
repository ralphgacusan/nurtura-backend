"""add server default for care_spaces.updated_at

Revision ID: 3cdea087d98a
Revises: 8e8136514dac
Create Date: 2026-03-01 20:28:11.940609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cdea087d98a'
down_revision: Union[str, Sequence[str], None] = '8e8136514dac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill existing NULLs
    op.execute("UPDATE care_spaces SET updated_at = now() WHERE updated_at IS NULL")

    # Ensure column has server default
    op.alter_column(
        "care_spaces",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False
    )

def downgrade() -> None:
    op.alter_column(
        "care_spaces",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False
    )