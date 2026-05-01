import os
from collections.abc import Generator
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("GOOGLE_BOOKS_API_URL", "https://example.com/books")
os.environ.setdefault("GOOGLE_BOOKS_API_KEY", "test-key")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.crud.admin_logs_crud import get_admin_logs
from app.db.db_models.admin_logs import AdminLogs


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:")
    AdminLogs.__table__.create(bind=engine)
    with Session(engine) as test_session:
        yield test_session


def test_get_admin_logs_filters_orders_paginates_and_counts(
    session: Session,
) -> None:
    start_time = datetime(2026, 4, 1, 0, 0, 0)
    middle_time = datetime(2026, 4, 15, 12, 0, 0)
    end_time = datetime(2026, 4, 30, 23, 59, 59)
    session.add_all(
        [
            AdminLogs(
                id=1,
                event_type="create",
                event_description="Outside range",
                created_at=datetime(2026, 3, 31, 23, 59, 59),
            ),
            AdminLogs(
                id=2,
                event_type="create",
                event_description="Start boundary",
                created_at=start_time,
            ),
            AdminLogs(
                id=3,
                event_type="update",
                event_description="Middle lower id",
                created_at=middle_time,
            ),
            AdminLogs(
                id=4,
                event_type="delete",
                event_description="Middle higher id",
                created_at=middle_time,
            ),
            AdminLogs(
                id=5,
                event_type="modify",
                event_description="End boundary",
                created_at=end_time,
            ),
        ]
    )
    session.commit()

    admin_logs, total = get_admin_logs(
        start_time,
        end_time,
        2,
        1,
        session,
    )

    assert total == 4
    assert [admin_log.id for admin_log in admin_logs] == [4, 3]
