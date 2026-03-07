"""add server default for care_spaces.updated_at

Revision ID: 3d0e3432cd86
Revises: 3cdea087d98a
Create Date: 2026-03-01 20:31:03.530092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d0e3432cd86'
down_revision: Union[str, Sequence[str], None] = '3cdea087d98a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
