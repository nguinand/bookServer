
from app.db.db_models import Book
from app.models.access_info import AccessInfoModel, FormatInfoModel
from app.models.book import BookModel
from app.models.book_sale_info import BookSaleInfoModel, PriceModel
from app.models.identifiers import IdentifierType, IndustryIdentifier
from app.models.volume_info import ImageLinksModel, VolumeInfoModel





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
            book_id=book.book_id,
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
        id=book.google_books_id,
        volumeInfo=volume_info,
        saleInfo=sale_info,
        accessInfo=access_info,
    )
