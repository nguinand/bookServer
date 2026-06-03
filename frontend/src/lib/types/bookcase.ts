import type { BookModel } from "./book";

export interface BookcaseModel {
  id: number | null;
  user_id: number;
  name: string;
  created_at: string;
  books: BookModel[];
}
