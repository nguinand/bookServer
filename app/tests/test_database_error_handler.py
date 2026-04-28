import asyncio
import json
import os
from unittest.mock import MagicMock, Mock

from sqlalchemy.exc import IntegrityError

# Avoid import-time db_manager initialization errors in unit tests.
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")
os.environ.setdefault("GOOGLE_BOOKS_API_URL", "https://example.com/books")
os.environ.setdefault("GOOGLE_BOOKS_API_KEY", "test-key")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app import main
from app.db.db_conn import DatabaseOperationError
from app.utils.error_logger import ErrorLogOperation


class DuplicateEmailError(Exception):
    pass


def make_commit_error() -> DatabaseOperationError:
    try:
        try:
            raise IntegrityError(
                "insert user", {}, DuplicateEmailError("duplicate email")
            )
        except IntegrityError as original_error:
            raise DatabaseOperationError(
                original_error,
                operation=ErrorLogOperation.CREATE_USER,
            ) from original_error
    except DatabaseOperationError as database_error:
        return database_error


def test_database_error_handler_records_error_and_returns_sanitized_response(
    monkeypatch,
) -> None:
    recorder = MagicMock()
    recorder_class = Mock(return_value=recorder)
    monkeypatch.setattr(main, "ErrorLogRecorder", recorder_class)
    monkeypatch.setattr(
        main, "uuid4", Mock(return_value="00000000-0000-0000-0000-000000000123")
    )

    request = main.Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/database/create_user/",
            "headers": [],
        }
    )

    response = asyncio.run(
        main.sqlalchemy_error_handler(
            request,
            make_commit_error(),
        )
    )

    recorder_class.assert_called_once()
    recorder_kwargs = recorder_class.call_args.kwargs
    assert recorder_kwargs["error_id"] == "00000000-0000-0000-0000-000000000123"
    assert recorder_kwargs["name"] == ErrorLogOperation.CREATE_USER
    assert recorder_kwargs["exception_type"] == str(DuplicateEmailError)
    assert recorder_kwargs["description"] == "duplicate email"
    recorder.record_error.assert_called_once_with()
    assert response.status_code == 500
    assert json.loads(response.body) == {
        "detail": "A database error occurred. Please try again later.",
        "error_id": "00000000-0000-0000-0000-000000000123",
    }
