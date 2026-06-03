import type { ApiClient } from "./client";
import type { DeleteResponse } from "$lib/types/common";
import type { GenreModel } from "$lib/types/genre";

export function makeGenreApi(client: ApiClient) {
  return {
    create: (body: GenreModel) =>
      client.post<GenreModel>("/genre/create_genre/", body),

    getById: (genre_id: number) =>
      client.get<GenreModel>(`/genre/get_genre_by_id/${genre_id}`),

    getByName: (name: string) =>
      client.get<GenreModel>("/genre/get_genre_by_name/", { query: { name } }),

    update: (body: GenreModel) =>
      client.put<GenreModel>("/genre/update_genre/", body),

    delete: (genre_id: number) =>
      client.delete<DeleteResponse<"genre_id">>(
        `/genre/delete_genre/${genre_id}`,
      ),
  };
}

export type GenreApi = ReturnType<typeof makeGenreApi>;
