from sqlalchemy.orm import Session
from app.db.db_models.user import User
from app.db.sql_queries.avatar_queries import get_avatar_by_id
from app.db.sql_queries.user_queries import (
    get_user_by_id,
    get_user_by_username,
    get_users_by_email,
)
from app.db.sql_queries.user_status_queries import get_user_status_by_id
from app.models.user import UserModel


class UserCrud:
    def create_user(self, user_model: UserModel, session: Session) -> User:
        user_data = User(**user_model.model_dump(by_alias=True, exclude_unset=True))
        session.add(user_data)
        session.commit()
        session.refresh(user_data)
        return user_data

    def get_user_by_id(self, id: int, session: Session) -> User:
        user_record = get_user_by_id(id, session)
        return user_record

    def get_users_by_email(self, email: str, session: Session) -> list[User]:
        return get_users_by_email(email, session)

    def get_users_by_username(self, username: str, session: Session) -> User:
        return get_user_by_username(username, session)

    def update_user(self, user_replacement: UserModel, session: Session) -> None | User:
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

    def delete_user(self, user_id: int, session: Session) -> bool:
        user = get_user_by_id(user_id, session)
        if not user:
            return False

        session.delete(user)
        session.commit()
        return True

    def convert_user(self, user_data: User) -> UserModel:
        return UserModel.model_validate(user_data)
