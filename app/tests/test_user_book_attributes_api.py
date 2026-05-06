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

from app.api.user_book_attributes import get_user_book_attribute as attribute_routes
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.db.db_models.user_book_attributes import UserBookAttributes
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token


CREATED_AT = datetime(2026, 5, 1, 12, 0, 0)
UPDATED_AT = datetime(2026, 5, 2, 12, 0, 0)


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


def make_attribute(
    attribute_id: int,
    user_id: int,
    book_id: int = 10,
    rating: int = 8,
    review_text: str = "Good read.",
) -> UserBookAttributes:
    return UserBookAttributes(
        id=attribute_id,
        user_id=user_id,
        book_id=book_id,
        rating=rating,
        review_text=review_text,
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
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


def test_book_attribute_by_book_id_returns_all_reviews_for_authenticated_user(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = make_user(user_id=1)
    book_id = 10
    user_book_lookup = MagicMock()
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        attribute_routes,
        "get_user_book_attribute_by_user_and_book_id",
        user_book_lookup,
    )

    def fake_get_by_book_id(requested_book_id: int, request_session: MagicMock):
        assert requested_book_id == book_id
        assert request_session is session
        return [
            make_attribute(attribute_id=1, user_id=1, book_id=book_id),
            make_attribute(
                attribute_id=2,
                user_id=2,
                book_id=book_id,
                rating=9,
                review_text="Loved it.",
            ),
        ]

    monkeypatch.setattr(
        attribute_routes,
        "get_user_book_attribute_by_book_id",
        fake_get_by_book_id,
    )

    response = client.get(
        "/api/user_book_attributes/book_attribute_by_book_id/",
        headers=auth_header(1),
        params={"book_id": book_id},
    )

    assert response.status_code == 200
    assert [attribute["user_id"] for attribute in response.json()] == [1, 2]
    user_book_lookup.assert_not_called()


def test_book_attribute_by_book_id_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/user_book_attributes/book_attribute_by_book_id/",
        params={"book_id": 10},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_book_attribute_by_book_and_user_id_returns_authorized_user_reviews(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = make_user(user_id=1)
    book_id = 10
    book_lookup = MagicMock()
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        attribute_routes,
        "get_user_book_attribute_by_book_id",
        book_lookup,
    )

    def fake_get_by_user_and_book_id(
        requested_user_id: int,
        requested_book_id: int,
        request_session: MagicMock,
    ):
        assert requested_user_id == 1
        assert requested_book_id == book_id
        assert request_session is session
        return [make_attribute(attribute_id=1, user_id=1, book_id=book_id)]

    monkeypatch.setattr(
        attribute_routes,
        "get_user_book_attribute_by_user_and_book_id",
        fake_get_by_user_and_book_id,
    )

    response = client.get(
        "/api/user_book_attributes/book_attribute_by_book_and_user_id/",
        headers=auth_header(1),
        params={"book_id": book_id, "user_id": 1},
    )

    assert response.status_code == 200
    assert response.json()[0]["user_id"] == 1
    assert response.json()[0]["book_id"] == book_id
    book_lookup.assert_not_called()


def test_book_attribute_by_book_and_user_id_rejects_other_user(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = make_user(user_id=1)
    user_book_lookup = MagicMock()
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(
        attribute_routes,
        "get_user_book_attribute_by_user_and_book_id",
        user_book_lookup,
    )

    response = client.get(
        "/api/user_book_attributes/book_attribute_by_book_and_user_id/",
        headers=auth_header(1),
        params={"book_id": 10, "user_id": 2},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."
    user_book_lookup.assert_not_called()


def test_book_attribute_by_book_and_user_id_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/user_book_attributes/book_attribute_by_book_and_user_id/",
        params={"book_id": 10, "user_id": 1},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
