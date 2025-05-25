from sqlalchemy.orm import Session
from app.db.db_models.avatar import Avatar
from app.db.db_models.user import User
from app.db.db_models.user_status import UserStatus
from app.models.user import UserModel


class UserCrud:
    def create_user(self, user_model: UserModel, session: Session) -> User:
        user_data = User(**user_model.model_dump(by_alias=True, exclude_unset=True))
        session.add(user_data)
        session.commit()
        session.refresh(user_data)
        return user_data

    def get_user_by_id(self, id: int, session: Session) -> User:
        user_record = session.query(User).filter_by(id=id).first()
        return user_record

    def get_users_by_email(self, email: str, session: Session) -> list[User]:
        users = session.query(User).filter_by(email=email).all()
        return users

    def get_users_by_username(self, username: str, session: Session) -> User:
        user_record = session.query(User).filter_by(email=username).first()
        return user_record

    def update_user(
        self, user_replacement: UserModel, session: Session
    ) -> None | User:
        if user_replacement.id is None:
            raise ValueError(
                f"Cannot replace user without an ID. {user_replacement.id} - {user_replacement.email}"
            )

        user_record = session.query(User).filter_by(id=user_replacement.id).first()

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
            avatar = (
                session.query(Avatar).filter_by(id=user_replacement.avatar_id).first()
            )
            if avatar is not None:
                user_record.avatar_id = user_replacement.avatar_id
        # check status_id exists in UserStatus
        if user_replacement.status_id is not None:
            user_status = (
                session.query(UserStatus)
                .filter_by(id=user_replacement.status_id)
                .first()
            )
            if user_status is not None:
                user_record.status_id = user_replacement.status_id

        user_record.bookcases = user_record.bookcases

        session.commit()
        return user_record

    def delete_user(self, user_id: int, session: Session) -> bool:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False

        session.delete(user)
        session.commit()
        return True

    def convert_user(
        self, user_data: User
    ) -> UserModel:
        return UserModel.model_validate(user_data)