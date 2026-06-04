export interface UserBookAttributesModel {
  id: number | null;
  user_id: number;
  book_id: number;
  rating: number;
  review_text: string | null;
  created_at: string | null;
  updated_at: string | null;
}
