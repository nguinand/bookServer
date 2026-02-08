from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.crud.author_crud import AuthorCrud, AuthorModel


def test_create_author_commits():
    mock_session = MagicMock()
    crud = AuthorCrud()
    author = AuthorModel(name="Fake_author", google_books_id="123", bio="fake bio")

    created_author = crud.create_author(author, mock_session)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert created_author
    assert created_author.name == "Fake_author"
    assert created_author.google_books_id == "123"
    assert created_author.bio == "fake bio"


@pytest.mark.parametrize(
    "input_data,should_raise",
    [
        ({"name": "fake author", "google_books_id": "123", "bio": "fake_bio"}, False),
        ({"name": "fake _author"}, False),
        ({"google_books_id": "123"}, True),  # Missing required field `name`
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
