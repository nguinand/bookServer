"""error log table has uuid col

Revision ID: 7f537b1485c1
Revises: e0b4c8d5f2a1
Create Date: 2026-04-27 19:59:18.566235

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7f537b1485c1"
down_revision: Union[str, Sequence[str], None] = "e0b4c8d5f2a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def get_index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    """Upgrade schema."""
    column_names = get_column_names("error_logs")
    if "error_id" not in column_names:
        op.add_column(
            "error_logs", sa.Column("error_id", sa.String(length=36), nullable=True)
        )
    if "exception_type" not in column_names:
        op.add_column(
            "error_logs",
            sa.Column("exception_type", sa.String(length=255), nullable=True),
        )

    op.execute(
        sa.text(
            "UPDATE error_logs "
            "SET error_id = UUID() "
            "WHERE error_id IS NULL OR error_id = ''"
        )
    )
    op.execute(
        sa.text(
            "UPDATE error_logs "
            "SET exception_type = 'unknown' "
            "WHERE exception_type IS NULL OR exception_type = ''"
        )
    )
    op.alter_column(
        "error_logs",
        "error_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.alter_column(
        "error_logs",
        "exception_type",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    index_name = op.f("ix_error_logs_error_id")
    if index_name not in get_index_names("error_logs"):
        op.create_index(index_name, "error_logs", ["error_id"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    column_names = get_column_names("error_logs")
    index_name = op.f("ix_error_logs_error_id")
    if index_name in get_index_names("error_logs"):
        op.drop_index(index_name, table_name="error_logs")
    if "exception_type" in column_names:
        op.drop_column("error_logs", "exception_type")
    if "error_id" in column_names:
        op.drop_column("error_logs", "error_id")
