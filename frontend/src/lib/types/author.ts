import type { BookModel } from "./book";

export interface AuthorModel {
  id: number | null;
  bio: string | null;
  name: string;
  books: BookModel[];
}
