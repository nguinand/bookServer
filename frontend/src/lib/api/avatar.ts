import type { ApiClient } from "./client";
import type { AvatarModel } from "$lib/types/avatar";
import type { DeleteResponse } from "$lib/types/common";

export function makeAvatarApi(client: ApiClient) {
  return {
    create: (body: AvatarModel) =>
      client.post<AvatarModel>("/avatar/create_avatar/", body),

    getById: (avatar_id: number) =>
      client.get<AvatarModel>(`/avatar/get_avatar_by_id/${avatar_id}`),

    update: (body: AvatarModel) =>
      client.put<AvatarModel>("/avatar/update_avatar/", body),

    delete: (avatar_id: number) =>
      client.delete<DeleteResponse<"avatar_id">>(
        `/avatar/delete_avatar/${avatar_id}`,
      ),
  };
}

export type AvatarApi = ReturnType<typeof makeAvatarApi>;
