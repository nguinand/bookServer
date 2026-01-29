from typing import List
from app.crud.author_crud import get_authors_by_name, resolve_author
from app.crud.genre_crud import get_genre_by_name
from app.db.db_models.author import Author
from app.db.db_models.book_access import BookAccess
from app.db.db_models.book_identifier import BookIdentifier
from app.db.db_models.book_sale_info import BookSaleInfo
from app.db.db_models.genre import Genre
from app.models.access_info import AccessInfoModel, FormatInfoModel
from app.models.book import BookModel
from app.db.db_models import Book
from app.models.book_sale_info import BookSaleInfoModel, PriceModel
from app.models.identifiers import IdentifierType, IndustryIdentifier
from sqlalchemy.orm import Session

from app.models.volume_info import ImageLinksModel, VolumeInfoModel


def create_book(book_model: BookModel, session: Session) -> Book:
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
        author = resolve_author(name, book_model.volume_info.title, session)
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
    session.commit()

    return book_data


def get_books_by_title(title: str, session: Session) -> list[Book]:
    return session.query(Book).filter_by(title=title).all()


def get_book_by_google_id(google_id: str, session: Session) -> None | Book:
    return session.query(Book).filter_by(google_id=google_id).first()


def get_book_by_id(id: int, session: Session) -> None | Book:
    return session.query(Book).filter_by(id=id).first()


def update_book(book_replacement: BookModel, session: Session) -> None | Book:
    if book_replacement.id is None:
        raise ValueError(
            f"Cannot replace book without an ID. {book_replacement.id} - {book_replacement.volume_info.title}"
        )

    book_record = get_book_by_id(book_replacement.id, session)

    if not book_record:
        return None

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

    # authors is a list[str] -> ["auth1", "auth2"]
    for name in book_replacement.volume_info.authors or []:
        author = get_authors_by_name(name, session)
        if not author:
            author = Author(name=name)
            session.add(author)
            session.flush()
        book_record.authors.append(author)

    book_record.identifiers.clear()
    for identifier_model in book_replacement.volume_info.industryIdentifiers or []:
        identifier = BookIdentifier(
            identifier_type=identifier_model.type.value,
            identifier_value=identifier_model.identifier,
            book=book_record,
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

    session.commit()
    session.refresh(book_record)
    return book_record


def delete_book(book_id: int, session: Session) -> bool:
    book = get_book_by_id(book_id, session)

    if not book:
        return False

    session.delete(book)
    session.commit()
    return True


def convert_book_to_model(book: Book) -> BookModel:
    volume_info = VolumeInfoModel(
        title=book.title,
        subtitle=book.subtitle,
        authors=[author.name for author in book.authors],
        publisher=book.publisher_name,
        publishedDate=book.published_date,
        description=book.description,
        pageCount=book.page_count,
        categories=[genre.name for genre in book.genres],
        averageRating=book.average_rating,
        ratingsCount=book.ratings_count,
        imageLinks=ImageLinksModel(thumbnail=book.cover_image, smallThumbnail=None)
        if book.cover_image
        else None,
        previewLink=book.preview_link,
        infoLink=book.info_link,
        language=book.language,
        industryIdentifiers=[
            IndustryIdentifier(
                type=IdentifierType(identifier.identifier_type),
                identifier=identifier.identifier_value,
            )
            for identifier in book.identifiers
        ],
        maturity_rating=book.maturity_rating,
    )
    sale_info = None
    if book.book_sale_info:
        sale_info = BookSaleInfoModel(
            book_id=book.id,
            country=book.book_sale_info.country,
            saleability=book.book_sale_info.saleability,
            isEbook=book.book_sale_info.is_ebook,
            listPrice=PriceModel(
                amount=book.book_sale_info.list_price,
                currencyCode=book.book_sale_info.list_price_currency_code,
            ),
            retailPrice=PriceModel(
                amount=book.book_sale_info.retail_price,
                currencyCode=book.book_sale_info.retail_price_currency_code,
            )
            if book.book_sale_info.retail_price is not None
            else None,
            buyLink=book.book_sale_info.buy_link,
        )

    access_info = None
    if book.access_info:
        access_info = AccessInfoModel(
            country=book.access_info.country,
            viewability=book.access_info.viewability,
            embeddable=book.access_info.embeddable,
            publicDomain=book.access_info.public_domain,
            epub=FormatInfoModel(
                isAvailable=book.access_info.epub_available,
                acsTokenLink=book.access_info.epub_token_link,
            ),
            pdf=FormatInfoModel(
                isAvailable=book.access_info.pdf_available,
                acsTokenLink=book.access_info.pdf_token_link,
            ),
            webReaderLink=book.access_info.web_reader_link,
        )

    return BookModel(
        id=book.id,
        google_books_id=book.google_books_id,
        volumeInfo=volume_info,
        saleInfo=sale_info,
        accessInfo=access_info,
    )
