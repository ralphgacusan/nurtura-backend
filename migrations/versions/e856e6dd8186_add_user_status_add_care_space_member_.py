"""Add user status, add care_space_member_permissions, merge care_space_dependents

Revision ID: e856e6dd8186
Revises: 8621284cff99
Create Date: 2026-03-07 02:58:56.230884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e856e6dd8186'
down_revision: Union[str, Sequence[str], None] = '8621284cff99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
