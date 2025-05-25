from app.db.db_models.book_sale_info import BookSaleInfo
from app.models.book_sale_info import BookSaleInfoModel, CurrencyCode, PriceModel
from sqlalchemy.orm import Session


class BookSaleInfoCrud:
    def create_book_sale_info(
        self, book_sale_info_model: BookSaleInfoModel, session: Session
    ) -> BookSaleInfo:
        book_sale_info_data = BookSaleInfo(
            book_id=book_sale_info_model.book_id,
            country=book_sale_info_model.country,
            saleability=book_sale_info_model.saleability,
            is_ebook=book_sale_info_model.is_ebook,
        )

        # list_price and retail_price are both related to the PriceModel pydantic model. We need to invidually extract their values.

        if book_sale_info_model.list_price is not None:
            book_sale_info_data.list_price = book_sale_info_model.list_price.amount
            book_sale_info_data.list_price_currency_code = (
                book_sale_info_model.list_price.currencyCode
            )

        if book_sale_info_model.retail_price is not None:
            book_sale_info_data.retail_price = book_sale_info_model.retail_price.amount
            book_sale_info_data.retail_price_currency_code = (
                book_sale_info_model.retail_price.currencyCode
            )

        session.add(book_sale_info_data)
        session.commit()
        session.refresh(book_sale_info_data)

        return book_sale_info_data

    def get_book_sale_info_by_id(
        self, id: int, session: Session
    ) -> BookSaleInfo | None:
        book_sale_info_record = session.query(BookSaleInfo).filter_by(id=id).first()
        try:
            return book_sale_info_record
        except AttributeError as e:
            print(e)
            return None

    def update_book_sale_info(
        self, book_sale_info_replacement: BookSaleInfoModel, session: Session
    ) -> None | BookSaleInfo:
        if book_sale_info_replacement.id is None:
            raise ValueError(
                f"Cannot replace a book sale info record without an ID. {book_sale_info_replacement.id}"
            )

        book_sale_info_record = (
            session.query(BookSaleInfo)
            .filter_by(id=book_sale_info_replacement.id)
            .first()
        )

        if not book_sale_info_record:
            return None

        book_sale_info_record.id = book_sale_info_replacement.id
        book_sale_info_record.book_id = book_sale_info_replacement.book_id
        book_sale_info_record.country = book_sale_info_replacement.country
        book_sale_info_record.saleability = book_sale_info_replacement.saleability
        book_sale_info_record.is_ebook = book_sale_info_replacement.is_ebook
        book_sale_info_record.buy_link = book_sale_info_replacement.buy_link

        if book_sale_info_replacement.list_price is not None:
            book_sale_info_record.list_price = (
                book_sale_info_replacement.list_price.amount
            )
            book_sale_info_record.list_price_currency_code = (
                book_sale_info_replacement.list_price.currencyCode
            )

        if book_sale_info_replacement.retail_price is not None:
            book_sale_info_record.retail_price = (
                book_sale_info_replacement.retail_price.amount
            )
            book_sale_info_record.retail_price_currency_code = (
                book_sale_info_replacement.retail_price.currencyCode
            )

        session.commit()
        return book_sale_info_record

    def delete_book_sale_info(self, book_sale_info_id: int, session: Session) -> bool:
        book_sale_info = (
            session.query(BookSaleInfo).filter_by(id=book_sale_info_id).first()
        )

        if not book_sale_info:
            return False

        session.delete(book_sale_info)
        session.commit()
        return True

    def convert_book_sale_info(
        self, book_sale_info_data: BookSaleInfo
    ) -> BookSaleInfoModel:
        converted_book_sale_info = BookSaleInfoModel(
            id=book_sale_info_data.id,
            book_id=book_sale_info_data.book_id,
            buyLink=book_sale_info_data.buy_link,
            country=book_sale_info_data.country,
            isEbook=book_sale_info_data.is_ebook,
            saleability=book_sale_info_data.saleability,
            listPrice=PriceModel(
                amount=book_sale_info_data.list_price,
                currencyCode=CurrencyCode(book_sale_info_data.list_price_currency_code)
                if book_sale_info_data.list_price_currency_code
                else None,
            ),
            retailPrice=PriceModel(
                amount=book_sale_info_data.retail_price,
                currencyCode=CurrencyCode(
                    book_sale_info_data.retail_price_currency_code
                )
                if book_sale_info_data.retail_price_currency_code
                else None,
            ),
        )

        return converted_book_sale_info
