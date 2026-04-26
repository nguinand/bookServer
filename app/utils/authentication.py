from passlib.context import CryptContext
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PasswordHandler(BaseModel):
    id: int | None = Field(
        default=None,
        gt=0,
        description="User ID used to locate the account.",
        examples=[1, 2, 3],
    )
    username: str | None = Field(
        default=None,
        description="Username used to locate the account.",
        examples=["jonydoe"],
    )
    password: str = Field(
        description="Plaintext password that will be verified.", examples=["Apple"]
    )

    @model_validator(mode="after")
    def validate_identifier(self) -> "PasswordHandler":
        if self.id is None and self.username is None:
            raise ValueError("PasswordHandler requires either an id or a username.")
        if self.id is not None and self.username is not None:
            raise ValueError(
                "PasswordHandler accepts either an id or a username, not both."
            )
        return self

    @staticmethod
    def _password_context() -> CryptContext:
        return CryptContext(schemes=["argon2"], deprecated="auto")

    def get_user(self, session: Session) -> User | None:
        if self.id is not None:
            return session.get(User, self.id)

        stmt = select(User).where(User.username == self.username)
        return session.scalars(stmt).one_or_none()

    def get_authenticated_user(self, session: Session) -> User | None:
        user = self.get_user(session)
        if user and self._password_context().verify(self.password, user.password_hash):
            return user
        return None

    def verify_password(self, session: Session) -> bool:
        return self.get_authenticated_user(session) is not None

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordHandler._password_context().hash(password)

    def update_password(self, password_hash: str, user: User, session: Session) -> bool:
        user.password_hash = password_hash
        session.add(user)
        db_manager.commit_or_raise(session)
        return True
