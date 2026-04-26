import os
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("GOOGLE_BOOKS_API_URL", "https://example.com/books")
os.environ.setdefault("GOOGLE_BOOKS_API_KEY", "test-key")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.api.users import authenticate_user as authenticate_user_routes
from app.api.users import create_user as create_user_routes
from app.api.users import get_user as get_user_routes
from app.api.users import update_password as update_password_routes
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token


def make_user(
    *,
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
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticated_user = make_user()
    monkeypatch.setattr(
        authenticate_user_routes.PasswordHandler,
        "get_authenticated_user",
        lambda self, session: authenticated_user,
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


def test_token_endpoint_rejects_invalid_credentials(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        authenticate_user_routes.PasswordHandler,
        "get_authenticated_user",
        lambda self, session: None,
    )

    response = client.post(
        "/api/authenticate/token/",
        json={"username": "owner", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."


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
