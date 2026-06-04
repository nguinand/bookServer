export interface DetailResponse {
  detail: string;
}

export type DeleteResponse<K extends string = string> = {
  deleted: boolean;
} & Record<K, number>;

export interface DatabaseErrorResponse {
  detail: string;
  error_id: string;
}
