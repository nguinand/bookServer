from sqlalchemy.orm import Session

from app.db.db_models.user_status import UserStatus
from app.models.user_status import UserStatusModel


def create_user_status(
    user_status_model: UserStatusModel, session: Session
) -> UserStatus: ...


def get_user_status_by_id(id: int, session: Session) -> UserStatus | None:
    return session.query(UserStatus).filter_by(id=id).first()
