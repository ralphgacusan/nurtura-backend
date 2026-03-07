"""add default to updated_at

Revision ID: 8e8136514dac
Revises: 5025a6467194
Create Date: 2026-03-01 20:21:23.178897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e8136514dac'
down_revision: Union[str, Sequence[str], None] = '5025a6467194'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill existing rows with NULL updated_at
    op.execute("UPDATE care_spaces SET updated_at = now() WHERE updated_at IS NULL")

    # Alter column to have server default of current timestamp
    op.alter_column(
        'care_spaces',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        existing_nullable=False
    )

def downgrade() -> None:
    op.alter_column(
        'care_spaces',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False
    )
