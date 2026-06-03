import type { ApiClient } from "./client";
import type { DeleteResponse, DetailResponse } from "$lib/types/common";
import type { UserBookAttributesModel } from "$lib/types/user_book_attributes";

export function makeUserBookAttributesApi(client: ApiClient) {
  return {
    create: (body: UserBookAttributesModel) =>
      client.post<UserBookAttributesModel>(
        "/user_book_attributes/create_user_book_attribute/",
        body,
      ),

    // Backend path quirk: this endpoint is mounted at /api/update_book_attribute
    // (no trailing slash, no /user_book_attributes prefix).
    update: (body: UserBookAttributesModel) =>
      client.post<DetailResponse>("/update_book_attribute", body),

    delete: (attribute_id: number) =>
      client.delete<DeleteResponse<"attribute_id">>(
        `/user_book_attributes/delete_user_book_attribute/${attribute_id}`,
      ),

    getById: (attribute_id: number) =>
      client.get<UserBookAttributesModel>(
        `/user_book_attributes/book_attribute_by_id/${attribute_id}`,
      ),

    listByUser: (
      user_id: number,
      params: { limit?: number; offset?: number } = {},
    ) =>
      client.get<UserBookAttributesModel[]>(
        "/user_book_attributes/book_attribute_by_user_id/",
        { query: { user_id, ...params } },
      ),

    listByBook: (book_id: number) =>
      client.get<UserBookAttributesModel[]>(
        "/user_book_attributes/book_attribute_by_book_id/",
        { query: { book_id } },
      ),

    listByBookAndUser: (book_id: number, user_id: number) =>
      client.get<UserBookAttributesModel[]>(
        "/user_book_attributes/book_attribute_by_book_and_user_id/",
        { query: { book_id, user_id } },
      ),
  };
}

export type UserBookAttributesApi = ReturnType<
  typeof makeUserBookAttributesApi
>;
