import os
from unittest.mock import MagicMock, Mock

import pytest

# Avoid import-time db_manager initialization errors in unit tests.
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")

from app.crud import user_crud as crud
from app.db.db_models.user import User
from app.models.user import UserModel
from app.utils.error_logger import ErrorLogOperation


def make_user_model(user_id: int | None = 1) -> UserModel:
    return UserModel.model_construct(
        id=user_id,
        first_name="Test",
        last_name="User",
        username="test_user",
        email="test@example.com",
        role="user",
        avatar_id=None,
        status_id=None,
        created_at=None,
        last_login=None,
    )


def make_user(user_id: int = 1) -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username="test_user",
        email="test@example.com",
        password_hash="hashed-password",
        role="user",
    )


def test_create_user_exception_reraises_without_error_recorder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    db_manager_mock = MagicMock()
    db_manager_mock.commit_or_raise.side_effect = RuntimeError("commit failed")
    monkeypatch.setattr(crud, "db_manager", db_manager_mock)
    monkeypatch.setattr(
        crud.PasswordHandler,
        "hash_password",
        Mock(return_value="hashed-password"),
    )

    with pytest.raises(RuntimeError, match="commit failed"):
        crud.create_user(make_user_model(user_id=None), "password1", session)

    db_manager_mock.commit_or_raise.assert_called_once_with(
        session, operation=ErrorLogOperation.CREATE_USER
    )
    assert not hasattr(crud, "ErrorLogRecorder")


def test_update_user_exception_reraises_without_error_recorder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    db_manager_mock = MagicMock()
    db_manager_mock.commit_or_raise.side_effect = RuntimeError("commit failed")
    monkeypatch.setattr(crud, "db_manager", db_manager_mock)
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))

    with pytest.raises(RuntimeError, match="commit failed"):
        crud.update_user(make_user_model(), session)

    db_manager_mock.commit_or_raise.assert_called_once_with(
        session, operation=ErrorLogOperation.UPDATE_USER
    )
    assert not hasattr(crud, "ErrorLogRecorder")


def test_delete_user_exception_reraises_without_error_recorder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    db_manager_mock = MagicMock()
    db_manager_mock.commit_or_raise.side_effect = RuntimeError("commit failed")
    monkeypatch.setattr(crud, "db_manager", db_manager_mock)
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))

    with pytest.raises(RuntimeError, match="commit failed"):
        crud.delete_user(user_id=1, session=session)

    db_manager_mock.commit_or_raise.assert_called_once_with(
        session, operation=ErrorLogOperation.DELETE_USER
    )
    assert not hasattr(crud, "ErrorLogRecorder")


def test_delete_user_not_found_returns_false_without_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    lookup_mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_user_by_id", lookup_mock)

    deleted = crud.delete_user(user_id=1, session=session)

    assert deleted is False
    lookup_mock.assert_called_once_with(1, session)
    assert not hasattr(crud, "ErrorLogRecorder")
    session.delete.assert_not_called()
    session.commit.assert_not_called()


def test_update_user_not_found_returns_none_without_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    lookup_mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_user_by_id", lookup_mock)

    updated = crud.update_user(make_user_model(), session)

    assert updated is None
    lookup_mock.assert_called_once_with(1, session)
    assert not hasattr(crud, "ErrorLogRecorder")
    session.commit.assert_not_called()
