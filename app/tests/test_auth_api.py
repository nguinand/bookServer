import os
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock, Mock

import pytest
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

from app.api.users import authenticate_user as authenticate_user_routes
from app.api.users import create_user as create_user_routes
from app.api.users import get_user as get_user_routes
from app.api.users import update_password as update_password_routes
from app.api.users import update_user as update_user_routes
from app.db.db_conn import db_manager
from app.db.db_models.login_status import LoginStatus
from app.db.db_models.user import User
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token


AUTH_ENDPOINT_PATHS = (
    "/api/authenticate/authenticate_user/",
    "/api/authenticate/token/",
)


def make_user(
    user_id: int = 1,
    username: str = "owner",
    email: str = "owner@example.com",
    role: str = "user",
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


def make_login_status(user_id: int = 1, locked: bool = False) -> LoginStatus:
    locked_at = datetime.now() if locked else None
    return LoginStatus(
        user_id=user_id,
        failed_login_attempts=4 if locked else 1,
        last_failed_login_attempt_at=datetime.now(),
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


def stub_auth_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    user: User | None,
    password_matches: bool = True,
    login_status: LoginStatus | None = None,
) -> tuple[Mock, Mock, Mock, Mock, Mock]:
    get_user_mock = Mock(return_value=user)
    verify_password_mock = Mock(return_value=password_matches)
    get_status_mock = Mock(return_value=login_status)
    record_failed_attempt_mock = Mock(return_value=login_status)
    reset_login_status_mock = Mock(return_value=login_status)

    monkeypatch.setattr(
        authenticate_user_routes.PasswordHandler,
        "get_user",
        lambda self, session: get_user_mock(session),
    )
    monkeypatch.setattr(
        authenticate_user_routes.PasswordHandler,
        "verify_password_for_user",
        lambda self, user: verify_password_mock(user),
    )
    monkeypatch.setattr(
        authenticate_user_routes,
        "get_login_status_by_user_id",
        get_status_mock,
    )
    monkeypatch.setattr(
        authenticate_user_routes,
        "record_failed_login_attempt",
        record_failed_attempt_mock,
    )
    monkeypatch.setattr(
        authenticate_user_routes,
        "reset_login_status_after_successful_login",
        reset_login_status_mock,
    )

    return (
        get_user_mock,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    )


def test_create_user_is_public(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    created_user = make_user(user_id=5, username="new_user", email="new@example.com")
    monkeypatch.setattr(
        create_user_routes,
        "create_user",
        lambda user_model, password, session: created_user,
    )

    response = client.post(
        "/api/database/create_user/",
        json={
            "user_model": {
                "first_name": "New",
                "last_name": "User",
                "username": "new_user",
                "email": "new@example.com",
                "role": "user",
            },
            "password": "password1",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "new_user"


def test_token_endpoint_returns_bearer_token(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    authenticated_user = make_user()
    (
        _,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    ) = stub_auth_dependencies(
        monkeypatch,
        user=authenticated_user,
        password_matches=True,
        login_status=None,
    )

    response = client.post(
        "/api/authenticate/token/",
        json={"username": "owner", "password": "password1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]
    verify_password_mock.assert_called_once_with(authenticated_user)
    get_status_mock.assert_called_once_with(1, session)
    record_failed_attempt_mock.assert_not_called()
    reset_login_status_mock.assert_not_called()


def test_token_endpoint_rejects_invalid_credentials(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    authenticated_user = make_user()
    (
        _,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    ) = stub_auth_dependencies(
        monkeypatch,
        user=authenticated_user,
        password_matches=False,
        login_status=None,
    )

    response = client.post(
        "/api/authenticate/token/",
        json={"username": "owner", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."
    verify_password_mock.assert_called_once_with(authenticated_user)
    get_status_mock.assert_called_once_with(1, session)
    record_failed_attempt_mock.assert_called_once_with(1, session)
    reset_login_status_mock.assert_not_called()


def test_authenticate_user_endpoint_returns_authentication_status(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticated_user = make_user()
    stub_auth_dependencies(
        monkeypatch,
        user=authenticated_user,
        password_matches=True,
        login_status=None,
    )

    response = client.post(
        "/api/authenticate/authenticate_user/",
        json={"username": "owner", "password": "password1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "username": "owner",
        "authenticated": True,
        "details": "User authenticated.",
    }


@pytest.mark.parametrize("path", AUTH_ENDPOINT_PATHS)
def test_authentication_endpoints_reject_unknown_username_without_lockout_write(
    path: str,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        _,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    ) = stub_auth_dependencies(monkeypatch, user=None)

    response = client.post(
        path,
        json={"username": "missing", "password": "password1"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."
    verify_password_mock.assert_not_called()
    get_status_mock.assert_not_called()
    record_failed_attempt_mock.assert_not_called()
    reset_login_status_mock.assert_not_called()


@pytest.mark.parametrize("path", AUTH_ENDPOINT_PATHS)
def test_authentication_endpoints_return_401_when_failed_attempt_locks_account(
    path: str,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    session: MagicMock,
) -> None:
    authenticated_user = make_user()
    locked_status = make_login_status(locked=True)
    (
        _,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    ) = stub_auth_dependencies(
        monkeypatch,
        user=authenticated_user,
        password_matches=False,
        login_status=None,
    )
    record_failed_attempt_mock.return_value = locked_status

    response = client.post(
        path,
        json={"username": "owner", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."
    verify_password_mock.assert_called_once_with(authenticated_user)
    get_status_mock.assert_called_once_with(1, session)
    record_failed_attempt_mock.assert_called_once_with(1, session)
    reset_login_status_mock.assert_not_called()


@pytest.mark.parametrize("path", AUTH_ENDPOINT_PATHS)
def test_authentication_endpoints_return_423_for_locked_account_without_password_check(
    path: str,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    session: MagicMock,
) -> None:
    authenticated_user = make_user()
    locked_status = make_login_status(locked=True)
    (
        _,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    ) = stub_auth_dependencies(
        monkeypatch,
        user=authenticated_user,
        password_matches=True,
        login_status=locked_status,
    )

    response = client.post(
        path,
        json={"username": "owner", "password": "password1"},
    )

    assert response.status_code == 423
    assert response.json()["detail"] == "Account is locked. Contact an admin."
    verify_password_mock.assert_not_called()
    get_status_mock.assert_called_once_with(1, session)
    record_failed_attempt_mock.assert_not_called()
    reset_login_status_mock.assert_not_called()


@pytest.mark.parametrize("path", AUTH_ENDPOINT_PATHS)
def test_authentication_endpoints_reset_existing_login_status_after_success(
    path: str,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    session: MagicMock,
) -> None:
    authenticated_user = make_user()
    login_status = make_login_status(locked=False)
    (
        _,
        verify_password_mock,
        get_status_mock,
        record_failed_attempt_mock,
        reset_login_status_mock,
    ) = stub_auth_dependencies(
        monkeypatch,
        user=authenticated_user,
        password_matches=True,
        login_status=login_status,
    )

    response = client.post(
        path,
        json={"username": "owner", "password": "password1"},
    )

    assert response.status_code == 200
    verify_password_mock.assert_called_once_with(authenticated_user)
    get_status_mock.assert_called_once_with(1, session)
    record_failed_attempt_mock.assert_not_called()
    reset_login_status_mock.assert_called_once_with(1, session)


def test_books_routes_require_authentication(client: TestClient) -> None:
    response = client.get("/api/books/name/", params={"book_name": "Dune"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_expired_token_is_rejected(client: TestClient) -> None:
    expired_token = create_access_token(subject=1, expires_delta=timedelta(seconds=-1))

    response = client.get(
        "/api/database/user_by_id/1",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."


def test_valid_token_for_locked_user_is_rejected(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, session: MagicMock
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    locked_status = make_login_status(user_id=1, locked=True)
    get_status_mock = Mock(return_value=locked_status)
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        api_token_module,
        "get_login_status_by_user_id",
        get_status_mock,
    )

    response = client.get("/api/database/user_by_id/1", headers=auth_header(1))

    assert response.status_code == 423
    assert response.json()["detail"] == "Account is locked. Contact an admin."
    get_status_mock.assert_called_once_with(1, session)


def test_user_route_allows_owner_access(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        get_user_routes,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )

    response = client.get("/api/database/user_by_id/1", headers=auth_header(1))

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "owner"


def test_user_route_rejects_non_owner_access(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )

    response = client.get("/api/database/user_by_id/2", headers=auth_header(1))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."


def test_admin_route_allows_cross_user_access(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    admin_user = make_user(
        user_id=1,
        username="admin_user",
        email="admin@example.com",
        role="admin",
    )
    target_user = make_user(
        user_id=2,
        username="target_user",
        email="target@example.com",
    )
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: admin_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        get_user_routes,
        "get_user_by_id",
        lambda user_id, session: target_user if user_id == 2 else None,
    )

    response = client.get("/api/database/user_by_id/2", headers=auth_header(1))

    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["username"] == "target_user"


def test_admin_can_delete_other_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    admin_user = make_user(
        user_id=1,
        username="admin_user",
        email="admin@example.com",
        role="admin",
    )
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: admin_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        "app.api.users.delete_user.delete_user",
        lambda user_id, session: True,
    )

    response = client.delete("/api/database/delete_user/2", headers=auth_header(1))

    assert response.status_code == 200
    assert response.json() == {"user_id": 2, "deleted": True}


def test_update_user_allows_owner_update(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    updated_user = make_user(
        user_id=1,
        username="updated_owner",
        email="updated@example.com",
    )
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        update_user_routes,
        "update_user",
        lambda user_replacement, session: updated_user,
    )

    response = client.put(
        "/api/database/update_user/",
        headers=auth_header(1),
        json={
            "user_model": {
                "id": 1,
                "first_name": "Updated",
                "last_name": "Owner",
                "username": "updated_owner",
                "email": "updated@example.com",
                "role": "user",
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "updated_owner"
    assert response.json()["email"] == "updated@example.com"


def test_update_user_returns_404_when_user_is_missing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        update_user_routes,
        "update_user",
        lambda user_replacement, session: None,
    )

    response = client.put(
        "/api/database/update_user/",
        headers=auth_header(1),
        json={
            "user_model": {
                "id": 1,
                "first_name": "Updated",
                "last_name": "Owner",
                "username": "updated_owner",
                "email": "updated@example.com",
                "role": "user",
            }
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_update_user_rejects_missing_user_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )

    response = client.put(
        "/api/database/update_user/",
        headers=auth_header(1),
        json={
            "user_model": {
                "first_name": "Updated",
                "last_name": "Owner",
                "username": "updated_owner",
                "email": "updated@example.com",
                "role": "user",
            }
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User ID is required."


def test_update_user_rejects_non_owner_update(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )

    response = client.put(
        "/api/database/update_user/",
        headers=auth_header(1),
        json={
            "user_model": {
                "id": 2,
                "first_name": "Target",
                "last_name": "User",
                "username": "target_user",
                "email": "target@example.com",
                "role": "user",
            }
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."


def test_update_password_succeeds_for_authenticated_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        update_password_routes.PasswordHandler,
        "verify_password",
        lambda self, session: True,
    )
    monkeypatch.setattr(
        update_password_routes.PasswordHandler,
        "update_password",
        lambda self, password_hash, user, session: True,
    )

    response = client.post(
        "/api/authenticate/update_user_password/",
        headers=auth_header(1),
        json={
            "current_password": "password1",
            "new_password": "newpassword1",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "updated": True,
        "details": "Password updated.",
    }


def test_update_password_rejects_invalid_current_password(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(user_id=1, username="owner", email="owner@example.com")
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        update_password_routes.PasswordHandler,
        "verify_password",
        lambda self, session: False,
    )

    response = client.post(
        "/api/authenticate/update_user_password/",
        headers=auth_header(1),
        json={
            "current_password": "wrongpass1",
            "new_password": "newpassword1",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."
