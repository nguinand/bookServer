from sqlalchemy.orm import Session
from app.crud.avatar_crud import get_avatar_by_id
from app.crud.user_status_crud import get_user_status_by_id
from app.db.db_models.user import User
from app.models.user import UserModel


def create_user(user_model: UserModel, session: Session) -> User:
    user_data = User(
        **user_model.model_dump(by_alias=True, exclude_unset=True)
    )  # verify this
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


def get_user_by_id(id: int, session: Session) -> None | User:
    return session.query(User).filter_by(id=id).first()


def get_users_by_email(email: str, session: Session) -> None | list[User]:
    return session.query(User).filter_by(email=email).filter_by(email=email).all()


def get_users_by_username(username: str, session: Session) -> None | User:
    return session.query(User).filter_by(username=username).first()


def update_user(user_replacement: UserModel, session: Session) -> None | User:
    if user_replacement.id is None:
        raise ValueError(
            f"Cannot replace user without an ID. {user_replacement.id} - {user_replacement.email}"
        )

    user_record = get_user_by_id(user_replacement.id, session)
    if not user_record:
        return None

    user_record.first_name = user_replacement.first_name
    user_record.last_name = user_replacement.last_name
    user_record.username = user_replacement.username
    user_record.email = user_replacement.email
    user_record.password_hash = user_replacement.password_hash
    user_record.role = user_replacement.role
    user_record.last_login = user_replacement.last_login

    # check avatar_id exists in Avatar
    if user_replacement.avatar_id is not None:
        avatar = get_avatar_by_id(user_replacement.avatar_id, session)
        if avatar is not None:
            user_record.avatar_id = user_replacement.avatar_id
    # check status_id exists in UserStatus
    if user_replacement.status_id is not None:
        user_status = get_user_status_by_id(user_replacement.status_id, session)
        if user_status is not None:
            user_record.status_id = user_replacement.status_id

    user_record.bookcases = user_record.bookcases

    session.commit()
    return user_record


def delete_user(user_id: int, session: Session) -> bool:
    user = get_user_by_id(user_id, session)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True


def convert_user(user_data: User) -> UserModel:
    return UserModel.model_validate(user_data)
