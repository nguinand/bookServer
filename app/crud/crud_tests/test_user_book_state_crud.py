from typing import Generator
from unittest.mock import MagicMock, Mock

import pytest

from app.crud import user_book_state_crud as crud
from app.db.db_models.user_book_state import ReadingStatus, UserBookState
from app.models.user_book_state import UserBookStateModel


@pytest.fixture
def session() -> Generator[MagicMock, None, None]:
    yield MagicMock()


@pytest.fixture
def existing_record() -> UserBookState:
    return UserBookState(
        user_id=1,
        book_id=2,
        reading_status=ReadingStatus.WANT_TO_READ,
        current_page=10,
        percent_complete=20,
    )


@pytest.fixture
def replacement_model() -> UserBookStateModel:
    return UserBookStateModel(
        id=5,
        user_id=3,
        book_id=4,
        reading_status=ReadingStatus.READING,
        current_page=30,
        percent_complete=40,
    )


def test_create_user_book_state_commits(session: MagicMock) -> None:
    model = UserBookStateModel(user_id=1, book_id=2)

    created = crud.create_user_book_state(model, session)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    assert created.user_id == 1
    assert created.book_id == 2
    assert created.reading_status == ReadingStatus.WANT_TO_READ


def test_update_user_book_state_raises_without_id(session: MagicMock) -> None:
    model = UserBookStateModel(user_id=1, book_id=2)

    with pytest.raises(ValueError):
        crud.update_user_book_state(model, session)


def test_update_user_book_state_updates_fields_and_commits(
    monkeypatch: pytest.MonkeyPatch,
    session: MagicMock,
    existing_record: UserBookState,
    replacement_model: UserBookStateModel,
) -> None:
    lookup_mock: Mock = Mock(return_value=existing_record)
    monkeypatch.setattr(crud, "get_user_book_state_by_id", lookup_mock)

    updated = crud.update_user_book_state(replacement_model, session)

    session.commit.assert_called_once()
    lookup_mock.assert_called_once_with(replacement_model.id, session)
    assert updated is not None
    assert updated.user_id == replacement_model.user_id
    assert updated.book_id == replacement_model.book_id
    assert updated.reading_status == ReadingStatus.READING
    assert updated.current_page == replacement_model.current_page
    assert updated.percent_complete == replacement_model.percent_complete


def test_delete_user_book_state_by_id(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    record = UserBookState(user_id=1, book_id=2)
    lookup_mock: Mock = Mock(return_value=record)

    monkeypatch.setattr(crud, "get_user_book_state_by_id", lookup_mock)

    result = crud.delete_user_book_state_by_id(7, session)

    lookup_mock.assert_called_once_with(7, session)
    session.delete.assert_called_once_with(record)
    session.commit.assert_called_once()
    assert result is True


def test_delete_user_book_state_by_id_not_found(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    lookup_mock: Mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_user_book_state_by_id", lookup_mock)

    result = crud.delete_user_book_state_by_id(7, session)

    lookup_mock.assert_called_once_with(7, session)
    session.delete.assert_not_called()
    session.commit.assert_not_called()
    assert result is False
