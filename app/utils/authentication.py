from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.db_models.user import User


class Authenticator(BaseModel):
    id: int = Field(
        gt=0, description="ID which would be used in the query", examples=[1, 2, 3]
    )
    password: str = Field(
        description="Plaintext password that will be verified.", examples=["Apple"]
    )

    def verify_password(self, session: Session) -> bool:
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hashed_password = self._get_user_hashed_password(session)
        return pwd_context.verify(self.password, hashed_password)

    def _get_user_hashed_password(self, session: Session) -> None | str:
        stmt = select(User.password_hash).where(User.id == self.id)
        return session.scalars(stmt).one_or_none()
