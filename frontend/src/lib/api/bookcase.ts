import type { ApiClient } from "./client";
import type { BookcaseModel } from "$lib/types/bookcase";
import type { DeleteResponse, DetailResponse } from "$lib/types/common";

export function makeBookcaseApi(client: ApiClient) {
  return {
    create: (body: BookcaseModel) =>
      client.post<BookcaseModel>("/database/create_bookcase/", body),

    getById: (bookcase_id: number) =>
      client.get<BookcaseModel>(`/database/bookcase_by_id/${bookcase_id}`),

    listByUser: (
      user_id: number,
      params: { limit?: number; offset?: number } = {},
    ) =>
      client.get<BookcaseModel[]>("/database/bookcases_by_user_id/", {
        query: { user_id, ...params },
      }),

    update: (body: BookcaseModel) =>
      client.post<DetailResponse>("/database/update_bookcase/", body),

    delete: (bookcase_id: number) =>
      client.delete<DeleteResponse<"bookcase_id">>(
        `/database/delete_bookcase/${bookcase_id}`,
      ),
  };
}

export type BookcaseApi = ReturnType<typeof makeBookcaseApi>;
