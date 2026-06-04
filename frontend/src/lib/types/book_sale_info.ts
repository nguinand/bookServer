export type CurrencyCode = "USD" | "EUR" | "GBP" | "JPY" | "INR";

export interface PriceModel {
  amount: string | null;
  currencyCode: CurrencyCode | null;
}

export interface BookSaleInfoModel {
  id: number | null;
  book_id: number | null;
  country: string | null;
  saleability: string | null;
  isEbook: boolean; // is_ebook
  listPrice: PriceModel | null; // list_price
  retailPrice: PriceModel | null; // retail_price
  buyLink: string | null; // buy_link
}
