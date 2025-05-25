from app.crud.author_crud import AuthorCrud
from app.db.db_models.author import Author
from app.db.db_models.book_access import BookAccess
from app.db.db_models.book_identifier import BookIdentifier
from app.db.db_models.book_sale_info import BookSaleInfo
from app.db.db_models.genre import Genre
from app.models.author import AuthorModel
from app.models.book import BookModel
from app.db.db_models import Book
from app.models.user_book_attributes import UserBookAttributesModel
from sqlalchemy.orm import Session


class BookCrud:
    def create_book(self, book_model: BookModel, session: Session) -> Book:
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

        author_names = book_model.volume_info.authors or []
        book_authors = []
        for name in author_names:
            author = AuthorCrud().get_author_by_name(name, session)
            if not author:
                author = Author(name=name)
                session.add(author)
                session.flush()
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
                public_domain=access_info_model.publicDomain,
                epub_available=access_info_model.epub.isAvailable
                if access_info_model.epub
                else None,
                pdf_available=access_info_model.pdf.isAvailable
                if access_info_model.pdf
                else None,
                web_reader_link=access_info_model.web_reader_link,
            )

        identifiers = []
        for book_identifier_model in book_model.volume_info.industryIdentifiers or []:
            identifer = BookIdentifier(
                identifier_type=book_identifier_model.type.value,
                identifier_value=book_identifier_model.identifier,
            )
            identifiers.append(identifer)
        book_data.identifiers = identifiers

        genres = []
        for name in book_model.volume_info.categories or []:
            genre = session.query(Genre).filter_by(name=name).first()
            if not genre:
                genre = Genre(name=name)
                session.add(genre)
                session.flush()
            genres.append(genre)
        book_data.genres = genres

        session.add(book_data)
        session.commit()

        return book_data

    def get_books_by_title(self, name: str, session: Session) -> list[Book]: 
        book_records = session.query(Book).filter_by(title=name).all()
        return book_records
    
    def get_book_by_google_id(self, name: str, session: Session) -> list[Book]: 
        book_record = session.query(Book).filter_by(google_books_id=name).first()
        return book_record
    
    def get_book_by_id(self, id: int, session: Session) -> Book: 
        book_record = session.query(Book).filter_by(id=id).first()
        return book_record

    def update_book(
        self, book_replacement: BookModel, session: Session
    ) -> None | Book: ...

    def delete_book(self, book_id: int, session: Session) -> bool: ...
