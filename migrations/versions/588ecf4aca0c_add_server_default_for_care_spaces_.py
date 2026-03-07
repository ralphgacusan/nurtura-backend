"""add server default for care_spaces.updated_at

Revision ID: 588ecf4aca0c
Revises: 3d0e3432cd86
Create Date: 2026-03-01 21:20:19.100582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '588ecf4aca0c'
down_revision: Union[str, Sequence[str], None] = '3d0e3432cd86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
