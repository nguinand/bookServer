import type { ApiClient } from "./client";
import type {
  AdminLogsModel,
  GetAdminLogsRequest,
  GetAdminLogsResponse,
} from "$lib/types/admin_log";
import type { DeleteResponse } from "$lib/types/common";

export function makeAdminLogsApi(client: ApiClient) {
  return {
    create: (body: AdminLogsModel) =>
      client.post<AdminLogsModel>("/admin_logs/create_admin_logs/", body),

    getById: (admin_log_id: number) =>
      client.get<AdminLogsModel>(
        `/admin_logs/get_admin_logs_by_id/${admin_log_id}`,
      ),

    list: (body: GetAdminLogsRequest) =>
      client.post<GetAdminLogsResponse>("/admin_logs/get_admin_logs/", body),

    update: (body: AdminLogsModel) =>
      client.put<AdminLogsModel>("/admin_logs/update_admin_logs/", body),

    delete: (admin_log_id: number) =>
      client.delete<DeleteResponse<"admin_log_id">>(
        `/admin_logs/delete_admin_logs/${admin_log_id}`,
      ),
  };
}

export type AdminLogsApi = ReturnType<typeof makeAdminLogsApi>;
