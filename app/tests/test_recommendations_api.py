import os
from datetime import datetime
from typing import Any, Generator
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

from app.api.books.external_api import BooksRequestError
from app.api.books.external_api.recommendations import (
    book_recommendations_by_author as author_routes,
)
from app.api.books.external_api.recommendations import (
    book_recommendations_by_bookshelf as bookshelf_routes,
)
from app.api.books.external_api.recommendations import (
    book_recommendations_by_genre as genre_routes,
)
from app.db.db_conn import db_manager
from app.db.db_models.book import Book
from app.db.db_models.bookcase import Bookcase
from app.db.db_models.genre import Genre
from app.db.db_models.user import User
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token

NOW = datetime(2026, 5, 1, 12, 0, 0)


class FakeGoogleBooksResponse:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    def json(self) -> dict[str, Any]:
        return self.payload


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


def make_user(user_id: int = 1) -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username="owner",
        email="owner@example.com",
        password_hash="hashed-password",
        role="user",
        created_at=NOW,
        last_login=None,
    )


def authenticate(monkeypatch: pytest.MonkeyPatch, user_id: int = 1) -> None:
    current_user = make_user(user_id=user_id)
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == current_user.id else None,
    )


def auth_header(user_id: int = 1) -> dict[str, str]:
    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


def google_item(google_books_id: str, title: str = "Recommended Book") -> dict:
    return {
        "id": google_books_id,
        "volumeInfo": {
            "title": title,
            "authors": ["Test Author"],
            "categories": ["Fantasy"],
        },
        "saleInfo": None,
        "accessInfo": {},
    }


def make_book(
    book_id: int, google_books_id: str, title: str, genre_names: list[str]
) -> Book:
    book = Book(
        book_id=book_id,
        google_books_id=google_books_id,
        title=title,
    )
    book.genres = [
        Genre(id=index + 1, name=genre_name)
        for index, genre_name in enumerate(genre_names)
    ]
    return book


def make_bookcase(bookcase_id: int, user_id: int, books: list[Book]) -> Bookcase:
    bookcase = Bookcase(
        id=bookcase_id,
        name=f"Bookcase {bookcase_id}",
        created_at=NOW,
        user_id=user_id,
    )
    bookcase.books = books
    return bookcase


def mock_google_books(
    route_module,
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, Any],
    captured_params: list[dict[str, Any]],
) -> None:
    mock_google_books_pages(route_module, monkeypatch, [payload], captured_params)


def mock_google_books_pages(
    route_module,
    monkeypatch: pytest.MonkeyPatch,
    payloads: list[dict[str, Any]],
    captured_params: list[dict[str, Any]],
) -> None:
    payload_iter = iter(payloads)

    async def fake_book_api_request(client, params, logger):
        captured_params.append(params)
        return FakeGoogleBooksResponse(next(payload_iter, {"items": []}))

    monkeypatch.setattr(route_module, "book_api_request", fake_book_api_request)


@pytest.mark.parametrize(
    ("path", "params"),
    [
        (
            "/api/books/recommendations/by_author/",
            {"author": "Octavia Butler"},
        ),
        (
            "/api/books/recommendations/by_genre/",
            {"genre_name": "Science Fiction"},
        ),
        ("/api/books/recommendations/by_bookshelf_genre/", {}),
    ],
)
def test_recommendation_routes_require_authentication(
    client: TestClient, path: str, params: dict
) -> None:
    response = client.get(path, params=params)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_author_recommendations_build_author_query(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    mock_google_books(
        author_routes,
        monkeypatch,
        {"items": [google_item("author-result")]},
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_author/",
        headers=auth_header(),
        params={"author": "Octavia Butler", "max_results": 3, "start_index": 2},
    )

    assert response.status_code == 200
    assert captured_params[0]["q"] == "author:Octavia Butler"
    assert captured_params[0]["maxResults"] == 3
    assert captured_params[0]["startIndex"] == 2
    assert response.json()[0]["id"] == "author-result"


def test_direct_genre_recommendations_build_subject_query(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    mock_google_books(
        genre_routes,
        monkeypatch,
        {"items": [google_item("genre-result")]},
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_genre/",
        headers=auth_header(),
        params={"genre_name": "Fantasy"},
    )

    assert response.status_code == 200
    assert captured_params[0]["q"] == "subject:Fantasy"
    assert response.json()[0]["id"] == "genre-result"


def test_bookshelf_recommendations_use_most_frequent_genre(
    client: TestClient,
    session: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    bookcases = [
        make_bookcase(
            bookcase_id=1,
            user_id=1,
            books=[
                make_book(1, "owned-1", "A", ["Fantasy"]),
                make_book(2, "owned-2", "B", ["Fantasy", "Mystery"]),
            ],
        )
    ]
    monkeypatch.setattr(
        bookshelf_routes,
        "get_bookcases_with_books_and_genres_by_user_id",
        lambda user_id, session: bookcases,
    )
    mock_google_books(
        bookshelf_routes,
        monkeypatch,
        {"items": [google_item("new-book")]},
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_bookshelf_genre/",
        headers=auth_header(),
    )

    assert response.status_code == 200
    assert captured_params[0]["q"] == "subject:Fantasy"
    assert response.json()[0]["id"] == "new-book"
    assert session is not None


def test_bookshelf_recommendations_break_ties_alphabetically(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    bookcases = [
        make_bookcase(
            bookcase_id=1,
            user_id=1,
            books=[
                make_book(1, "owned-1", "A", ["Mystery"]),
                make_book(2, "owned-2", "B", ["Adventure"]),
            ],
        )
    ]
    monkeypatch.setattr(
        bookshelf_routes,
        "get_bookcases_with_books_and_genres_by_user_id",
        lambda user_id, session: bookcases,
    )
    mock_google_books(
        bookshelf_routes,
        monkeypatch,
        {"items": [google_item("tie-result")]},
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_bookshelf_genre/",
        headers=auth_header(),
    )

    assert response.status_code == 200
    assert captured_params[0]["q"] == "subject:Adventure"


def test_bookshelf_recommendations_fall_back_to_bestsellers_without_genres(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    monkeypatch.setattr(
        bookshelf_routes,
        "get_bookcases_with_books_and_genres_by_user_id",
        lambda user_id, session: [],
    )
    mock_google_books(
        bookshelf_routes,
        monkeypatch,
        {"items": [google_item("fallback-result")]},
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_bookshelf_genre/",
        headers=auth_header(),
    )

    assert response.status_code == 200
    assert captured_params[0]["q"] == "bestsellers"
    assert response.json()[0]["id"] == "fallback-result"


def test_bookshelf_recommendations_exclude_owned_books_and_deduplicate_results(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    bookcases = [
        make_bookcase(
            bookcase_id=1,
            user_id=1,
            books=[make_book(1, "owned-1", "Owned", ["Fantasy"])],
        )
    ]
    monkeypatch.setattr(
        bookshelf_routes,
        "get_bookcases_with_books_and_genres_by_user_id",
        lambda user_id, session: bookcases,
    )
    mock_google_books(
        bookshelf_routes,
        monkeypatch,
        {
            "items": [
                google_item("owned-1", "Already Owned"),
                google_item("new-1", "New One"),
                google_item("new-1", "New One Duplicate"),
                google_item("new-2", "New Two"),
            ]
        },
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_bookshelf_genre/",
        headers=auth_header(),
    )

    assert response.status_code == 200
    assert [book["id"] for book in response.json()] == ["new-1", "new-2"]


def test_author_recommendations_fetch_next_page_to_fill_max_results(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    mock_google_books_pages(
        author_routes,
        monkeypatch,
        [
            {"items": [google_item("duplicate"), google_item("duplicate")]},
            {"items": [google_item("second"), google_item("third")]},
        ],
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_author/",
        headers=auth_header(),
        params={"author": "Octavia Butler", "max_results": 3},
    )

    assert response.status_code == 200
    assert [book["id"] for book in response.json()] == ["duplicate", "second", "third"]
    assert [params["startIndex"] for params in captured_params] == [0, 2]


def test_genre_recommendations_fetch_next_page_to_fill_max_results(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    mock_google_books_pages(
        genre_routes,
        monkeypatch,
        [
            {"items": [google_item("duplicate"), google_item("duplicate")]},
            {"items": [google_item("second"), google_item("third")]},
        ],
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_genre/",
        headers=auth_header(),
        params={"genre_name": "Fantasy", "max_results": 3},
    )

    assert response.status_code == 200
    assert [book["id"] for book in response.json()] == ["duplicate", "second", "third"]
    assert [params["startIndex"] for params in captured_params] == [0, 2]


def test_bookshelf_recommendations_fetch_next_page_to_fill_max_results(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    bookcases = [
        make_bookcase(
            bookcase_id=1,
            user_id=1,
            books=[make_book(1, "owned-1", "Owned", ["Fantasy"])],
        )
    ]
    monkeypatch.setattr(
        bookshelf_routes,
        "get_bookcases_with_books_and_genres_by_user_id",
        lambda user_id, session: bookcases,
    )
    mock_google_books_pages(
        bookshelf_routes,
        monkeypatch,
        [
            {"items": [google_item("owned-1"), google_item("first")]},
            {"items": [google_item("second"), google_item("third")]},
        ],
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_bookshelf_genre/",
        headers=auth_header(),
        params={"max_results": 3},
    )

    assert response.status_code == 200
    assert [book["id"] for book in response.json()] == ["first", "second", "third"]
    assert [params["startIndex"] for params in captured_params] == [0, 2]


def test_upstream_google_books_error_returns_sanitized_json(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)

    async def fake_book_api_request(client, params, logger):
        raise BooksRequestError(
            status_code=503,
            error={"error": "Google Books unavailable"},
        )

    monkeypatch.setattr(author_routes, "book_api_request", fake_book_api_request)

    response = client.get(
        "/api/books/recommendations/by_author/",
        headers=auth_header(),
        params={"author": "Octavia Butler"},
    )

    assert response.status_code == 503
    assert response.json() == {"error": "Google Books unavailable"}


def test_invalid_google_books_payload_returns_validation_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    captured_params: list[dict[str, Any]] = []
    mock_google_books(
        genre_routes,
        monkeypatch,
        {"items": [{"id": "invalid", "volumeInfo": {}}]},
        captured_params,
    )

    response = client.get(
        "/api/books/recommendations/by_genre/",
        headers=auth_header(),
        params={"genre_name": "Fantasy"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "Validation error"


def test_blank_direct_recommendation_query_is_rejected(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)

    response = client.get(
        "/api/books/recommendations/by_author/",
        headers=auth_header(),
        params={"author": "   "},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "author must not be blank."
