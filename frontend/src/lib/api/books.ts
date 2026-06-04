import type { ApiClient } from "./client";
import type { BookModel } from "$lib/types/book";
import type { DeleteResponse, DetailResponse } from "$lib/types/common";

export type SearchType = "author" | "publisher" | "isbn" | "subject";

export interface PaginationParams {
  max_results?: number;
  start_index?: number;
}

export function makeBooksApi(client: ApiClient) {
  return {
    // ---- external (Google Books proxy) ----
    searchByName: (book_name: string, params: PaginationParams = {}) =>
      client.get<BookModel[]>("/books/name/", {
        query: { book_name, ...params },
      }),

    searchByIsbn: (isbn: number, params: PaginationParams = {}) =>
      client.get<BookModel[]>("/books/books_by_isbn/", {
        query: { isbn, ...params },
      }),

    searchGeneric: (
      search_type: SearchType,
      val: string,
      params: PaginationParams = {},
    ) =>
      client.get<BookModel[]>("/books/generic/", {
        query: { search_type, val, ...params },
      }),

    recommendationsByAuthor: (author: string, params: PaginationParams = {}) =>
      client.get<BookModel[]>("/books/recommendations/by_author/", {
        query: { author, ...params },
      }),

    recommendationsByGenre: (
      genre_name: string,
      params: PaginationParams = {},
    ) =>
      client.get<BookModel[]>("/books/recommendations/by_genre/", {
        query: { genre_name, ...params },
      }),

    recommendationsByBookshelfGenre: (params: PaginationParams = {}) =>
      client.get<BookModel[]>("/books/recommendations/by_bookshelf_genre/", {
        query: { ...params },
      }),

    // ---- internal (DB) ----
    create: (body: BookModel) =>
      client.post<BookModel>("/database/create_book/", body),

    update: (body: BookModel) =>
      client.post<DetailResponse>("/database/update_book/", body),

    delete: (book_id: number) =>
      client.delete<DeleteResponse<"book_id">>(
        `/database/delete_book/${book_id}`,
      ),

    getByTitle: (
      title: string,
      query: { limit?: number; offset?: number } = {},
    ) =>
      client.get<BookModel[]>("/database/books_by_title/", {
        query: { title, ...query },
      }),

    getByGoogleId: (google_id: string) =>
      client.get<BookModel>(
        `/database/books_by_google_id/${encodeURIComponent(google_id)}`,
      ),

    getById: (book_id: number) =>
      client.get<BookModel>(`/database/books_by_book_id/${book_id}`),
  };
}

export type BooksApi = ReturnType<typeof makeBooksApi>;
