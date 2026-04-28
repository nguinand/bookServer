import os
from unittest.mock import MagicMock

# Avoid import-time db_manager initialization errors in unit tests.
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_URL", "localhost")
os.environ.setdefault("DATABASE_NAME", "test")

from app.db.db_models.error_log import ErrorLog
from app.utils import error_logger as crud


def test_record_error_commits_and_refreshes(monkeypatch) -> None:
    logging_session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = logging_session
    db_manager_mock = MagicMock()
    db_manager_mock.session = session_context
    monkeypatch.setattr(crud, "db_manager", db_manager_mock)
    recorder = crud.ErrorLogRecorder(
        error_id="00000000-0000-0000-0000-000000000001",
        name=crud.ErrorLogOperation.CREATE_USER,
        exception_type="<class 'Exception'>",
        description="boom",
    )

    created = recorder.record_error()

    logging_session.rollback.assert_not_called()
    logging_session.add.assert_called_once()
    error_log = logging_session.add.call_args.args[0]
    assert isinstance(error_log, ErrorLog)
    assert error_log.error_id == "00000000-0000-0000-0000-000000000001"
    assert error_log.name == "create_user"
    assert error_log.exception_type == "<class 'Exception'>"
    assert error_log.description == "boom"
    db_manager_mock.commit_or_raise.assert_called_once_with(logging_session)
    logging_session.refresh.assert_called_once_with(error_log)
    assert created is error_log


def test_error_log_operation_values_are_stored_as_strings(monkeypatch) -> None:
    logging_session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = logging_session
    db_manager_mock = MagicMock()
    db_manager_mock.session = session_context
    monkeypatch.setattr(crud, "db_manager", db_manager_mock)
    recorder = crud.ErrorLogRecorder(
        error_id="00000000-0000-0000-0000-000000000002",
        name=crud.ErrorLogOperation.UPDATE_USER,
        exception_type="<class 'Exception'>",
        description="commit failed",
    )

    created = recorder.record_error()

    assert created is not None
    assert created.name == "update_user"


def test_record_error_logs_write_failure(monkeypatch) -> None:
    recorder = crud.ErrorLogRecorder(
        error_id="00000000-0000-0000-0000-000000000003",
        name="delete_user",
        exception_type="<class 'Exception'>",
        description="boom",
    )
    logger_mock = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.side_effect = RuntimeError("log write failed")
    db_manager_mock = MagicMock()
    db_manager_mock.session = session_context
    monkeypatch.setattr(crud, "db_manager", db_manager_mock)
    monkeypatch.setattr(crud, "logger", logger_mock)

    created = recorder.record_error()

    assert created is None
    logger_mock.error.assert_called_once()
