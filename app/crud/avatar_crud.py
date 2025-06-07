from sqlalchemy.orm import Session

from app.db.db_models.avatar import Avatar
from app.models.avatar import AvatarModel


def create_avatar(avatar_model: AvatarModel, session: Session) -> Avatar: ...


def get_avatar_by_id(avatar_id: int, session: Session) -> Avatar | None:
    return session.query(Avatar).filter_by(id=avatar_id).first()


def update_avatar(avatar_model: AvatarModel, session: Session) -> Avatar: ...


def delete_avatar(avatar_id: int, session: Session) -> bool: ...


def convert_avatar_to_model(avatar_record: Avatar): ...
