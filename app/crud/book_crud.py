from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.author_crud import create_author, get_author_by_name
from app.crud.genre_crud import get_genre_by_name
from app.crud.shared_queries import get_book_by_book_id
from app.db.db_conn import db_manager
from app.db.db_models import Book
from app.db.db_models.author import Author
from app.db.db_models.book_access import BookAccess
from app.db.db_models.book_identifier import BookIdentifier
from app.db.db_models.book_sale_info import BookSaleInfo
from app.db.db_models.genre import Genre
from app.models.author import AuthorModel
from app.models.book import BookModel


def store_book_entry(book_model: BookModel, session: Session) -> Book:
    book_data = Book(
        google_books_id=book_model.google_books_id,
        title=book_model.volume_info.title,
        subtitle=book_model.volume_info.subtitle,
        publisher_name=book_model.volume_info.publisher,
        published_date=book_model.volume_info.published_date,
        description=book_model.volume_info.description,
        page_count=book_model.volume_info.page_count,
        average_rating=book_model.volume_info.average_rating,
        ratings_count=book_model.volume_info.ratings_count,
        maturity_rating=book_model.volume_info.maturity_rating,
        cover_image=book_model.volume_info.image_links.thumbnail
        if book_model.volume_info.image_links
        else None,
        preview_link=book_model.volume_info.preview_link,
        info_link=book_model.volume_info.info_link,
        language=book_model.volume_info.language,
    )

    book_authors: List[Author] = []
    for name in book_model.volume_info.authors or []:
        if author := get_author_by_name(name, session):
            book_authors.append(author)
        else:
            author = create_author(AuthorModel(name=name), session=session)
            book_authors.append(author)

    book_data.authors = book_authors

    if book_model.sale_info:
        sale_info_model = book_model.sale_info
        book_data.book_sale_info = BookSaleInfo(
            country=sale_info_model.country,
            saleability=sale_info_model.saleability,
            is_ebook=sale_info_model.is_ebook,
            buy_link=sale_info_model.buy_link,
            list_price=sale_info_model.list_price.amount
            if sale_info_model.list_price
            else None,
            list_price_currency_code=sale_info_model.list_price.currencyCode
            if sale_info_model.list_price
            else None,
            retail_price=sale_info_model.retail_price.amount
            if sale_info_model.retail_price
            else None,
            retail_price_currency_code=sale_info_model.retail_price.currencyCode
            if sale_info_model.retail_price
            else None,
        )

    if book_model.access_info:
        access_info_model = book_model.access_info
        book_data.access_info = BookAccess(
            country=access_info_model.country,
            viewability=access_info_model.viewability,
            embeddable=access_info_model.embeddable,
            public_domain=access_info_model.public_domain,
            epub_available=(
                access_info_model.epub.isAvailable if access_info_model.epub else None
            ),
            epub_token_link=(
                access_info_model.epub.acsTokenLink if access_info_model.epub else None
            ),
            pdf_available=(
                access_info_model.pdf.isAvailable if access_info_model.pdf else None
            ),
            pdf_token_link=(
                access_info_model.pdf.acsTokenLink if access_info_model.pdf else None
            ),
            web_reader_link=access_info_model.web_reader_link,
        )

    identifiers: List[BookIdentifier] = []
    for book_identifier_model in book_model.volume_info.industryIdentifiers or []:
        identifier = BookIdentifier(
            identifier_type=book_identifier_model.type.value,
            identifier_value=book_identifier_model.identifier,
        )
        identifiers.append(identifier)
    book_data.identifiers = identifiers

    genres: List[Genre] = []
    for name in book_model.volume_info.categories or []:
        genre = get_genre_by_name(name, session)
        if not genre:
            genre = Genre(name=name)
            session.add(genre)
            session.flush()
        genres.append(genre)
    book_data.genres = genres

    session.add(book_data)
    db_manager.commit_or_raise(session)
    session.refresh(book_data)

    return book_data


def get_books_by_title(
    title: str, session: Session, limit: int = 100, offset: int = 0
) -> list[Book]:
    stmt = (
        select(Book)
        .where(Book.title == title)
        .order_by(Book.book_id)
        .limit(limit)
        .offset(offset)
    )
    return session.scalars(stmt).all()


def get_book_by_google_id(google_id: str, session: Session) -> None | Book:
    return session.query(Book).filter_by(google_books_id=google_id).first()


def update_book_by_model(book_replacement: BookModel, session: Session) -> bool:
    if book_replacement.book_id is None:
        raise ValueError(
            f"Cannot replace book without an ID. book_id: {book_replacement.book_id} - title:{book_replacement.volume_info.title}"
        )

    # book_record = session.query(Book).filter_by(id=book_replacement.book_id).first()
    book_record = get_book_by_book_id(book_replacement.book_id, session)

    if not book_record:
        return False

    book_record.google_books_id = book_replacement.google_books_id
    book_record.title = book_replacement.volume_info.title
    book_record.subtitle = book_replacement.volume_info.subtitle
    book_record.description = book_replacement.volume_info.description
    book_record.page_count = book_replacement.volume_info.page_count
    book_record.average_rating = book_replacement.volume_info.average_rating
    book_record.ratings_count = book_replacement.volume_info.ratings_count
    book_record.preview_link = book_replacement.volume_info.preview_link
    book_record.info_link = book_replacement.volume_info.info_link
    book_record.language = book_replacement.volume_info.language
    book_record.published_date = book_replacement.volume_info.published_date
    book_record.publisher_name = book_replacement.volume_info.publisher
    book_record.maturity_rating = book_replacement.volume_info.maturity_rating

    book_record.cover_image = (
        book_replacement.volume_info.image_links.thumbnail
        if book_replacement.volume_info.image_links
        else book_record.cover_image
    )

    book_record.authors.clear()
    for name in book_replacement.volume_info.authors or []:
        author = get_author_by_name(name, session)
        if not author:
            author = Author(name=name)
            session.add(author)
            session.flush()
            book_record.authors.append(author)
        book_record.authors.append(author)

    book_record.identifiers.clear()
    session.flush()
    for identifier_model in book_replacement.volume_info.industryIdentifiers or []:
        identifier = BookIdentifier(
            identifier_type=identifier_model.type.value,
            identifier_value=identifier_model.identifier,
        )
        book_record.identifiers.append(identifier)

    book_record.genres.clear()
    for name in book_replacement.volume_info.categories or []:
        genre = get_genre_by_name(name, session)
        if not genre:
            genre = Genre(name=name)
            session.add(genre)
            session.flush()
        book_record.genres.append(genre)

    sale_info_model = book_replacement.sale_info
    if sale_info_model:
        if book_record.book_sale_info:
            book_record.book_sale_info.country = sale_info_model.country
            book_record.book_sale_info.saleability = sale_info_model.saleability
            book_record.book_sale_info.is_ebook = sale_info_model.is_ebook
            book_record.book_sale_info.buy_link = sale_info_model.buy_link
            book_record.book_sale_info.list_price = (
                sale_info_model.list_price.amount
                if sale_info_model.list_price
                else None
            )
            book_record.book_sale_info.list_price_currency_code = (
                sale_info_model.list_price.currencyCode
                if sale_info_model.list_price
                else None
            )
            book_record.book_sale_info.retail_price = (
                sale_info_model.retail_price.amount
                if sale_info_model.retail_price
                else None
            )
            book_record.book_sale_info.retail_price_currency_code = (
                sale_info_model.retail_price.currencyCode
                if sale_info_model.retail_price
                else None
            )
        else:
            book_record.book_sale_info = BookSaleInfo(
                country=sale_info_model.country,
                saleability=sale_info_model.saleability,
                is_ebook=sale_info_model.is_ebook,
                buy_link=sale_info_model.buy_link,
                list_price=sale_info_model.list_price.amount
                if sale_info_model.list_price
                else None,
                list_price_currency_code=sale_info_model.list_price.currencyCode
                if sale_info_model.list_price
                else None,
                retail_price=sale_info_model.retail_price.amount
                if sale_info_model.retail_price
                else None,
                retail_price_currency_code=sale_info_model.retail_price.currencyCode
                if sale_info_model.retail_price
                else None,
            )
    db_manager.commit_or_raise(session)
    session.refresh(book_record)
    return True


def delete_book_by_book_id(book_id: int, session: Session) -> bool:
    book = get_book_by_book_id(book_id, session)

    if not book:
        return False

    session.delete(book)
    db_manager.commit_or_raise(session)
    return True
