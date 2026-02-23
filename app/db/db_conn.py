from pathlib import Path
from typing import Any, Generator

from dotenv import load_dotenv
from sqlalchemy import ChunkedIteratorResult, create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.utils.get_env import get_env_val_or_raise
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load .env file from the current directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class DatabaseOperationError(Exception):
    pass


def batch_results(
    result: ChunkedIteratorResult, batch_size: int = 500
) -> Generator[list[Any], None, None]:
    while True:
        batch = result.fetchmany(batch_size)
        if not batch:
            break
        yield batch


class DatabaseManager:
    """
    Class that handles the engine and session creation.
    """

    database_username = get_env_val_or_raise("DATABASE_USERNAME")
    database_password = get_env_val_or_raise("DATABASE_PASSWORD")
    database_url = get_env_val_or_raise("DATABASE_URL")
    database_name = get_env_val_or_raise("DATABASE_NAME")

    connection_string = f"mysql+mysqldb://{database_username}:{database_password}@{database_url}/{database_name}"
    engine = create_engine(
        connection_string, pool_pre_ping=True, echo=False, pool_recycle=3600
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @property
    def session(self) -> Session:
        """
        Provides a fresh SQLAlchemy session object.
        """
        return self.SessionLocal()

    def get_db(self) -> Session | Generator:
        session = self.session
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def commit_or_raise(session: Session) -> None:
        try:
            session.commit()
        except (IntegrityError, SQLAlchemyError) as e:
            session.rollback()
            logger.error(e)
            raise DatabaseOperationError(e) from e


# Singleton instance
db_manager = DatabaseManager()
