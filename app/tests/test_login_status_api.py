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

from app.api.login_status import (
    create_login_status as create_login_status_routes,
)
from app.api.login_status import (
    delete_login_status as delete_login_status_routes,
)
from app.api.login_status import (
    get_login_status as get_login_status_routes,
)
from app.api.login_status import (
    update_login_status as update_login_status_routes,
)
from app.db.db_conn import db_manager
from app.db.db_models.login_status import LoginStatus
from app.db.db_models.user import User
from app.main import app
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


def make_login_status(
    user_id: int = 7,
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


def login_status_payload(user_id: int = 7) -> dict[str, object]:
    return {
        "user_id": user_id,
        "failed_login_attempts": 0,
        "last_failed_login_attempt_at": None,
        "locked": False,
        "locked_at": None,
    }


def updated_login_status_payload(user_id: int = 7) -> dict[str, object]:
    return {
        "user_id": user_id,
        "failed_login_attempts": 2,
        "last_failed_login_attempt_at": "2026-05-28T12:01:00",
        "locked": False,
        "locked_at": None,
    }


def login_status_response(user_id: int = 7) -> dict[str, object]:
    return {
        "user_id": user_id,
        "failed_login_attempts": 0,
        "last_failed_login_attempt_at": None,
        "locked": False,
        "locked_at": None,
    }


def test_create_login_status_returns_created_status_for_admin(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    created_status = make_login_status(user_id=7)
    create_mock = Mock(return_value=created_status)
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        create_login_status_routes,
        "create_login_status",
        create_mock,
    )

    response = client.post(
        "/api/login_status/create_login_status/",
        headers=auth_header(1),
        json=login_status_payload(user_id=7),
    )

    assert response.status_code == 200
    assert response.json() == login_status_response(user_id=7)
    create_mock.assert_called_once()
    login_status_model = create_mock.call_args.args[0]
    assert login_status_model.user_id == 7
    assert create_mock.call_args.args[1] is session


def test_create_login_status_returns_404_when_user_is_missing(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    create_mock = Mock(side_effect=ValueError("User not found."))
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        create_login_status_routes,
        "create_login_status",
        create_mock,
    )

    response = client.post(
        "/api/login_status/create_login_status/",
        headers=auth_header(1),
        json=login_status_payload(user_id=7),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_create_login_status_returns_409_when_row_already_exists(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    create_mock = Mock(side_effect=ValueError("Login status already exists."))
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        create_login_status_routes,
        "create_login_status",
        create_mock,
    )

    response = client.post(
        "/api/login_status/create_login_status/",
        headers=auth_header(1),
        json=login_status_payload(user_id=7),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Login status already exists."


def test_get_login_status_returns_status_for_admin(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    login_status = make_login_status(user_id=7)
    get_mock = Mock(return_value=login_status)
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        get_login_status_routes,
        "get_login_status_by_user_id",
        get_mock,
    )

    response = client.get(
        "/api/login_status/login_status_by_user_id/7",
        headers=auth_header(1),
    )

    assert response.status_code == 200
    assert response.json() == login_status_response(user_id=7)
    get_mock.assert_called_once_with(7, session)


def test_get_login_status_returns_404_when_row_is_missing(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    get_mock = Mock(return_value=None)
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        get_login_status_routes,
        "get_login_status_by_user_id",
        get_mock,
    )

    response = client.get(
        "/api/login_status/login_status_by_user_id/7",
        headers=auth_header(1),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Login status not found."
    get_mock.assert_called_once_with(7, session)


def test_update_login_status_returns_updated_status_for_admin(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    failed_at = datetime(2026, 5, 28, 12, 1, 0)
    updated_status = make_login_status(
        user_id=7,
        failed_login_attempts=2,
        last_failed_login_attempt_at=failed_at,
    )
    update_mock = Mock(return_value=updated_status)
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        update_login_status_routes,
        "update_login_status",
        update_mock,
    )

    response = client.put(
        "/api/login_status/update_login_status/",
        headers=auth_header(1),
        json=updated_login_status_payload(user_id=7),
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 7,
        "failed_login_attempts": 2,
        "last_failed_login_attempt_at": "2026-05-28T12:01:00",
        "locked": False,
        "locked_at": None,
    }
    update_mock.assert_called_once()
    login_status_model = update_mock.call_args.args[0]
    assert login_status_model.user_id == 7
    assert login_status_model.failed_login_attempts == 2
    assert update_mock.call_args.args[1] is session


def test_update_login_status_returns_404_when_row_is_missing(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    update_mock = Mock(return_value=None)
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        update_login_status_routes,
        "update_login_status",
        update_mock,
    )

    response = client.put(
        "/api/login_status/update_login_status/",
        headers=auth_header(1),
        json=updated_login_status_payload(user_id=7),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Login status not found."
    assert update_mock.call_args.args[1] is session


@pytest.mark.parametrize("deleted", [True, False])
def test_delete_login_status_returns_delete_status_for_admin(
    deleted: bool,
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin_user = make_user(user_id=1)
    delete_mock = Mock(return_value=deleted)
    stub_current_user(monkeypatch, admin_user)
    monkeypatch.setattr(
        delete_login_status_routes,
        "delete_login_status_by_user_id",
        delete_mock,
    )

    response = client.delete(
        "/api/login_status/delete_login_status/7",
        headers=auth_header(1),
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": 7, "deleted": deleted}
    delete_mock.assert_called_once_with(7, session)


@pytest.mark.parametrize(
    ("method", "path", "json_payload"),
    [
        ("POST", "/api/login_status/create_login_status/", login_status_payload()),
        ("GET", "/api/login_status/login_status_by_user_id/7", None),
        (
            "PUT",
            "/api/login_status/update_login_status/",
            updated_login_status_payload(),
        ),
        ("DELETE", "/api/login_status/delete_login_status/7", None),
    ],
)
def test_login_status_routes_reject_non_admin_users(
    method: str,
    path: str,
    json_payload: dict[str, object] | None,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = make_user(
        user_id=1,
        username="regular_user",
        email="regular@example.com",
        role="user",
    )
    create_mock = Mock()
    get_mock = Mock()
    update_mock = Mock()
    delete_mock = Mock()
    stub_current_user(monkeypatch, current_user)
    monkeypatch.setattr(create_login_status_routes, "create_login_status", create_mock)
    monkeypatch.setattr(
        get_login_status_routes,
        "get_login_status_by_user_id",
        get_mock,
    )
    monkeypatch.setattr(update_login_status_routes, "update_login_status", update_mock)
    monkeypatch.setattr(
        delete_login_status_routes,
        "delete_login_status_by_user_id",
        delete_mock,
    )

    response = client.request(
        method,
        path,
        headers=auth_header(1),
        json=json_payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."
    create_mock.assert_not_called()
    get_mock.assert_not_called()
    update_mock.assert_not_called()
    delete_mock.assert_not_called()


@pytest.mark.parametrize(
    ("method", "path", "json_payload"),
    [
        ("POST", "/api/login_status/create_login_status/", login_status_payload()),
        ("GET", "/api/login_status/login_status_by_user_id/7", None),
        (
            "PUT",
            "/api/login_status/update_login_status/",
            updated_login_status_payload(),
        ),
        ("DELETE", "/api/login_status/delete_login_status/7", None),
    ],
)
def test_login_status_routes_require_authentication(
    method: str,
    path: str,
    json_payload: dict[str, object] | None,
    client: TestClient,
) -> None:
    response = client.request(method, path, json=json_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
