import type { ApiClient } from "./client";
import type { DeleteResponse } from "$lib/types/common";
import type { UserStatusModel } from "$lib/types/user_status";

export function makeUserStatusApi(client: ApiClient) {
  return {
    create: (body: UserStatusModel) =>
      client.post<UserStatusModel>("/user_status/create_user_status/", body),

    getById: (status_id: number) =>
      client.get<UserStatusModel>(
        `/user_status/get_user_status_by_id/${status_id}`,
      ),

    update: (body: UserStatusModel) =>
      client.put<UserStatusModel>("/user_status/update_user_status/", body),

    delete: (status_id: number) =>
      client.delete<DeleteResponse<"status_id">>(
        `/user_status/delete_user_status/${status_id}`,
      ),
  };
}

export type UserStatusApi = ReturnType<typeof makeUserStatusApi>;
