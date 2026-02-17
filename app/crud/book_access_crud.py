from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.db.db_models import BookAccess
from app.models.access_info import AccessInfoModel, FormatInfoModel


def create_access_info(access_info: AccessInfoModel, session: Session) -> BookAccess:
    access_info_data = BookAccess(**access_info.to_orm_dict())
    session.add(access_info_data)
    db_manager.commit_or_raise(session)
    return access_info_data


def get_access_info_by_id(access_info_id: int, session: Session) -> BookAccess | None:
    return session.get(BookAccess, access_info_id)


def get_access_info_by_book_id(book_id: int, session: Session) -> BookAccess | None:
    return session.scalars(select(BookAccess).where(BookAccess.book_id == book_id))


def update_access_info(
    access_info_id: int, access_info_replacement: AccessInfoModel, session: Session
) -> None | BookAccess:
    access_info_record = get_access_info_by_id(access_info_id, session)
    if access_info_record is None:
        return None
    access_info_record.country = access_info_replacement.country
    access_info_record.viewability = access_info_replacement.viewability
    access_info_record.embeddable = access_info_replacement.embeddable
    access_info_record.public_domain = access_info_replacement.public_domain

    if access_info_replacement.epub is None:
        access_info_record.epub_available = None
        access_info_record.epub_token_link = None
    else:
        access_info_record.epub_available = access_info_replacement.epub.isAvailable
        access_info_record.epub_token_link = access_info_replacement.epub.acsTokenLink

    if access_info_replacement.pdf is None:
        access_info_record.pdf_available = None
        access_info_record.pdf_token_link = None
    else:
        access_info_record.pdf_available = access_info_replacement.pdf.isAvailable
        access_info_record.pdf_token_link = access_info_replacement.pdf.acsTokenLink

    access_info_record.web_reader_link = access_info_replacement.web_reader_link

    db_manager.commit_or_raise(session)
    return access_info_record


def delete_access_info(book_access_id: int, session: Session) -> bool:
    access_info = get_access_info_by_id(book_access_id, session)
    if not access_info:
        return False
    session.delete(access_info)
    db_manager.commit_or_raise(session)
    return True


def convert_access_info(book_access_data: BookAccess) -> AccessInfoModel:
    epub = FormatInfoModel(
        isAvailable=book_access_data.epub_available,
        acsTokenLink=book_access_data.epub_token_link,
    )
    pdf = FormatInfoModel(
        isAvailable=book_access_data.pdf_available,
        acsTokenLink=book_access_data.pdf_token_link,
    )
    return AccessInfoModel(
        country=book_access_data.country,
        viewability=book_access_data.viewability,
        embeddable=book_access_data.embeddable,
        publicDomain=book_access_data.public_domain,
        epub=epub,
        pdf=pdf,
        webReaderLink=book_access_data.web_reader_link,
    )
