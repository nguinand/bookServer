import os
from typing import Generator
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")

from app.crud import book_access_crud as crud
from app.db.db_models.book_access import BookAccess
from app.models.access_info import AccessInfoModel


@pytest.fixture
def session() -> Generator[MagicMock, None, None]:
    yield MagicMock()


def test_create_access_info_attaches_book_id(session: MagicMock) -> None:
    model = AccessInfoModel(country="US", viewability="PARTIAL")

    created = crud.create_access_info(model, book_id=12, session=session)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    assert created.book_id == 12
    assert created.country == "US"


def test_get_access_info_by_book_id_returns_one_record(session: MagicMock) -> None:
    record = BookAccess(id=1, book_id=12)
    scalar_result = session.scalars.return_value
    scalar_result.one_or_none.return_value = record

    result = crud.get_access_info_by_book_id(12, session)

    session.scalars.assert_called_once()
    scalar_result.one_or_none.assert_called_once()
    assert result is record
