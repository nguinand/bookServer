export type AdminEventType =
  | "create"
  | "update"
  | "delete"
  | "login"
  | "logout"
  | "modify";

export interface AdminLogsModel {
  id: number | null;
  event_type: AdminEventType;
  event_description: string;
  created_at: string;
}

export interface GetAdminLogsRequest {
  start_time: string;
  end_time: string;
  limit: number;
  offset: number;
}

export interface GetAdminLogsResponse {
  logs: AdminLogsModel[];
  limit: number;
  offset: number;
  count: number;
  total: number;
}
