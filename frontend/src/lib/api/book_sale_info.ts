import type { ApiClient } from "./client";
import type { BookSaleInfoModel } from "$lib/types/book_sale_info";
import type { DeleteResponse } from "$lib/types/common";

export function makeBookSaleInfoApi(client: ApiClient) {
  return {
    create: (body: BookSaleInfoModel) =>
      client.post<BookSaleInfoModel>(
        "/book_sale_info/create_book_sale_info/",
        body,
      ),

    getById: (book_sale_info_id: number) =>
      client.get<BookSaleInfoModel>(
        `/book_sale_info/get_book_sale_info_by_id/${book_sale_info_id}`,
      ),

    update: (body: BookSaleInfoModel) =>
      client.put<BookSaleInfoModel>(
        "/book_sale_info/update_book_sale_info/",
        body,
      ),

    delete: (book_sale_info_id: number) =>
      client.delete<DeleteResponse<"book_sale_info_id">>(
        `/book_sale_info/delete_book_sale_info/${book_sale_info_id}`,
      ),
  };
}

export type BookSaleInfoApi = ReturnType<typeof makeBookSaleInfoApi>;
