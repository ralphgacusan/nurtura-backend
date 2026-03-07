"""Added Care Space Join Code Table

Revision ID: 2f002d74cbaa
Revises: 5c7a498478d0
Create Date: 2026-03-07 23:20:38.306152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2f002d74cbaa'
down_revision: Union[str, Sequence[str], None] = '5c7a498478d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use the existing enum instead of trying to create it again
    role_enum = postgresql.ENUM(
        'owner', 'editor', 'viewer',
        name='role_in_space_enum',
        create_type=False  # Prevent duplicate creation
    )

    op.create_table(
        'care_space_join_codes',
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('care_space_id', sa.Integer(), nullable=False),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['care_space_id'], ['care_spaces.care_space_id']),
        sa.PrimaryKeyConstraint('code')
    )

    op.create_index(
        op.f('ix_care_space_join_codes_code'),
        'care_space_join_codes',
        ['code'],
        unique=False
    )

    # Remove old care_space_code column and index if needed
    op.drop_index(op.f('ix_care_spaces_care_space_code'), table_name='care_spaces')
    op.drop_column('care_spaces', 'care_space_code')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'care_spaces',
        sa.Column('care_space_code', sa.VARCHAR(length=20), autoincrement=False, nullable=True)
    )
    op.create_index(
        op.f('ix_care_spaces_care_space_code'),
        'care_spaces',
        ['care_space_code'],
        unique=True
    )
    op.drop_index(op.f('ix_care_space_join_codes_code'), table_name='care_space_join_codes')
    op.drop_table('care_space_join_codes')