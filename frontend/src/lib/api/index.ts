import { ApiClient, type Fetch } from "./client";
import { makeAdminLogsApi } from "./admin_logs";
import { makeAuthorApi } from "./author";
import { makeAvatarApi } from "./avatar";
import { makeBookAccessApi } from "./book_access";
import { makeBookSaleInfoApi } from "./book_sale_info";
import { makeBookcaseApi } from "./bookcase";
import { makeBooksApi } from "./books";
import { makeGenreApi } from "./genre";
import { makeUserBookAttributesApi } from "./user_book_attributes";
import { makeUserBookStateApi } from "./user_book_state";
import { makeUserStatusApi } from "./user_status";
import { makeUsersApi } from "./users";

export { ApiClient, ApiError } from "./client";
export type { Fetch, Query, QueryValue, RequestOptions } from "./client";

export function makeApi(fetch: Fetch, jwt?: string) {
  const client = new ApiClient(fetch, jwt);
  return {
    client,
    admin_logs: makeAdminLogsApi(client),
    author: makeAuthorApi(client),
    avatar: makeAvatarApi(client),
    book_access: makeBookAccessApi(client),
    book_sale_info: makeBookSaleInfoApi(client),
    bookcase: makeBookcaseApi(client),
    books: makeBooksApi(client),
    genre: makeGenreApi(client),
    user_book_attributes: makeUserBookAttributesApi(client),
    user_book_state: makeUserBookStateApi(client),
    user_status: makeUserStatusApi(client),
    users: makeUsersApi(client),
  };
}

export type Api = ReturnType<typeof makeApi>;
