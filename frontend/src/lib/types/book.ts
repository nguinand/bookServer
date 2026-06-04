import type { AccessInfoModel } from "./access_info";
import type { BookSaleInfoModel } from "./book_sale_info";
import type { VolumeInfoModel } from "./volume_info";

export interface BookModel {
  book_id: number | null;
  id: string; // google_books_id
  volumeInfo: VolumeInfoModel; // volume_info
  saleInfo: BookSaleInfoModel | null; // sale_info
  accessInfo: AccessInfoModel | null; // access_info
}
