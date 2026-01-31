"""rename books.id to book_id

Revision ID: c86439fa1681
Revises: 937c2f2e0a4e
Create Date: 2026-01-28 23:04:06.916779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c86439fa1681"
down_revision: Union[str, Sequence[str], None] = "937c2f2e0a4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("book_authors_ibfk_2", "book_authors", type_="foreignkey")
    op.drop_constraint("book_genres_ibfk_1", "book_genres", type_="foreignkey")
    op.drop_constraint("book_identifiers_ibfk_1", "book_identifiers", type_="foreignkey")
    op.drop_constraint("book_sale_info_ibfk_1", "book_sale_info", type_="foreignkey")
    op.drop_constraint("bookcase_books_ibfk_1", "bookcase_books", type_="foreignkey")
    op.drop_constraint(
        "user_book_attributes_ibfk_1", "user_book_attributes", type_="foreignkey"
    )
    op.drop_constraint("user_book_state_ibfk_1", "user_book_state", type_="foreignkey")

    op.alter_column(
        "books",
        "id",
        new_column_name="book_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
        existing_autoincrement=True,
    )

    op.drop_index(op.f("ix_books_id"), table_name="books")
    op.create_index(op.f("ix_books_book_id"), "books", ["book_id"], unique=False)

    op.create_foreign_key(
        "book_access_ibfk_1",
        "book_access",
        "books",
        ["book_id"],
        ["book_id"],
    )
    op.create_foreign_key(
        "book_authors_ibfk_2",
        "book_authors",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "book_genres_ibfk_1",
        "book_genres",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "book_identifiers_ibfk_1",
        "book_identifiers",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "book_sale_info_ibfk_1",
        "book_sale_info",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "bookcase_books_ibfk_1",
        "bookcase_books",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_book_attributes_ibfk_1",
        "user_book_attributes",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_book_state_ibfk_1",
        "user_book_state",
        "books",
        ["book_id"],
        ["book_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("user_book_state_ibfk_1", "user_book_state", type_="foreignkey")
    op.drop_constraint(
        "user_book_attributes_ibfk_1", "user_book_attributes", type_="foreignkey"
    )
    op.drop_constraint("bookcase_books_ibfk_1", "bookcase_books", type_="foreignkey")
    op.drop_constraint("book_sale_info_ibfk_1", "book_sale_info", type_="foreignkey")
    op.drop_constraint("book_identifiers_ibfk_1", "book_identifiers", type_="foreignkey")
    op.drop_constraint("book_genres_ibfk_1", "book_genres", type_="foreignkey")
    op.drop_constraint("book_authors_ibfk_2", "book_authors", type_="foreignkey")
    op.drop_constraint("book_access_ibfk_1", "book_access", type_="foreignkey")

    op.drop_index(op.f("ix_books_book_id"), table_name="books")
    op.alter_column(
        "books",
        "book_id",
        new_column_name="id",
        existing_type=sa.Integer(),
        existing_nullable=False,
        existing_autoincrement=True,
    )
    op.create_index(op.f("ix_books_id"), "books", ["id"], unique=False)

    op.create_foreign_key(
        "book_access_ibfk_1",
        "book_access",
        "books",
        ["book_id"],
        ["id"],
    )
    op.create_foreign_key(
        "book_authors_ibfk_2",
        "book_authors",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "book_genres_ibfk_1",
        "book_genres",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "book_identifiers_ibfk_1",
        "book_identifiers",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "book_sale_info_ibfk_1",
        "book_sale_info",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "bookcase_books_ibfk_1",
        "bookcase_books",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_book_attributes_ibfk_1",
        "user_book_attributes",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_book_state_ibfk_1",
        "user_book_state",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
