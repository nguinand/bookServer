from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.db.db_models.avatar import Avatar
from app.models.avatar import AvatarModel


def create_avatar(avatar_model: AvatarModel, session: Session) -> Avatar:
    avatar_data = Avatar(**avatar_model.model_dump(by_alias=True))
    session.add(avatar_data)
    db_manager.commit_or_raise(session)
    session.refresh(avatar_data)
    return avatar_data


def get_avatar_by_id(avatar_id: int, session: Session) -> Avatar | None:
    return session.get(Avatar, avatar_id)


def update_avatar(avatar_replacement: AvatarModel, session: Session) -> None | Avatar:
    if avatar_replacement.id is None:
        raise AttributeError("Avatar id is required")

    avatar_record = get_avatar_by_id(avatar_replacement.id, session)
    if not avatar_record:
        return None

    avatar_record.image_url = avatar_replacement.image_url
    avatar_record.description = avatar_replacement.description
    db_manager.commit_or_raise(session)
    return avatar_record


def delete_avatar(avatar_id: int, session: Session) -> bool:
    avatar_record = get_avatar_by_id(avatar_id, session)

    if not avatar_record:
        return False

    session.delete(avatar_record)
    db_manager.commit_or_raise(session)
    return True


def convert_avatar_to_model(avatar_record: Avatar) -> AvatarModel:
    return AvatarModel.model_validate(avatar_record)
