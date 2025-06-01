from app.db.db_models.genre import Genre
from sqlalchemy.orm import Session


def get_genre_by_name(name: str, session: Session) -> Genre | None:
    return session.query(Genre).filter_by(name=name).first()


def get_genre_by_id(id: int, session: Session) -> Genre | None:
    genre_record = session.query(Genre).filter_by(id=id).first()
    return genre_record
