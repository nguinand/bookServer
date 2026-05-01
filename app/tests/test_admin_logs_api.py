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

from app.api.admin_logs import get_admin_logs as admin_logs_routes
from app.db.db_conn import db_manager
from app.db.db_models.admin_logs import AdminLogs
from app.db.db_models.user import User
from app.main import app
from app.utils import api_token as api_token_module
from app.utils.api_token import create_access_token


START_TIME = datetime(2026, 4, 1, 0, 0, 0)
END_TIME = datetime(2026, 4, 30, 23, 59, 59)


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


def admin_logs_payload() -> dict[str, str | int]:
    return {
        "start_time": START_TIME.isoformat(),
        "end_time": END_TIME.isoformat(),
        "limit": 2,
        "offset": 1,
    }


def test_get_admin_logs_returns_paginated_logs_for_admin(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    admin_user = make_user()
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: admin_user if user_id == 1 else None,
    )

    def fake_get_admin_logs(
        start_time: datetime,
        end_time: datetime,
        limit: int,
        offset: int,
        session: MagicMock,
    ) -> tuple[list[AdminLogs], int]:
        assert start_time == START_TIME
        assert end_time == END_TIME
        assert limit == 2
        assert offset == 1
        return (
            [
                AdminLogs(
                    id=4,
                    event_type="delete",
                    event_description="Deleted user",
                    created_at=datetime(2026, 4, 25, 10, 0, 0),
                ),
                AdminLogs(
                    id=3,
                    event_type="create",
                    event_description="Created book",
                    created_at=datetime(2026, 4, 20, 10, 0, 0),
                ),
            ],
            7,
        )

    monkeypatch.setattr(admin_logs_routes, "get_admin_logs", fake_get_admin_logs)

    response = client.post(
        "/api/database/get_admin_logs/",
        headers=auth_header(1),
        json=admin_logs_payload(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "logs": [
            {
                "id": 4,
                "event_type": "delete",
                "event_description": "Deleted user",
                "created_at": "2026-04-25T10:00:00",
            },
            {
                "id": 3,
                "event_type": "create",
                "event_description": "Created book",
                "created_at": "2026-04-20T10:00:00",
            },
        ],
        "limit": 2,
        "offset": 1,
        "count": 2,
        "total": 7,
    }


def test_get_admin_logs_rejects_non_admin_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    current_user = make_user(
        username="regular_user",
        email="regular@example.com",
        role="user",
    )
    get_admin_logs_mock = MagicMock()
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: current_user if user_id == 1 else None,
    )
    monkeypatch.setattr(admin_logs_routes, "get_admin_logs", get_admin_logs_mock)

    response = client.post(
        "/api/database/get_admin_logs/",
        headers=auth_header(1),
        json=admin_logs_payload(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this resource."
    get_admin_logs_mock.assert_not_called()


def test_get_admin_logs_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/database/get_admin_logs/",
        json=admin_logs_payload(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_admin_logs_rejects_invalid_time_frame(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    admin_user = make_user()
    get_admin_logs_mock = MagicMock()
    monkeypatch.setattr(
        api_token_module,
        "get_user_by_id",
        lambda user_id, session: admin_user if user_id == 1 else None,
    )
    monkeypatch.setattr(admin_logs_routes, "get_admin_logs", get_admin_logs_mock)

    response = client.post(
        "/api/database/get_admin_logs/",
        headers=auth_header(1),
        json={
            "start_time": END_TIME.isoformat(),
            "end_time": START_TIME.isoformat(),
            "limit": 2,
            "offset": 0,
        },
    )

    assert response.status_code == 422
    get_admin_logs_mock.assert_not_called()
