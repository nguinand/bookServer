import type { ApiClient } from "./client";
import type { AuthorModel } from "$lib/types/author";
import type { DeleteResponse } from "$lib/types/common";

export function makeAuthorApi(client: ApiClient) {
  return {
    create: (body: AuthorModel) =>
      client.post<AuthorModel>("/author/create_author/", body),

    getById: (author_id: number) =>
      client.get<AuthorModel>(`/author/get_author_by_id/${author_id}`),

    getByName: (name: string) =>
      client.get<AuthorModel>("/author/get_author_by_name/", {
        query: { name },
      }),

    update: (body: AuthorModel) =>
      client.put<AuthorModel>("/author/update_author/", body),

    delete: (author_id: number) =>
      client.delete<DeleteResponse<"author_id">>(
        `/author/delete_author_by_id/${author_id}`,
      ),
  };
}

export type AuthorApi = ReturnType<typeof makeAuthorApi>;
