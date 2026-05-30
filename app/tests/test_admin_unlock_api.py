import os
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, Mock

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("GOOGLE_BOOKS_API_URL", "https://example.com/books")
os.environ.setdefault("GOOGLE_BOOKS_API_KEY", "test-key")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("FRONTEND_ENDPOINT", "localhost")
os.environ.setdefault("FRONTEND_PORT", "test")

import pytest

from app.api.admin import unlock_user_account as admin_unlock_routes
from app.db.db_conn import db_manager
from app.db.db_models.login_status import LoginStatus
from app.db.db_models.user import User
from app.main import app
from app.models.admin_log import AdminEventType
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token


def make_user(
    user_id: int = 1,
    username: str = "admin_user",
    email: str = "admin@example.com",
    role: str = "admin",
) -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username=username,
        email=email,
        password_hash="hashed-password",
        role=role,
        created_at=datetime.now(),
        last_login=None,
    )


def make_unlocked_login_status(user_id: int = 7) -> LoginStatus:
    return LoginStatus(
        user_id=user_id,
        failed_login_attempts=0,
        last_failed_login_attempt_at=None,
        locked=False,
        locked_at=None,
    )


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(session: MagicMock) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[MagicMock, None, None]:
        yield session

    app.dependency_overrides[db_manager.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_header(user_id: int) -> dict[str, str]:
    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


def stub_current_user(monkeypatch: pytest.MonkeyPatch, current_user: User) -> None:
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == current_user.id else None,
    )


def assert_unlock_admin_log(
    create_admin_logs_mock: Mock,
    session: MagicMock,
    admin_user_id: int,
    unlocked_user_id: int,
) -> None:
    create_admin_logs_mock.assert_called_once()
    admin_log_model = create_admin_logs_mock.call_args.args[0]
    assert create_admin_logs_mock.call_args.args[1] is session
    assert admin_log_model.event_type == AdminEventType.MODIFY
    assert admin_log_model.event_description == (
        f"Admin user {admin_user_id} unlocked account for user {unlocked_user_id}."
    )


def test_unlock_user_account_by_id_returns_login_status_and_writes_admin_log(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    unlocked_status = make_unlocked_login_status(user_id=7)
    unlock_mock = Mock(return_value=unlocked_status)
    create_admin_logs_mock = Mock()
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        admin_unlock_routes,
        "unlock_login_status_by_user_id",
        unlock_mock,
    )
    monkeypatch.setattr(
        admin_unlock_routes,
        "create_admin_logs",
        create_admin_logs_mock,
    )

    response = client.post(
        "/api/admin/unlock_user_account_by_id/",
        headers=auth_header(1),
        json={"user_id": 7},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 7,
        "failed_login_attempts": 0,
        "last_failed_login_attempt_at": None,
        "locked": False,
        "locked_at": None,
    }
    unlock_mock.assert_called_once_with(7, session)
    assert_unlock_admin_log(create_admin_logs_mock, session, 1, 7)


def test_unlock_user_account_by_username_returns_login_status_and_writes_admin_log(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    unlocked_status = make_unlocked_login_status(user_id=8)
    unlock_mock = Mock(return_value=unlocked_status)
    create_admin_logs_mock = Mock()
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        admin_unlock_routes,
        "unlock_login_status_by_username",
        unlock_mock,
    )
    monkeypatch.setattr(
        admin_unlock_routes,
        "create_admin_logs",
        create_admin_logs_mock,
    )

    response = client.post(
        "/api/admin/unlock_user_account_by_username/",
        headers=auth_header(1),
        json={"username": "locked_user"},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == 8
    assert response.json()["locked"] is False
    unlock_mock.assert_called_once_with("locked_user", session)
    assert_unlock_admin_log(create_admin_logs_mock, session, 1, 8)


def test_unlock_user_account_by_id_returns_404_when_login_status_is_missing(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    unlock_mock = Mock(return_value=None)
    create_admin_logs_mock = Mock()
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        admin_unlock_routes,
        "unlock_login_status_by_user_id",
        unlock_mock,
    )
    monkeypatch.setattr(
        admin_unlock_routes,
        "create_admin_logs",
        create_admin_logs_mock,
    )

    response = client.post(
        "/api/admin/unlock_user_account_by_id/",
        headers=auth_header(1),
        json={"user_id": 7},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Login status not found."
    unlock_mock.assert_called_once_with(7, session)
    create_admin_logs_mock.assert_not_called()


def test_unlock_user_account_by_username_returns_404_when_user_is_missing(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    unlock_mock = Mock(side_effect=ValueError("User not found."))
    create_admin_logs_mock = Mock()
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        admin_unlock_routes,
        "unlock_login_status_by_username",
        unlock_mock,
    )
    monkeypatch.setattr(
        admin_unlock_routes,
        "create_admin_logs",
        create_admin_logs_mock,
    )

    response = client.post(
        "/api/admin/unlock_user_account_by_username/",
        headers=auth_header(1),
        json={"username": "missing"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
    unlock_mock.assert_called_once_with("missing", session)
    create_admin_logs_mock.assert_not_called()


def test_unlock_user_account_by_username_returns_404_when_login_status_is_missing(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    unlock_mock = Mock(return_value=None)
    create_admin_logs_mock = Mock()
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        admin_unlock_routes,
        "unlock_login_status_by_username",
        unlock_mock,
    )
    monkeypatch.setattr(
        admin_unlock_routes,
        "create_admin_logs",
        create_admin_logs_mock,
    )

    response = client.post(
        "/api/admin/unlock_user_account_by_username/",
        headers=auth_header(1),
        json={"username": "unlocked_user"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Login status not found."
    unlock_mock.assert_called_once_with("unlocked_user", session)
    create_admin_logs_mock.assert_not_called()


def test_unlock_user_account_rejects_non_admin_user(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = make_user(
        user_id=1,
        username="regular_user",
        email="regular@example.com",
        role="user",
    )
    unlock_mock = Mock()
    stub_current_user(monkeypatch, current_user)
    monkeypatch.setattr(
        admin_unlock_routes,
        "unlock_login_status_by_user_id",
        unlock_mock,
    )

    response = client.post(
        "/api/admin/unlock_user_account_by_id/",
        headers=auth_header(1),
        json={"user_id": 7},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."
    unlock_mock.assert_not_called()


def test_unlock_user_account_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/admin/unlock_user_account_by_id/",
        json={"user_id": 7},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
