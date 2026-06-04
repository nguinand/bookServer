import type { ApiClient } from "./client";
import type {
  AccessInfoModel,
  CreateAccessInfoRequest,
  UpdateAccessInfoRequest,
} from "$lib/types/access_info";
import type { DeleteResponse } from "$lib/types/common";

export function makeBookAccessApi(client: ApiClient) {
  return {
    create: (body: CreateAccessInfoRequest) =>
      client.post<AccessInfoModel>("/book_access/create_access_info/", body),

    getById: (access_info_id: number) =>
      client.get<AccessInfoModel>(
        `/book_access/get_access_info_by_id/${access_info_id}`,
      ),

    getByBookId: (book_id: number) =>
      client.get<AccessInfoModel>(
        `/book_access/get_access_info_by_book_id/${book_id}`,
      ),

    update: (body: UpdateAccessInfoRequest) =>
      client.put<AccessInfoModel>("/book_access/update_access_info/", body),

    delete: (book_access_id: number) =>
      client.delete<DeleteResponse<"book_access_id">>(
        `/book_access/delete_access_info/${book_access_id}`,
      ),
  };
}

export type BookAccessApi = ReturnType<typeof makeBookAccessApi>;
