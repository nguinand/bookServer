from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.utils.get_env import get_env_val_or_raise

# Load .env file from the current directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


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

    def get_db(self) -> Session:
        session = self.session
        try:
            yield session
        finally:
            session.close()


# Singleton instance
db_manager = DatabaseManager()
