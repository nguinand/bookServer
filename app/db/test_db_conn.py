import pytest
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from sqlalchemy.exc import OperationalError
from sqlalchemy.inspection import inspect


print("Mapped columns:", inspect(User).columns.keys())


def test_conn():
    try:
        with db_manager.session as session:
            session.query(User).limit(1).all()
    except OperationalError as exc:
        pytest.skip(f"Database connection unavailable for integration test: {exc}")
