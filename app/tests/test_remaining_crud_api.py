import os
from datetime import datetime
from decimal import Decimal
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

from app.api.admin_logs import create_admin_logs as admin_create_routes
from app.api.admin_logs import delete_admin_logs as admin_delete_routes
from app.api.admin_logs import get_admin_logs as admin_get_routes
from app.api.admin_logs import get_admin_logs_by_id as admin_get_by_id_routes
from app.api.admin_logs import update_admin_logs as admin_update_routes
from app.api.avatar import create_avatar as avatar_create_routes
from app.api.avatar import delete_avatar as avatar_delete_routes
from app.api.avatar import get_avatar as avatar_get_routes
from app.api.avatar import update_avatar as avatar_update_routes
from app.api.book_access import create_access_info as access_create_routes
from app.api.book_access import delete_access_info as access_delete_routes
from app.api.book_access import get_access_info as access_get_routes
from app.api.book_access import update_access_info as access_update_routes
from app.api.book_sale_info import create_book_sale_info as sale_create_routes
from app.api.book_sale_info import delete_book_sale_info as sale_delete_routes
from app.api.book_sale_info import get_book_sale_info as sale_get_routes
from app.api.book_sale_info import update_book_sale_info as sale_update_routes
from app.api.genre import create_genre as genre_create_routes
from app.api.genre import delete_genre as genre_delete_routes
from app.api.genre import get_genre as genre_get_routes
from app.api.genre import update_genre as genre_update_routes
from app.api.user_book_state import create_user_book_state as state_create_routes
from app.api.user_book_state import delete_user_book_state as state_delete_routes
from app.api.user_book_state import get_user_book_state as state_get_routes
from app.api.user_book_state import update_user_book_state as state_update_routes
from app.api.user_status import create_user_status as status_create_routes
from app.api.user_status import delete_user_status as status_delete_routes
from app.api.user_status import get_user_status as status_get_routes
from app.api.user_status import update_user_status as status_update_routes
from app.db.db_conn import db_manager
from app.db.db_models.admin_logs import AdminLogs
from app.db.db_models.avatar import Avatar
from app.db.db_models.book_access import BookAccess
from app.db.db_models.book_sale_info import BookSaleInfo
from app.db.db_models.genre import Genre
from app.db.db_models.user import User
from app.db.db_models.user_book_state import ReadingStatus, UserBookState
from app.db.db_models.user_status import UserStatus
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token

NOW = datetime(2026, 5, 1, 12, 0, 0)


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


def make_user(user_id: int = 1, role: str = "user") -> User:
    return User(
        id=user_id,
        first_name="Test",
        last_name="User",
        username=f"{role}-user",
        email=f"{role}@example.com",
        password_hash="hashed-password",
        role=role,
        created_at=NOW,
        last_login=None,
    )


def authenticate(
    monkeypatch: pytest.MonkeyPatch,
    user_id: int = 1,
    role: str = "user",
) -> None:
    current_user = make_user(user_id=user_id, role=role)
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == current_user.id else None,
    )


def auth_header(user_id: int = 1) -> dict[str, str]:
    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


def access_payload() -> dict:
    return {
        "country": "US",
        "viewability": "PARTIAL",
        "embeddable": True,
        "publicDomain": False,
        "epub": {"isAvailable": True, "acsTokenLink": "https://example.com/epub"},
        "pdf": {"isAvailable": False},
        "webReaderLink": "https://example.com/read",
    }


def sale_payload(book_sale_info_id: int | None = None) -> dict:
    payload = {
        "book_id": 12,
        "country": "US",
        "saleability": "FOR_SALE",
        "isEbook": True,
        "listPrice": {"amount": "12.99", "currencyCode": "USD"},
        "retailPrice": {"amount": "10.99", "currencyCode": "USD"},
        "buyLink": "https://example.com/buy",
    }
    if book_sale_info_id is not None:
        payload["id"] = book_sale_info_id
    return payload


def state_payload(user_book_state_id: int | None = None) -> dict:
    payload = {
        "user_id": 1,
        "book_id": 2,
        "reading_status": "reading",
        "current_page": 40,
        "percent_complete": 20,
    }
    if user_book_state_id is not None:
        payload["id"] = user_book_state_id
    return payload


def make_access(access_info_id: int = 1, book_id: int = 12) -> BookAccess:
    return BookAccess(
        id=access_info_id,
        book_id=book_id,
        country="US",
        viewability="PARTIAL",
        embeddable=True,
        public_domain=False,
        epub_available=True,
        epub_token_link="https://example.com/epub",
        pdf_available=False,
        pdf_token_link=None,
        web_reader_link="https://example.com/read",
    )


def make_sale(book_sale_info_id: int = 1) -> BookSaleInfo:
    return BookSaleInfo(
        id=book_sale_info_id,
        book_id=12,
        country="US",
        saleability="FOR_SALE",
        is_ebook=True,
        buy_link="https://example.com/buy",
        list_price=Decimal("12.99"),
        list_price_currency_code="USD",
        retail_price=Decimal("10.99"),
        retail_price_currency_code="USD",
    )


def make_state(user_book_state_id: int = 1) -> UserBookState:
    return UserBookState(
        id=user_book_state_id,
        user_id=1,
        book_id=2,
        reading_status=ReadingStatus.READING,
        current_page=40,
        percent_complete=20,
        started_at=None,
        finished_at=None,
    )


def make_admin_log(admin_log_id: int = 1) -> AdminLogs:
    return AdminLogs(
        id=admin_log_id,
        event_type="create",
        event_description="Created a record",
        created_at=NOW,
    )


@pytest.mark.parametrize(
    "path",
    [
        "/api/genre/get_genre_by_id/1",
        "/api/avatar/get_avatar_by_id/1",
        "/api/user_status/get_user_status_by_id/1",
        "/api/user_book_state/get_user_book_state_by_id/1",
        "/api/book_access/get_access_info_by_id/1",
        "/api/book_sale_info/get_book_sale_info_by_id/1",
        "/api/admin_logs/get_admin_logs_by_id/1",
    ],
)
def test_new_routes_require_authentication(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_genre_crud_endpoints(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    monkeypatch.setattr(
        genre_create_routes,
        "create_genre",
        lambda genre_model, session: Genre(id=1, name=genre_model.name),
    )
    monkeypatch.setattr(
        genre_get_routes,
        "get_genre_by_id",
        lambda genre_id, session: Genre(id=genre_id, name="Fantasy"),
    )
    monkeypatch.setattr(
        genre_get_routes,
        "get_genre_by_name",
        lambda name, session: Genre(id=2, name=name),
    )
    monkeypatch.setattr(
        genre_update_routes,
        "update_genre",
        lambda genre_replacement, session: Genre(
            id=genre_replacement.id,
            name=genre_replacement.name,
        ),
    )
    delete_mock = MagicMock(return_value=True)
    monkeypatch.setattr(genre_delete_routes, "delete_genre", delete_mock)

    assert (
        client.post(
            "/api/genre/create_genre/",
            headers=auth_header(),
            json={"name": "Fantasy"},
        ).json()["name"]
        == "Fantasy"
    )
    assert (
        client.get(
            "/api/genre/get_genre_by_id/1",
            headers=auth_header(),
        ).json()["id"]
        == 1
    )
    assert (
        client.get(
            "/api/genre/get_genre_by_name/",
            headers=auth_header(),
            params={"name": "Horror"},
        ).json()["name"]
        == "Horror"
    )
    assert client.put(
        "/api/genre/update_genre/",
        headers=auth_header(),
        json={"id": 3, "name": "Mystery"},
    ).json() == {"id": 3, "name": "Mystery"}

    response = client.delete("/api/genre/delete_genre/3", headers=auth_header())

    assert response.json() == {"genre_id": 3, "deleted": True}
    delete_mock.assert_called_once_with(genre_id=3, session=session)


def test_avatar_crud_endpoints(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    avatar = Avatar(id=1, image_url="https://example.com/a.png", description="Avatar")
    monkeypatch.setattr(avatar_create_routes, "create_avatar", lambda **_: avatar)
    monkeypatch.setattr(avatar_get_routes, "get_avatar_by_id", lambda **_: avatar)
    monkeypatch.setattr(avatar_update_routes, "update_avatar", lambda **_: avatar)
    delete_mock = MagicMock(return_value=False)
    monkeypatch.setattr(avatar_delete_routes, "delete_avatar", delete_mock)

    payload = {"image_url": avatar.image_url, "description": avatar.description}

    assert (
        client.post(
            "/api/avatar/create_avatar/",
            headers=auth_header(),
            json=payload,
        ).json()["image_url"]
        == avatar.image_url
    )
    assert (
        client.get(
            "/api/avatar/get_avatar_by_id/1",
            headers=auth_header(),
        ).json()["id"]
        == 1
    )
    assert (
        client.put(
            "/api/avatar/update_avatar/",
            headers=auth_header(),
            json={**payload, "id": 1},
        ).json()["description"]
        == "Avatar"
    )

    response = client.delete("/api/avatar/delete_avatar/1", headers=auth_header())

    assert response.json() == {"avatar_id": 1, "deleted": False}
    delete_mock.assert_called_once_with(avatar_id=1, session=session)


def test_user_status_crud_endpoints(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    status_record = UserStatus(id=1, name="Gold", level=2, benefits="Perks")
    monkeypatch.setattr(
        status_create_routes,
        "create_user_status",
        lambda **_: status_record,
    )
    monkeypatch.setattr(
        status_get_routes,
        "get_user_status_by_id",
        lambda **_: status_record,
    )
    monkeypatch.setattr(
        status_update_routes,
        "update_user_status",
        lambda **_: status_record,
    )
    delete_mock = MagicMock(return_value=True)
    monkeypatch.setattr(status_delete_routes, "delete_user_status", delete_mock)

    payload = {"name": "Gold", "level": 2, "benefits": "Perks"}

    assert (
        client.post(
            "/api/user_status/create_user_status/",
            headers=auth_header(),
            json=payload,
        ).json()["name"]
        == "Gold"
    )
    assert (
        client.get(
            "/api/user_status/get_user_status_by_id/1",
            headers=auth_header(),
        ).json()["level"]
        == 2
    )
    assert (
        client.put(
            "/api/user_status/update_user_status/",
            headers=auth_header(),
            json={**payload, "id": 1},
        ).json()["benefits"]
        == "Perks"
    )

    response = client.delete(
        "/api/user_status/delete_user_status/1",
        headers=auth_header(),
    )

    assert response.json() == {"status_id": 1, "deleted": True}
    delete_mock.assert_called_once_with(id=1, session=session)


def test_user_book_state_crud_and_body_lookup_endpoints(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    state_record = make_state(1)
    monkeypatch.setattr(
        state_create_routes,
        "create_user_book_state",
        lambda **_: state_record,
    )
    monkeypatch.setattr(
        state_get_routes,
        "get_user_book_state_by_id",
        lambda **_: state_record,
    )
    monkeypatch.setattr(
        state_get_routes,
        "get_user_book_states_by_user_id",
        lambda **_: [state_record],
    )
    monkeypatch.setattr(
        state_get_routes,
        "get_user_book_state_by_user_and_book",
        lambda **_: state_record,
    )
    monkeypatch.setattr(
        state_update_routes,
        "update_user_book_state",
        lambda **_: state_record,
    )
    delete_mock = MagicMock(return_value=True)
    monkeypatch.setattr(
        state_delete_routes,
        "delete_user_book_state_by_id",
        delete_mock,
    )

    assert (
        client.post(
            "/api/user_book_state/create_user_book_state/",
            headers=auth_header(),
            json=state_payload(),
        ).json()["reading_status"]
        == "reading"
    )
    assert (
        client.get(
            "/api/user_book_state/get_user_book_state_by_id/1",
            headers=auth_header(),
        ).json()["id"]
        == 1
    )
    assert (
        client.post(
            "/api/user_book_state/get_user_book_states_by_user_id/",
            headers=auth_header(),
            json={"user_id": 1, "limit": 5, "offset": 0},
        ).json()[0]["user_id"]
        == 1
    )
    assert (
        client.post(
            "/api/user_book_state/get_user_book_state_by_user_and_book/",
            headers=auth_header(),
            json={"user_id": 1, "book_id": 2},
        ).json()["book_id"]
        == 2
    )
    assert (
        client.put(
            "/api/user_book_state/update_user_book_state/",
            headers=auth_header(),
            json=state_payload(1),
        ).json()["percent_complete"]
        == 20
    )

    response = client.delete(
        "/api/user_book_state/delete_user_book_state_by_id/1",
        headers=auth_header(),
    )

    assert response.json() == {"user_book_state_id": 1, "deleted": True}
    delete_mock.assert_called_once_with(user_book_state_id=1, session=session)


def test_book_access_crud_endpoints_use_wrapper_bodies(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    access_record = make_access(1)

    def fake_create_access_info(access_info, book_id, session):
        assert access_info.country == "US"
        assert book_id == 12
        return access_record

    monkeypatch.setattr(
        access_create_routes,
        "create_access_info",
        fake_create_access_info,
    )
    monkeypatch.setattr(
        access_get_routes,
        "get_access_info_by_id",
        lambda **_: access_record,
    )
    monkeypatch.setattr(
        access_get_routes,
        "get_access_info_by_book_id",
        lambda **_: access_record,
    )
    monkeypatch.setattr(
        access_update_routes,
        "update_access_info",
        lambda **_: access_record,
    )
    delete_mock = MagicMock(return_value=True)
    monkeypatch.setattr(access_delete_routes, "delete_access_info", delete_mock)

    assert (
        client.post(
            "/api/book_access/create_access_info/",
            headers=auth_header(),
            json={"book_id": 12, "access_info": access_payload()},
        ).json()["webReaderLink"]
        == "https://example.com/read"
    )
    assert (
        client.get(
            "/api/book_access/get_access_info_by_id/1",
            headers=auth_header(),
        ).json()["country"]
        == "US"
    )
    assert (
        client.get(
            "/api/book_access/get_access_info_by_book_id/12",
            headers=auth_header(),
        ).json()["epub"]["isAvailable"]
        is True
    )
    assert (
        client.put(
            "/api/book_access/update_access_info/",
            headers=auth_header(),
            json={"access_info_id": 1, "access_info": access_payload()},
        ).json()["publicDomain"]
        is False
    )

    response = client.delete(
        "/api/book_access/delete_access_info/1",
        headers=auth_header(),
    )

    assert response.json() == {"book_access_id": 1, "deleted": True}
    delete_mock.assert_called_once_with(book_access_id=1, session=session)


def test_book_sale_info_crud_endpoints(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch)
    sale_record = make_sale(1)
    monkeypatch.setattr(
        sale_create_routes,
        "create_book_sale_info",
        lambda **_: sale_record,
    )
    monkeypatch.setattr(
        sale_get_routes,
        "get_book_sale_info_by_id",
        lambda **_: sale_record,
    )
    monkeypatch.setattr(
        sale_update_routes,
        "update_book_sale_info",
        lambda **_: sale_record,
    )
    delete_mock = MagicMock(return_value=True)
    monkeypatch.setattr(sale_delete_routes, "delete_book_sale_info", delete_mock)

    assert (
        client.post(
            "/api/book_sale_info/create_book_sale_info/",
            headers=auth_header(),
            json=sale_payload(),
        ).json()["book_id"]
        == 12
    )
    assert (
        client.get(
            "/api/book_sale_info/get_book_sale_info_by_id/1",
            headers=auth_header(),
        ).json()["saleability"]
        == "FOR_SALE"
    )
    assert (
        client.put(
            "/api/book_sale_info/update_book_sale_info/",
            headers=auth_header(),
            json=sale_payload(1),
        ).json()["id"]
        == 1
    )

    response = client.delete(
        "/api/book_sale_info/delete_book_sale_info/1",
        headers=auth_header(),
    )

    assert response.json() == {"book_sale_info_id": 1, "deleted": True}
    delete_mock.assert_called_once_with(book_sale_info_id=1, session=session)


def test_admin_log_crud_endpoints_are_admin_only(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch, role="admin")
    admin_log = make_admin_log(1)
    monkeypatch.setattr(admin_create_routes, "create_admin_logs", lambda **_: admin_log)
    monkeypatch.setattr(
        admin_get_by_id_routes,
        "get_admin_logs_by_id",
        lambda **_: admin_log,
    )
    monkeypatch.setattr(
        admin_get_routes,
        "get_admin_logs",
        lambda *args: ([admin_log], 1),
    )
    monkeypatch.setattr(admin_update_routes, "update_admin_logs", lambda **_: admin_log)
    delete_mock = MagicMock(return_value=True)
    monkeypatch.setattr(admin_delete_routes, "delete_admin_logs", delete_mock)
    payload = {
        "event_type": "create",
        "event_description": "Created a record",
        "created_at": NOW.isoformat(),
    }

    assert (
        client.post(
            "/api/admin_logs/create_admin_logs/",
            headers=auth_header(),
            json=payload,
        ).json()["event_type"]
        == "create"
    )
    assert (
        client.get(
            "/api/admin_logs/get_admin_logs_by_id/1",
            headers=auth_header(),
        ).json()["id"]
        == 1
    )
    assert (
        client.post(
            "/api/admin_logs/get_admin_logs/",
            headers=auth_header(),
            json={
                "start_time": NOW.isoformat(),
                "end_time": NOW.isoformat(),
                "limit": 10,
                "offset": 0,
            },
        ).json()["total"]
        == 1
    )
    assert (
        client.put(
            "/api/admin_logs/update_admin_logs/",
            headers=auth_header(),
            json={**payload, "id": 1},
        ).json()["event_description"]
        == "Created a record"
    )

    response = client.delete(
        "/api/admin_logs/delete_admin_logs/1",
        headers=auth_header(),
    )

    assert response.json() == {"admin_log_id": 1, "deleted": True}
    delete_mock.assert_called_once_with(admin_log_id=1, session=session)


def test_admin_log_routes_reject_non_admin(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    authenticate(monkeypatch, role="user")
    create_mock = MagicMock()
    monkeypatch.setattr(admin_create_routes, "create_admin_logs", create_mock)

    response = client.post(
        "/api/admin_logs/create_admin_logs/",
        headers=auth_header(),
        json={
            "event_type": "create",
            "event_description": "Created a record",
            "created_at": NOW.isoformat(),
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."
    create_mock.assert_not_called()


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("put", "/api/genre/update_genre/", {"name": "Missing"}),
        (
            "put",
            "/api/avatar/update_avatar/",
            {"image_url": "https://example.com/a.png"},
        ),
        (
            "put",
            "/api/user_status/update_user_status/",
            {"name": "Gold", "level": 2},
        ),
        ("put", "/api/user_book_state/update_user_book_state/", state_payload()),
        ("put", "/api/book_sale_info/update_book_sale_info/", sale_payload()),
        (
            "put",
            "/api/admin_logs/update_admin_logs/",
            {
                "event_type": "create",
                "event_description": "Created a record",
                "created_at": NOW.isoformat(),
            },
        ),
        (
            "put",
            "/api/book_access/update_access_info/",
            {"access_info": access_payload()},
        ),
        (
            "post",
            "/api/book_access/create_access_info/",
            {"access_info": access_payload()},
        ),
    ],
)
def test_missing_required_update_or_wrapper_ids_return_422(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    path: str,
    payload: dict,
) -> None:
    authenticate(
        monkeypatch,
        role="admin" if path.startswith("/api/admin_logs") else "user",
    )

    response = getattr(client, method)(path, headers=auth_header(), json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("path", "route_module", "function_name", "payload"),
    [
        ("/api/genre/get_genre_by_id/404", genre_get_routes, "get_genre_by_id", None),
        (
            "/api/avatar/get_avatar_by_id/404",
            avatar_get_routes,
            "get_avatar_by_id",
            None,
        ),
        (
            "/api/user_status/get_user_status_by_id/404",
            status_get_routes,
            "get_user_status_by_id",
            None,
        ),
        (
            "/api/user_book_state/get_user_book_state_by_id/404",
            state_get_routes,
            "get_user_book_state_by_id",
            None,
        ),
        (
            "/api/book_access/get_access_info_by_id/404",
            access_get_routes,
            "get_access_info_by_id",
            None,
        ),
        (
            "/api/book_sale_info/get_book_sale_info_by_id/404",
            sale_get_routes,
            "get_book_sale_info_by_id",
            None,
        ),
        (
            "/api/admin_logs/get_admin_logs_by_id/404",
            admin_get_by_id_routes,
            "get_admin_logs_by_id",
            None,
        ),
    ],
)
def test_missing_get_records_return_404(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    route_module,
    function_name: str,
    payload: dict | None,
) -> None:
    authenticate(
        monkeypatch,
        role="admin" if path.startswith("/api/admin_logs") else "user",
    )
    monkeypatch.setattr(route_module, function_name, lambda **_: None)

    response = client.get(path, headers=auth_header())

    assert response.status_code == 404
