"""add login_status

Revision ID: b2f9a7c4d6e1
Revises: 7f537b1485c1
Create Date: 2026-05-28 21:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f9a7c4d6e1"
down_revision: Union[str, Sequence[str], None] = "7f537b1485c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "login_status",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("last_failed_login_attempt_at", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "locked",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("locked_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("login_status")
