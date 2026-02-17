from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.db.db_models.user_book_attributes import UserBookAttributes
from app.models.user_book_attributes import UserBookAttributesModel


def create_user_book_attribute(
    book_attribute_model: UserBookAttributesModel, session: Session
) -> UserBookAttributes:
    user_book_attribute_data = UserBookAttributes(
        **book_attribute_model.model_dump(by_alias=True)
    )
    session.add(user_book_attribute_data)
    db_manager.commit_or_raise(session)
    session.refresh(user_book_attribute_data)
    return user_book_attribute_data


def get_user_book_attribute_by_id(
    attribute_id: int, session: Session
) -> UserBookAttributes | None:
    return session.get(UserBookAttributes, attribute_id)


def get_user_book_attribute_by_user_id(
    user_id: int, session: Session, limit: int = 100, offset: int = 0
) -> List[UserBookAttributes]:
    # A user can review multiple books. So there may be multiple entries with the same user_id
    stmt = (
        select(UserBookAttributes)
        .where(UserBookAttributes.user_id == user_id)
        .order_by(UserBookAttributes.id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).all()


def get_user_book_attribute_by_book_id(
    book_id: int, session: Session, limit: int = 100, offset: int = 0
) -> List[UserBookAttributes]:
    # A book can be reviewed by multiple users. So there may be multiple entries with the same book_id
    stmt = (
        select(UserBookAttributes)
        .where(UserBookAttributes.book_id == book_id)
        .order_by(UserBookAttributes.id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).all()


def update_user_book_attribute(
    book_attribute_replacement: UserBookAttributesModel, session: Session
) -> bool:
    if book_attribute_replacement.id is None:
        raise ValueError("Cannot update user book attribute without an ID.")

    user_book_attribute_record = get_user_book_attribute_by_id(
        book_attribute_replacement.id, session
    )

    if not user_book_attribute_record:
        return False

    user_book_attribute_record.user_id = book_attribute_replacement.user_id
    user_book_attribute_record.book_id = book_attribute_replacement.book_id
    user_book_attribute_record.rating = book_attribute_replacement.rating
    user_book_attribute_record.review_text = book_attribute_replacement.review_text
    user_book_attribute_record.updated_at = datetime.now()

    db_manager.commit_or_raise(session)
    return True


def delete_user_book_attribute_by_id(
    user_book_attribute_id: int, session: Session
) -> bool:
    user_book_attribute_record = get_user_book_attribute_by_id(
        user_book_attribute_id, session
    )

    if not user_book_attribute_record:
        return False

    session.delete(user_book_attribute_record)
    db_manager.commit_or_raise(session)
    return True


def convert_user_book_attribute(
    user_book_attribute: UserBookAttributes,
) -> UserBookAttributesModel:
    return UserBookAttributesModel(
        id=user_book_attribute.id,
        user_id=user_book_attribute.user_id,
        book_id=user_book_attribute.book_id,
        rating=user_book_attribute.rating,
        review_text=user_book_attribute.review_text,
        created_at=user_book_attribute.created_at,
        updated_at=user_book_attribute.updated_at,
    )
