import type { ApiClient } from "./client";
import type { DeleteResponse } from "$lib/types/common";
import type {
  GetUserBookStateByUserAndBookRequest,
  GetUserBookStatesByUserIdRequest,
  UserBookStateModel,
} from "$lib/types/user_book_state";

export function makeUserBookStateApi(client: ApiClient) {
  return {
    create: (body: UserBookStateModel) =>
      client.post<UserBookStateModel>(
        "/user_book_state/create_user_book_state/",
        body,
      ),

    getById: (user_book_state_id: number) =>
      client.get<UserBookStateModel>(
        `/user_book_state/get_user_book_state_by_id/${user_book_state_id}`,
      ),

    listByUser: (body: GetUserBookStatesByUserIdRequest) =>
      client.post<UserBookStateModel[]>(
        "/user_book_state/get_user_book_states_by_user_id/",
        body,
      ),

    getByUserAndBook: (body: GetUserBookStateByUserAndBookRequest) =>
      client.post<UserBookStateModel>(
        "/user_book_state/get_user_book_state_by_user_and_book/",
        body,
      ),

    update: (body: UserBookStateModel) =>
      client.put<UserBookStateModel>(
        "/user_book_state/update_user_book_state/",
        body,
      ),

    delete: (user_book_state_id: number) =>
      client.delete<DeleteResponse<"user_book_state_id">>(
        `/user_book_state/delete_user_book_state_by_id/${user_book_state_id}`,
      ),
  };
}

export type UserBookStateApi = ReturnType<typeof makeUserBookStateApi>;
