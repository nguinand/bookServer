from sqlalchemy.orm import Session

from app.db.db_models.user import User


def get_user_by_id(id: int, session: Session) -> User:
    return session.query(User).filter_by(id=id).first()


def get_user_by_username(username: str, session: Session) -> User:
    return session.query(User).filter_by(username=username).first()


def get_users_by_email(email: str, session: Session) -> list[User]:
    return session.query(User).filter_by(email=email).filter_by(email=email).all()
