from sqlalchemy.orm import Session

from app.db.db_models.avatar import Avatar


def get_avatar_by_id(id: int, session: Session) -> Avatar:
    return session.query(Avatar).filter_by(id=id).first()
