from sqlalchemy.orm import Session

from app.db.db_models.genre import Genre
from app.models.genre import GenreModel


def create_genre(genre_model: GenreModel, session: Session) -> Genre:
    genre_data = Genre(**genre_model.model_dump(by_alias=True))
    session.add(genre_data)
    session.commit()
    session.refresh(genre_data)
    return genre_data


def get_genre_by_id(id: int, session: Session) -> None | Genre:
    return session.query(Genre).filter_by(id=id).first()


def get_genre_by_name(name: str, session: Session) -> None | Genre:
    return session.query(Genre).filter_by(name=name).first()


def update_genre(genre_replacement: GenreModel, session: Session) -> None | Genre:
    if genre_replacement.id is None:
        raise ValueError(
            f"Cannot replace genre without an ID. {genre_replacement.id} - {genre_replacement.name}"
        )

    genre_record = get_genre_by_id(genre_replacement.id, session)

    if not genre_record:
        return None

    genre_record.name = genre_replacement.name
    session.commit()

    return genre_record


def delete_genre(genre_id: int, session: Session) -> bool:
    genre_record = get_genre_by_id(genre_id, session)

    if not genre_record:
        return False

    session.delete(genre_record)
    session.commit()
    return True


def convert_genre_model(genre_record: Genre) -> GenreModel:
    return GenreModel.model_validate(genre_record)
