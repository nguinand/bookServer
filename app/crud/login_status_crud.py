from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.crud.user_crud import get_user_by_id, get_users_by_username
from app.db.db_conn import db_manager
from app.db.db_models.login_status import LoginStatus
from app.models.login_status import MAX_FAILED_LOGIN_ATTEMPTS, LoginStatusModel

FAILED_LOGIN_WINDOW = timedelta(minutes=10)


def create_login_status(
    login_status_model: LoginStatusModel, session: Session
) -> LoginStatus:
    user = get_user_by_id(login_status_model.user_id, session)
    if user is None:
        raise ValueError("User not found.")

    existing_login_status = get_login_status_by_user_id(
        login_status_model.user_id, session
    )
    if existing_login_status is not None:
        raise ValueError("Login status already exists.")

    login_status = LoginStatus(**login_status_model.model_dump())
    session.add(login_status)
    db_manager.commit_or_raise(session)
    session.refresh(login_status)
    return login_status


def get_login_status_by_user_id(user_id: int, session: Session) -> LoginStatus | None:
    return session.get(LoginStatus, user_id)


def update_login_status(
    login_status_replacement: LoginStatusModel, session: Session
) -> LoginStatus | None:
    login_status = get_login_status_by_user_id(
        login_status_replacement.user_id, session
    )
    if login_status is None:
        return None

    login_status.failed_login_attempts = login_status_replacement.failed_login_attempts
    login_status.last_failed_login_attempt_at = (
        login_status_replacement.last_failed_login_attempt_at
    )
    login_status.locked = login_status_replacement.locked
    login_status.locked_at = login_status_replacement.locked_at

    db_manager.commit_or_raise(session)
    session.refresh(login_status)
    return login_status


def delete_login_status_by_user_id(user_id: int, session: Session) -> bool:
    login_status = get_login_status_by_user_id(user_id, session)
    if login_status is None:
        return False

    session.delete(login_status)
    db_manager.commit_or_raise(session)
    return True


def unlock_login_status_by_user_id(
    user_id: int, session: Session
) -> LoginStatus | None:
    login_status = get_login_status_by_user_id(user_id, session)
    if login_status is None:
        return None

    reset_login_status_to_unlocked(login_status)
    db_manager.commit_or_raise(session)
    session.refresh(login_status)
    return login_status


def unlock_login_status_by_username(
    username: str, session: Session
) -> LoginStatus | None:
    user = get_users_by_username(username, session)
    if user is None:
        raise ValueError("User not found.")
    return unlock_login_status_by_user_id(user.id, session)


def record_failed_login_attempt(
    user_id: int, session: Session, attempted_at: datetime | None = None
) -> LoginStatus | None:
    user = get_user_by_id(user_id, session)
    if user is None:
        return None

    failed_at = attempted_at or datetime.now()
    login_status = get_login_status_by_user_id(user_id, session)
    if login_status is None:
        login_status = LoginStatus(user_id=user_id)
        session.add(login_status)

    if login_status.locked:
        return login_status

    if should_increment_failed_login_attempts(login_status, failed_at):
        login_status.failed_login_attempts = min(
            login_status.failed_login_attempts + 1,
            MAX_FAILED_LOGIN_ATTEMPTS,
        )
    else:
        login_status.failed_login_attempts = 1
        login_status.locked = False
        login_status.locked_at = None

    login_status.last_failed_login_attempt_at = failed_at
    if login_status.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        login_status.locked = True
        login_status.locked_at = failed_at

    db_manager.commit_or_raise(session)
    session.refresh(login_status)
    return login_status


def reset_login_status_after_successful_login(
    user_id: int, session: Session
) -> LoginStatus | None:
    login_status = get_login_status_by_user_id(user_id, session)
    if login_status is None:
        return None

    reset_login_status_to_unlocked(login_status)
    db_manager.commit_or_raise(session)
    session.refresh(login_status)
    return login_status


def reset_login_status_to_unlocked(login_status: LoginStatus) -> None:
    login_status.failed_login_attempts = 0
    login_status.last_failed_login_attempt_at = None
    login_status.locked = False
    login_status.locked_at = None


def should_increment_failed_login_attempts(
    login_status: LoginStatus, failed_at: datetime
) -> bool:
    if login_status.last_failed_login_attempt_at is None:
        return False
    return failed_at - login_status.last_failed_login_attempt_at <= FAILED_LOGIN_WINDOW


def convert_login_status(login_status: LoginStatus) -> LoginStatusModel:
    return LoginStatusModel.model_validate(login_status)
