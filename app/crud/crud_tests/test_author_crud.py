import os
from unittest.mock import MagicMock, Mock

import pytest
from pydantic import ValidationError

# Avoid import-time db_manager initialization errors in unit tests.
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")

from app.crud import author_crud as crud
from app.db.db_models.author import Author
from app.db.db_models.book import Book
from app.models.author import AuthorModel
from app.models.book import BookModel


def test_create_author_commits():
    mock_session = MagicMock()
    author = AuthorModel(name="Fake_author", bio="fake bio")

    created_author = crud.create_author(author, mock_session)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert created_author
    assert created_author.name == "Fake_author"
    assert created_author.bio == "fake bio"


@pytest.mark.parametrize(
    "input_data,should_raise",
    [
        ({"name": "fake author", "bio": "fake_bio"}, False),
        ({"name": "fake _author"}, False),
        ({"bio": "fake_bio"}, True),  # Missing required field `name`
        ({"name": None}, True),  # `name` is required, cannot be None
    ],
)
def test_author_model_validation(input_data, should_raise):
    if should_raise:
        with pytest.raises(ValidationError):
            AuthorModel(**input_data)
    else:
        model = AuthorModel(**input_data)
        assert model.name


def test_update_author_assigns_book_records_and_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    author_record = Author(id=1, name="Old Name", bio="Old bio")
    author_record.books = []
    book_record = Book(book_id=2, google_books_id="google-id", title="Book Title")
    replacement = AuthorModel.model_construct(
        id=1,
        name="New Name",
        bio="New bio",
        books=[BookModel.model_construct(book_id=2)],
    )
    author_lookup: Mock = Mock(return_value=author_record)
    book_lookup: Mock = Mock(return_value=book_record)
    monkeypatch.setattr(crud, "get_author_by_id", author_lookup)
    monkeypatch.setattr(crud, "get_book_by_book_id", book_lookup)

    updated = crud.update_author(replacement, session)

    author_lookup.assert_called_once_with(1, session)
    book_lookup.assert_called_once_with(2, session)
    session.commit.assert_called_once()
    assert updated is author_record
    assert updated.name == "New Name"
    assert updated.bio == "New bio"
    assert updated.books == [book_record]


def test_update_author_raises_when_related_book_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    author_record = Author(id=1, name="Old Name", bio="Old bio")
    author_record.books = []
    replacement = AuthorModel.model_construct(
        id=1,
        name="New Name",
        bio="New bio",
        books=[BookModel.model_construct(book_id=404)],
    )
    monkeypatch.setattr(crud, "get_author_by_id", Mock(return_value=author_record))
    monkeypatch.setattr(crud, "get_book_by_book_id", Mock(return_value=None))

    with pytest.raises(ValueError, match="Book not found with ID - 404"):
        crud.update_author(replacement, session)

    session.commit.assert_not_called()
