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
  is_ebook: boolean;
  list_price: PriceModel | null;
  retail_price: PriceModel | null;
  buy_link: string | null;
}
