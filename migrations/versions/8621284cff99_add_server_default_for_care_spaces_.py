"""add server default for care_spaces.updated_at

Revision ID: 8621284cff99
Revises: 588ecf4aca0c
Create Date: 2026-03-01 21:25:53.014370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8621284cff99'
down_revision: Union[str, Sequence[str], None] = '588ecf4aca0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
