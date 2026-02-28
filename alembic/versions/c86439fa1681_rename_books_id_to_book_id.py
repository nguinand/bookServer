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


BOOK_FK_CONFIG = (
    ("book_access", "book_access_ibfk_1", None),
    ("book_authors", "book_authors_ibfk_2", "CASCADE"),
    ("book_genres", "book_genres_ibfk_1", "CASCADE"),
    ("book_identifiers", "book_identifiers_ibfk_1", "CASCADE"),
    ("book_sale_info", "book_sale_info_ibfk_1", "CASCADE"),
    ("bookcase_books", "bookcase_books_ibfk_1", "CASCADE"),
    ("user_book_attributes", "user_book_attributes_ibfk_1", "CASCADE"),
    ("user_book_state", "user_book_state_ibfk_1", "CASCADE"),
)


def _get_books_foreign_keys(table_name: str) -> list[dict[str, object]]:
    inspector = sa.inspect(op.get_bind())
    return [
        foreign_key
        for foreign_key in inspector.get_foreign_keys(table_name)
        if foreign_key.get("referred_table") == "books"
        and foreign_key.get("constrained_columns") == ["book_id"]
    ]


def _drop_books_foreign_keys(table_name: str) -> None:
    for foreign_key in _get_books_foreign_keys(table_name):
        foreign_key_name = foreign_key.get("name")
        if foreign_key_name:
            op.drop_constraint(foreign_key_name, table_name, type_="foreignkey")


def _has_books_book_id_foreign_key(table_name: str) -> bool:
    return any(
        foreign_key.get("referred_columns") == ["book_id"]
        for foreign_key in _get_books_foreign_keys(table_name)
    )


def upgrade() -> None:
    """Upgrade schema."""
    for table_name, _, _ in BOOK_FK_CONFIG:
        _drop_books_foreign_keys(table_name)

    book_columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("books")}
    if "id" in book_columns and "book_id" not in book_columns:
        op.alter_column(
            "books",
            "id",
            new_column_name="book_id",
            existing_type=sa.Integer(),
            existing_nullable=False,
            existing_autoincrement=True,
        )
    elif "book_id" not in book_columns:
        raise RuntimeError("books table must include either id or book_id before migration")

    book_indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("books")}
    if "ix_books_id" in book_indexes:
        op.drop_index("ix_books_id", table_name="books")
    if "ix_books_book_id" not in book_indexes:
        op.create_index("ix_books_book_id", "books", ["book_id"], unique=False)

    for table_name, constraint_name, ondelete in BOOK_FK_CONFIG:
        if _has_books_book_id_foreign_key(table_name):
            continue

        create_fk_kwargs = {}
        if ondelete:
            create_fk_kwargs["ondelete"] = ondelete

        op.create_foreign_key(
            constraint_name,
            table_name,
            "books",
            ["book_id"],
            ["book_id"],
            **create_fk_kwargs,
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
