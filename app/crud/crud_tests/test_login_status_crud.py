import os
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock, Mock

import pytest
from pydantic import ValidationError

# Avoid import-time db_manager initialization errors in unit tests.
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")

from app.crud import login_status_crud as crud
from app.db.db_models.login_status import LoginStatus
from app.db.db_models.user import User
from app.models.login_status import LoginStatusModel


@pytest.fixture
def session() -> Generator[MagicMock, None, None]:
    yield MagicMock()


def make_user(user_id: int = 1, username: str = "owner") -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username=username,
        email=f"{username}@example.com",
        password_hash="hashed-password",
        role="user",
    )


def make_login_status(
    user_id: int = 1,
    failed_login_attempts: int = 0,
    last_failed_login_attempt_at: datetime | None = None,
    locked: bool = False,
    locked_at: datetime | None = None,
) -> LoginStatus:
    return LoginStatus(
        user_id=user_id,
        failed_login_attempts=failed_login_attempts,
        last_failed_login_attempt_at=last_failed_login_attempt_at,
        locked=locked,
        locked_at=locked_at,
    )


def test_login_status_model_rejects_failed_attempts_without_timestamp() -> None:
    with pytest.raises(ValidationError):
        LoginStatusModel(user_id=1, failed_login_attempts=1)


def test_login_status_model_rejects_timestamp_when_attempts_are_zero() -> None:
    with pytest.raises(ValidationError):
        LoginStatusModel(
            user_id=1,
            failed_login_attempts=0,
            last_failed_login_attempt_at=datetime(2026, 5, 28, 12, 0, 0),
        )


def test_login_status_model_uses_strict_bool_for_locked() -> None:
    with pytest.raises(ValidationError):
        LoginStatusModel.model_validate(
            {
                "user_id": 1,
                "failed_login_attempts": 1,
                "last_failed_login_attempt_at": datetime(2026, 5, 28, 12, 0, 0),
                "locked": "true",
            }
        )


def test_login_status_model_rejects_more_than_four_failed_attempts() -> None:
    with pytest.raises(ValidationError):
        LoginStatusModel(
            user_id=1,
            failed_login_attempts=5,
            last_failed_login_attempt_at=datetime(2026, 5, 28, 12, 0, 0),
        )


def test_create_login_status_adds_row_when_user_exists(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    model = LoginStatusModel(user_id=1)
    lookup_user_mock = Mock(return_value=make_user())
    lookup_status_mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_user_by_id", lookup_user_mock)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", lookup_status_mock)

    created = crud.create_login_status(model, session)

    lookup_user_mock.assert_called_once_with(1, session)
    lookup_status_mock.assert_called_once_with(1, session)
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(created)
    assert created.user_id == 1
    assert created.failed_login_attempts == 0
    assert created.last_failed_login_attempt_at is None
    assert created.locked is False
    assert created.locked_at is None


def test_create_login_status_raises_when_user_is_missing(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=None))

    with pytest.raises(ValueError, match="User not found."):
        crud.create_login_status(LoginStatusModel(user_id=1), session)

    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_create_login_status_raises_when_row_exists(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=make_login_status()),
    )

    with pytest.raises(ValueError, match="Login status already exists."):
        crud.create_login_status(LoginStatusModel(user_id=1), session)

    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_get_login_status_by_user_id_uses_session_get(session: MagicMock) -> None:
    record = make_login_status()
    session.get.return_value = record

    result = crud.get_login_status_by_user_id(1, session)

    session.get.assert_called_once_with(LoginStatus, 1)
    assert result is record


def test_update_login_status_replaces_fields_and_commits(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    existing = make_login_status(user_id=1)
    failed_at = datetime(2026, 5, 28, 12, 0, 0)
    locked_at = datetime(2026, 5, 28, 12, 3, 0)
    replacement = LoginStatusModel(
        user_id=1,
        failed_login_attempts=4,
        last_failed_login_attempt_at=failed_at,
        locked=True,
        locked_at=locked_at,
    )
    lookup_mock = Mock(return_value=existing)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", lookup_mock)

    updated = crud.update_login_status(replacement, session)

    lookup_mock.assert_called_once_with(1, session)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(existing)
    assert updated is existing
    assert existing.failed_login_attempts == 4
    assert existing.last_failed_login_attempt_at == failed_at
    assert existing.locked is True
    assert existing.locked_at == locked_at


def test_update_login_status_returns_none_when_missing(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    lookup_mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", lookup_mock)

    updated = crud.update_login_status(LoginStatusModel(user_id=1), session)

    lookup_mock.assert_called_once_with(1, session)
    session.commit.assert_not_called()
    assert updated is None


def test_delete_login_status_by_user_id_deletes_existing_row(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    existing = make_login_status()
    lookup_mock = Mock(return_value=existing)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", lookup_mock)

    deleted = crud.delete_login_status_by_user_id(1, session)

    lookup_mock.assert_called_once_with(1, session)
    session.delete.assert_called_once_with(existing)
    session.commit.assert_called_once()
    assert deleted is True


def test_delete_login_status_by_user_id_returns_false_when_missing(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    lookup_mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", lookup_mock)

    deleted = crud.delete_login_status_by_user_id(1, session)

    lookup_mock.assert_called_once_with(1, session)
    session.delete.assert_not_called()
    session.commit.assert_not_called()
    assert deleted is False


def test_unlock_login_status_by_user_id_resets_existing_row(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 0, 0)
    existing = make_login_status(
        failed_login_attempts=4,
        last_failed_login_attempt_at=failed_at,
        locked=True,
        locked_at=failed_at,
    )
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=existing),
    )

    unlocked = crud.unlock_login_status_by_user_id(1, session)

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(existing)
    assert unlocked is existing
    assert existing.failed_login_attempts == 0
    assert existing.last_failed_login_attempt_at is None
    assert existing.locked is False
    assert existing.locked_at is None


def test_unlock_login_status_by_user_id_returns_none_when_missing(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    lookup_mock = Mock(return_value=None)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", lookup_mock)

    unlocked = crud.unlock_login_status_by_user_id(1, session)

    lookup_mock.assert_called_once_with(1, session)
    session.commit.assert_not_called()
    session.refresh.assert_not_called()
    assert unlocked is None


def test_unlock_login_status_by_username_resets_existing_row(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 0, 0)
    user = make_user(user_id=7, username="locked_user")
    existing = make_login_status(
        user_id=7,
        failed_login_attempts=4,
        last_failed_login_attempt_at=failed_at,
        locked=True,
        locked_at=failed_at,
    )
    user_lookup_mock = Mock(return_value=user)
    status_lookup_mock = Mock(return_value=existing)
    monkeypatch.setattr(crud, "get_users_by_username", user_lookup_mock)
    monkeypatch.setattr(crud, "get_login_status_by_user_id", status_lookup_mock)

    unlocked = crud.unlock_login_status_by_username("locked_user", session)

    user_lookup_mock.assert_called_once_with("locked_user", session)
    status_lookup_mock.assert_called_once_with(7, session)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(existing)
    assert unlocked is existing
    assert existing.failed_login_attempts == 0
    assert existing.last_failed_login_attempt_at is None
    assert existing.locked is False
    assert existing.locked_at is None


def test_unlock_login_status_by_username_raises_when_user_is_missing(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    monkeypatch.setattr(crud, "get_users_by_username", Mock(return_value=None))

    with pytest.raises(ValueError, match="User not found."):
        crud.unlock_login_status_by_username("missing", session)

    session.commit.assert_not_called()


def test_reset_login_status_after_successful_login_does_not_create_missing_row(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=None),
    )

    reset = crud.reset_login_status_after_successful_login(1, session)

    session.add.assert_not_called()
    session.commit.assert_not_called()
    assert reset is None


def test_reset_login_status_after_successful_login_resets_existing_row(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 0, 0)
    existing = make_login_status(
        failed_login_attempts=2,
        last_failed_login_attempt_at=failed_at,
        locked=False,
    )
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=existing),
    )

    reset = crud.reset_login_status_after_successful_login(1, session)

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(existing)
    assert reset is existing
    assert existing.failed_login_attempts == 0
    assert existing.last_failed_login_attempt_at is None
    assert existing.locked is False
    assert existing.locked_at is None


def test_record_failed_login_attempt_returns_none_for_missing_user(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=None))

    result = crud.record_failed_login_attempt(1, session)

    session.add.assert_not_called()
    session.commit.assert_not_called()
    assert result is None


def test_record_failed_login_attempt_creates_first_attempt_for_existing_user(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 0, 0)
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=None),
    )

    login_status = crud.record_failed_login_attempt(1, session, failed_at)

    session.add.assert_called_once_with(login_status)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(login_status)
    assert login_status is not None
    assert login_status.failed_login_attempts == 1
    assert login_status.last_failed_login_attempt_at == failed_at
    assert login_status.locked is False
    assert login_status.locked_at is None


def test_record_failed_login_attempt_increments_inside_window(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 5, 0)
    existing = make_login_status(
        failed_login_attempts=2,
        last_failed_login_attempt_at=failed_at - timedelta(minutes=5),
    )
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=existing),
    )

    login_status = crud.record_failed_login_attempt(1, session, failed_at)

    session.commit.assert_called_once()
    assert login_status is existing
    assert existing.failed_login_attempts == 3
    assert existing.last_failed_login_attempt_at == failed_at
    assert existing.locked is False


def test_record_failed_login_attempt_resets_outside_window(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 11, 0)
    existing = make_login_status(
        failed_login_attempts=3,
        last_failed_login_attempt_at=failed_at - timedelta(minutes=11),
    )
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=existing),
    )

    login_status = crud.record_failed_login_attempt(1, session, failed_at)

    session.commit.assert_called_once()
    assert login_status is existing
    assert existing.failed_login_attempts == 1
    assert existing.last_failed_login_attempt_at == failed_at
    assert existing.locked is False
    assert existing.locked_at is None


def test_record_failed_login_attempt_locks_on_fourth_attempt_inside_window(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 3, 0)
    existing = make_login_status(
        failed_login_attempts=3,
        last_failed_login_attempt_at=failed_at - timedelta(minutes=3),
    )
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=existing),
    )

    login_status = crud.record_failed_login_attempt(1, session, failed_at)

    session.commit.assert_called_once()
    assert login_status is existing
    assert existing.failed_login_attempts == 4
    assert existing.last_failed_login_attempt_at == failed_at
    assert existing.locked is True
    assert existing.locked_at == failed_at


def test_record_failed_login_attempt_caps_attempts_at_four(
    monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    failed_at = datetime(2026, 5, 28, 12, 4, 0)
    existing = make_login_status(
        failed_login_attempts=4,
        last_failed_login_attempt_at=failed_at - timedelta(minutes=4),
        locked=False,
    )
    monkeypatch.setattr(crud, "get_user_by_id", Mock(return_value=make_user()))
    monkeypatch.setattr(
        crud,
        "get_login_status_by_user_id",
        Mock(return_value=existing),
    )

    login_status = crud.record_failed_login_attempt(1, session, failed_at)

    session.commit.assert_called_once()
    assert login_status is existing
    assert existing.failed_login_attempts == 4
    assert existing.last_failed_login_attempt_at == failed_at
    assert existing.locked is True
    assert existing.locked_at == failed_at
