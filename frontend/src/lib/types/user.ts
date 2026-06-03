export type UserRole = "user" | "admin";

export interface UserModel {
  id: number | null;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  role: UserRole;
  avatar_id: number | null;
  status_id: number | null;
  created_at: string;
  last_login: string | null;
}

export interface CreateUserModelInput {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  role: "user";
}

export interface UserLoginRequest {
  username: string;
  password: string;
}

export interface AuthenticationStatusResponse {
  user_id: number;
  username: string;
  authenticated: boolean;
  details: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CreateUserRequest {
  user_model: CreateUserModelInput;
  password: string;
}

export interface UpdateUserRequest {
  user_model: UserModel;
}

export interface PasswordUpdateRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordUpdateResponse {
  user_id: number;
  updated: boolean;
  details: string;
}
