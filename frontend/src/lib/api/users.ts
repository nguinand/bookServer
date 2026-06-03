import type { ApiClient } from "./client";
import type { DeleteResponse } from "$lib/types/common";
import type {
  AuthenticationStatusResponse,
  CreateUserRequest,
  PasswordUpdateRequest,
  PasswordUpdateResponse,
  TokenResponse,
  UpdateUserRequest,
  UserLoginRequest,
  UserModel,
} from "$lib/types/user";

export function makeUsersApi(client: ApiClient) {
  return {
    authenticate: (body: UserLoginRequest) =>
      client.post<AuthenticationStatusResponse>(
        "/authenticate/authenticate_user/",
        body,
      ),

    login: (body: UserLoginRequest) =>
      client.post<TokenResponse>("/authenticate/token/", body),

    updatePassword: (body: PasswordUpdateRequest) =>
      client.post<PasswordUpdateResponse>(
        "/authenticate/update_user_password/",
        body,
      ),

    create: (body: CreateUserRequest) =>
      client.post<UserModel>("/database/create_user/", body),

    getByEmail: (email: string) =>
      client.get<UserModel>(
        `/database/users_by_email/${encodeURIComponent(email)}`,
      ),

    getByUsername: (username: string) =>
      client.get<UserModel>(
        `/database/users_by_username/${encodeURIComponent(username)}`,
      ),

    getById: (user_id: number) =>
      client.get<UserModel>(`/database/user_by_id/${user_id}`),

    update: (body: UpdateUserRequest) =>
      client.put<UserModel>("/database/update_user/", body),

    delete: (user_id: number) =>
      client.delete<DeleteResponse<"user_id">>(
        `/database/delete_user/${user_id}`,
      ),
  };
}

export type UsersApi = ReturnType<typeof makeUsersApi>;
