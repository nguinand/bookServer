from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any, Generator

from dotenv import load_dotenv
from sqlalchemy import URL, ChunkedIteratorResult, create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.utils.error_log_enums import ErrorLogOperation
from app.utils.get_env import get_env_val_or_raise
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load .env file from the current directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class DatabaseOperationError(Exception):
    def __init__(
        self,
        error: BaseException | str,
        operation: ErrorLogOperation | str | None = None,
    ) -> None:
        super().__init__(error)
        self.operation = operation


def batch_results(
    result: ChunkedIteratorResult, batch_size: int = 500
) -> Iterator[Sequence[Any]]:
    while True:
        batch = result.fetchmany(batch_size)
        if not batch:
            break
        yield batch


def build_database_url() -> URL:
    return URL.create(
        drivername="mysql+mysqldb",
        username=get_env_val_or_raise("DATABASE_USERNAME"),
        password=get_env_val_or_raise("DATABASE_PASSWORD"),
        host=get_env_val_or_raise("DATABASE_URL"),
        database=get_env_val_or_raise("DATABASE_NAME"),
    )


class DatabaseManager:
    def __init__(self):
        self.connection_string = build_database_url()
        self.engine = create_engine(
            self.connection_string, pool_pre_ping=True, echo=False, pool_recycle=3600
        )
        self.session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @property
    def session(self) -> Session:
        """
        Provides a fresh SQLAlchemy session object.
        """
        return self.session_factory()

    def get_db(self) -> Session | Generator:
        # FastAPI dependency injection
        session = self.session
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def commit_or_raise(
        session: Session,
        operation: ErrorLogOperation | str | None = None,
    ) -> None:
        try:
            session.commit()
        except (IntegrityError, SQLAlchemyError) as e:
            session.rollback()
            logger.error(e)
            raise DatabaseOperationError(e, operation=operation) from e


# Singleton instance
db_manager = DatabaseManager()
