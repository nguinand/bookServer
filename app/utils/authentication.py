from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.db_conn import DatabaseOperationError, db_manager
from app.db.db_models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PasswordHandler(BaseModel):
    id: int = Field(
        gt=0, description="ID which would be used in the query", examples=[1, 2, 3]
    )
    password: str = Field(
        description="Plaintext password that will be verified.", examples=["Apple"]
    )

    def verify_password(self, session: Session) -> bool:
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hashed_password = self._get_user_hashed_password(session)
        if hashed_password:
            return pwd_context.verify(self.password, hashed_password)
        return False

    def _get_user_hashed_password(self, session: Session) -> None | str:
        stmt = select(User.password_hash).where(User.id == self.id)
        return session.scalars(stmt).one_or_none()

    @staticmethod
    def hash_password(password: str) -> str:
        password_context = CryptContext(schemes=["argon2"], deprecated="auto")
        return password_context.hash(password)

    def update_password(self, password_hash: str, user: User, session: Session) -> bool:
        try:
            user.password_hash = password_hash
            session.add(user)
            db_manager.commit_or_raise(session)
            return True
        except DatabaseOperationError:
            logger.error(
                f"Could not update password for user {user.email}.", exc_info=True
            )
            return False
