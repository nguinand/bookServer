from app.db.db_models.author import Author
from sqlalchemy.orm import Session


def get_author_by_name(name: str, session: Session) -> Author | None:
    return session.query(Author).filter_by(name=name).first()


def get_author_by_id(id: int, session: Session) -> Author | None:
    author_record = session.query(Author).filter_by(id=id).first()
    return author_record
