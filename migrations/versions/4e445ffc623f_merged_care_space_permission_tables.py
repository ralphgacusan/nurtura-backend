"""Merged Care Space Permission Tables

Revision ID: 4e445ffc623f
Revises: bfa4f82c7bd4
Create Date: 2026-03-07 18:43:38.147068
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4e445ffc623f'
down_revision: Union[str, Sequence[str], None] = 'bfa4f82c7bd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old table
    op.drop_index(op.f('ix_care_space_member_permissions_permission_id'), table_name='care_space_member_permissions')
    op.drop_table('care_space_member_permissions')

    # Add new columns as nullable first
    op.add_column('care_space_members', sa.Column('can_manage_care_space', sa.Boolean(), nullable=True))
    op.add_column('care_space_members', sa.Column('can_manage_tasks', sa.Boolean(), nullable=True))

    # Fill defaults for existing rows
    op.execute("UPDATE care_space_members SET can_manage_care_space = FALSE")
    op.execute("UPDATE care_space_members SET can_manage_tasks = FALSE")

    # Alter columns to NOT NULL now that defaults exist
    op.alter_column('care_space_members', 'can_manage_care_space', nullable=False)
    op.alter_column('care_space_members', 'can_manage_tasks', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('care_space_members', 'can_manage_tasks')
    op.drop_column('care_space_members', 'can_manage_care_space')

    # Recreate old table
    op.create_table(
        'care_space_member_permissions',
        sa.Column('permission_id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('care_space_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('can_create_tasks', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('can_edit_tasks', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('can_delete_tasks', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('can_assign_tasks', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('can_add_members', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('can_remove_members', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('added_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('removed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['care_space_id'], ['care_spaces.care_space_id'],
                                name=op.f('care_space_member_permissions_care_space_id_fkey')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'],
                                name=op.f('care_space_member_permissions_user_id_fkey')),
        sa.PrimaryKeyConstraint('permission_id', name=op.f('care_space_member_permissions_pkey'))
    )
    op.create_index(op.f('ix_care_space_member_permissions_permission_id'),
                    'care_space_member_permissions', ['permission_id'], unique=False)