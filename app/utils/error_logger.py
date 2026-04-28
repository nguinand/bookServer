from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.db.db_conn import db_manager
from app.db.db_models.error_log import ErrorLog
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorLogOperation(StrEnum):
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"


class ErrorLogRecorder(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    error_id: str = Field(
        description="The public correlation ID for the failed operation.",
        examples=["00000000-0000-0000-0000-000000000001"],
        min_length=1,
        max_length=36,
    )
    name: ErrorLogOperation | str = Field(
        description="The operation that failed.",
        examples=["create_user", "update_user", "delete_user"],
        min_length=1,
        max_length=100,
    )
    exception_type: str = Field(
        description="The original exception class.",
        examples=["<class 'MySQLdb.IntegrityError'>"],
        min_length=1,
        max_length=255,
    )
    description: str = Field(
        description="The original exception message.",
        examples=["Duplicate entry 'test@example.com' for key 'users.email'"],
        min_length=1,
    )

    def record_error(self) -> ErrorLog | None:
        try:
            error_log = ErrorLog(**self.model_dump())
            with db_manager.session as session:
                session.add(error_log)
                db_manager.commit_or_raise(session)
                session.refresh(error_log)
                return error_log
        except Exception as error_log_exception:
            logger.error(
                "Failed to record database error log. "
                f"name={self.name}; error={error_log_exception}"
            )
            return None
