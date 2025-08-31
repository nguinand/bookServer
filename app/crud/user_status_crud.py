from sqlalchemy.orm import Session

from app.db.db_models.user_status import UserStatus
from app.models.user_status import UserStatusModel


def create_user_status(
    user_status_model: UserStatusModel, session: Session
) -> UserStatus:
    user_status_data = UserStatusModel(
        **user_status_model.model_dump(by_alias=True, exclude_unset=True)
    )
    session.add(user_status_data)
    session.commit()
    session.refresh(user_status_data)
    return user_status_data


def get_user_status_by_id(id: int, session: Session) -> UserStatus | None:
    return session.query(UserStatus).filter_by(id=id).first()


def update_user_status(
    user_status_replacement: UserStatus, session: Session
) -> None | UserStatus:
    if user_status_replacement.id is None:
        raise ValueError("user_status_replacement must have an id")

    user_status_record = get_user_status_by_id(user_status_replacement.id, session)
    if not user_status_record:
        return None

    user_status_record.name = user_status_replacement.name
    user_status_record.level = user_status_replacement.level
    user_status_record.benefits = user_status_replacement.benefits
    session.commit()
    session.refresh(user_status_record)
    return user_status_record


def delete_user_status(id: int, session: Session) -> bool:
    user_status = get_user_status_by_id(id, session)
    if not user_status:
        return False

    session.delete(user_status)
    session.commit()
    return True
