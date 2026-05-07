import os
from datetime import datetime
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

from app.api.author import create_author as create_author_routes
from app.api.author import delete_author as delete_author_routes
from app.api.author import get_author as get_author_routes
from app.api.author import update_author as update_author_routes
from app.db.db_conn import db_manager
from app.db.db_models.author import Author
from app.db.db_models.user import User
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token


def make_user(user_id: int = 1) -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username="author-user",
        email="author-user@example.com",
        password_hash="hashed-password",
        role="user",
        created_at=datetime.now(),
        last_login=None,
    )


def make_author(
    author_id: int = 1,
    name: str = "Octavia Butler",
    bio: str | None = "Science fiction author.",
) -> Author:
    author = Author(id=author_id, name=name, bio=bio)
    author.books = []
    return author


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


def authenticate(monkeypatch: pytest.MonkeyPatch, user_id: int = 1) -> None:
    current_user = make_user(user_id=user_id)
    expected_user_id = user_id
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == expected_user_id else None,
    )


def test_create_author_returns_created_author(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    test_session = session

    def fake_create_author(author_model, session):
        assert author_model.name == "Octavia Butler"
        assert author_model.bio == "Science fiction author."
        assert session is test_session
        return make_author(name=author_model.name, bio=author_model.bio)

    monkeypatch.setattr(create_author_routes, "create_author", fake_create_author)

    response = client.post(
        "/api/author/create_author/",
        headers=auth_header(1),
        json={"name": "Octavia Butler", "bio": "Science fiction author."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "bio": "Science fiction author.",
        "name": "Octavia Butler",
        "books": [],
    }


def test_get_author_by_name_returns_author(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    test_session = session

    def fake_get_author_by_name(name: str, session: MagicMock):
        assert name == "Octavia Butler"
        assert session is test_session
        return make_author(name=name)

    monkeypatch.setattr(
        get_author_routes,
        "get_author_by_name",
        fake_get_author_by_name,
    )

    response = client.get(
        "/api/author/get_author_by_name/",
        headers=auth_header(1),
        params={"name": "Octavia Butler"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Octavia Butler"


def test_get_author_by_id_returns_author(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    test_session = session

    def fake_get_author_by_id(author_id: int, session: MagicMock):
        assert author_id == 7
        assert session is test_session
        return make_author(author_id=author_id, name="N. K. Jemisin")

    monkeypatch.setattr(get_author_routes, "get_author_by_id", fake_get_author_by_id)

    response = client.get(
        "/api/author/get_author_by_id/7",
        headers=auth_header(1),
    )

    assert response.status_code == 200
    assert response.json()["id"] == 7
    assert response.json()["name"] == "N. K. Jemisin"


def test_get_author_by_id_returns_404_when_missing(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    monkeypatch.setattr(get_author_routes, "get_author_by_id", lambda **_: None)

    response = client.get(
        "/api/author/get_author_by_id/404",
        headers=auth_header(1),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found."


def test_update_author_returns_updated_author(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    test_session = session

    def fake_update_author(author_replacement, session):
        assert author_replacement.id == 3
        assert author_replacement.name == "Ursula K. Le Guin"
        assert session is test_session
        return make_author(
            author_id=author_replacement.id,
            name=author_replacement.name,
            bio=author_replacement.bio,
        )

    monkeypatch.setattr(update_author_routes, "update_author", fake_update_author)

    response = client.put(
        "/api/author/update_author/",
        headers=auth_header(1),
        json={
            "id": 3,
            "name": "Ursula K. Le Guin",
            "bio": "Updated bio.",
            "books": [],
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == 3
    assert response.json()["name"] == "Ursula K. Le Guin"


def test_update_author_without_id_returns_422(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)

    response = client.put(
        "/api/author/update_author/",
        headers=auth_header(1),
        json={"name": "Missing ID", "books": []},
    )

    assert response.status_code == 422
    assert "Cannot replace author without an ID." in response.json()["detail"]


def test_update_author_returns_404_when_missing(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    monkeypatch.setattr(update_author_routes, "update_author", lambda **_: None)

    response = client.put(
        "/api/author/update_author/",
        headers=auth_header(1),
        json={"id": 5, "name": "Missing Author", "books": []},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found."


@pytest.mark.parametrize("deleted", [True, False])
def test_delete_author_by_id_returns_delete_result(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    deleted: bool,
) -> None:
    authenticate(monkeypatch)
    test_session = session

    def fake_delete_author_by_id(author_id: int, session: MagicMock):
        assert author_id == 9
        assert session is test_session
        return deleted

    monkeypatch.setattr(
        delete_author_routes,
        "delete_author_by_id",
        fake_delete_author_by_id,
    )

    response = client.delete(
        "/api/author/delete_author_by_id/9",
        headers=auth_header(1),
    )

    assert response.status_code == 200
    assert response.json() == {"author_id": 9, "deleted": deleted}


def test_author_routes_require_authentication(client: TestClient) -> None:
    response = client.get("/api/author/get_author_by_id/1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
