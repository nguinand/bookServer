from sqlalchemy.orm import Session

from app.db.db_models.user_status import UserStatus


def get_user_status_by_id(id: int, session: Session) -> UserStatus:
    return session.query(UserStatus).filter_by(id=id).first()
