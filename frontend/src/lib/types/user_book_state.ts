export type ReadingStatus =
  | "want_to_read"
  | "reading"
  | "completed"
  | "abandoned";

export interface UserBookStateModel {
  id: number | null;
  user_id: number;
  book_id: number;
  reading_status: ReadingStatus;
  current_page: number;
  percent_complete: number;
  started_at: string | null;
  finished_at: string | null;
}

export interface GetUserBookStatesByUserIdRequest {
  user_id: number;
  limit: number;
  offset: number;
}

export interface GetUserBookStateByUserAndBookRequest {
  user_id: number;
  book_id: number;
}
