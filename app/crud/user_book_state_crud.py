from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.db.db_models.user_book_state import UserBookState
from app.models.user_book_state import UserBookStateModel


def create_user_book_state(
    user_book_state_model: UserBookStateModel, session: Session
) -> UserBookState:
    user_book_state_data = UserBookState(
        **user_book_state_model.model_dump(by_alias=True)
    )
    session.add(user_book_state_data)
    db_manager.commit_or_raise(session)
    session.refresh(user_book_state_data)
    return user_book_state_data


def get_user_book_state_by_id(
    user_book_state_id: int, session: Session
) -> UserBookState | None:
    return session.get(UserBookState, user_book_state_id)


def get_user_book_states_by_user_id(
    user_id: int, session: Session, limit: int = 100, offset: int = 0
) -> list[UserBookState]:
    stmt = (
        select(UserBookState)
        .where(UserBookState.user_id == user_id)
        .order_by(UserBookState.id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).all()  # type: ignore


def get_user_book_state_by_user_and_book(
    user_id: int, book_id: int, session: Session, limit: int = 100, offset: int = 0
) -> UserBookState | None:
    stmt = (
        select(UserBookState)
        .where(UserBookState.user_id == user_id, UserBookState.book_id == book_id)
        .order_by(UserBookState.id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).all()  # type: ignore


def update_user_book_state(
    user_book_state_replacement: UserBookStateModel, session: Session
) -> None | UserBookState:
    if user_book_state_replacement.id is None:
        raise ValueError("Cannot replace a user book state record without an ID.")

    user_book_state_record = get_user_book_state_by_id(
        user_book_state_replacement.id, session
    )

    if not user_book_state_record:
        return None

    user_book_state_record.user_id = user_book_state_replacement.user_id
    user_book_state_record.book_id = user_book_state_replacement.book_id
    user_book_state_record.reading_status = user_book_state_replacement.reading_status
    user_book_state_record.current_page = user_book_state_replacement.current_page
    user_book_state_record.percent_complete = (
        user_book_state_replacement.percent_complete
    )
    user_book_state_record.started_at = user_book_state_replacement.started_at
    user_book_state_record.finished_at = user_book_state_replacement.finished_at

    db_manager.commit_or_raise(session)
    return user_book_state_record


def delete_user_book_state_by_id(user_book_state_id: int, session: Session) -> bool:
    user_book_state_record = get_user_book_state_by_id(user_book_state_id, session)

    if not user_book_state_record:
        return False

    session.delete(user_book_state_record)
    db_manager.commit_or_raise(session)
    return True


def convert_user_book_state(
    user_book_state: UserBookState,
) -> UserBookStateModel:
    return UserBookStateModel.model_validate(user_book_state)
