"""create notifications table

Revision ID: e03cbd4ab891
Revises: e04fa3d98ae7
Create Date: 2026-04-08 03:10:18.964494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e03cbd4ab891'
down_revision: Union[str, Sequence[str], None] = 'e04fa3d98ae7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("read", sa.Boolean, nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("notifications")