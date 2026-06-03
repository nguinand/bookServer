import type { AccessInfoModel } from "./access_info";
import type { BookSaleInfoModel } from "./book_sale_info";
import type { VolumeInfoModel } from "./volume_info";

export interface BookModel {
  book_id: number | null;
  google_books_id: string;
  volume_info: VolumeInfoModel;
  sale_info: BookSaleInfoModel | null;
  access_info: AccessInfoModel | null;
}
