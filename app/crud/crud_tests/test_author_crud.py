import os
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

# Avoid import-time db_manager initialization errors in unit tests.
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")

from app.crud import author_crud as crud
from app.models.author import AuthorModel


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
