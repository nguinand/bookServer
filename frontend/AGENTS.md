# Frontend — bookServer

The web UI for [bookServer](../README.md), a personal book library / reading-tracker. The backend is the FastAPI app in `../app/`; this directory is the SvelteKit client that consumes it.

This file is the source of truth for **how the frontend is built**. Codex agents
and humans should be able to ship a feature without reading the backend Python
or hunting through Svelte/Skeleton docs.

---

## 1. Tech stack

| Layer            | Choice                                  | Notes                                                |
| ---------------- | --------------------------------------- | ---------------------------------------------------- |
| Framework        | **SvelteKit** (latest)                  | File-based routing, load functions, SSR.             |
| Language         | **Svelte 5** + **TypeScript** (strict)  | Runes everywhere. No legacy `export let` / `$:`.     |
| UI kit           | **Skeleton v3** (`@skeletonlabs/skeleton-svelte`) | Themed Tailwind components.                |
| Styling          | **Tailwind CSS** (per Skeleton pin)     | Skeleton drives the theme; raw Tailwind for the gap. |
| Forms/validation | **Zod**                                 | Schemas mirror backend Pydantic models.              |
| Tests            | **Vitest** (unit) + **Playwright** (e2e) | MSW for mocking the API in tests.                   |
| Pkg manager      | **pnpm**                                | Use `pnpm`, not `npm`/`yarn`, in commands.           |

Backend is FastAPI 0.115+ / Pydantic 2 / Python 3.12 / MySQL — see `../pyproject.toml`.

---

## 2. Project structure

```
frontend/
├── src/
│   ├── routes/                         # File-based routes (URL = folder path)
│   │   ├── +layout.svelte              # Root layout — wraps every page
│   │   ├── +layout.server.ts           # Loads `user` from session cookie for every page
│   │   ├── +page.svelte                # / (home / dashboard)
│   │   ├── login/+page.svelte
│   │   ├── login/+page.server.ts       # Form action: POST creds → set cookie → redirect
│   │   ├── signup/...
│   │   ├── books/
│   │   │   ├── search/+page.svelte
│   │   │   └── [book_id]/+page.svelte  # Dynamic param — book detail
│   │   ├── bookcases/[id]/+page.svelte
│   │   └── profile/+page.svelte
│   ├── lib/
│   │   ├── api/                        # Typed API client — the ONLY place that calls the backend
│   │   │   ├── client.ts               # Base fetch wrapper (URL, auth header, errors)
│   │   │   ├── auth.ts                 # login / signup / changePassword
│   │   │   ├── books.ts                # search / detail / recommendations
│   │   │   ├── bookcases.ts
│   │   │   ├── userBookState.ts
│   │   │   └── ...                     # one module per backend router
│   │   ├── types/                      # TypeScript mirrors of backend Pydantic models
│   │   │   ├── user.ts
│   │   │   ├── book.ts
│   │   │   └── ...
│   │   ├── schemas/                    # Zod schemas for form validation
│   │   ├── stores/
│   │   │   └── auth.svelte.ts          # Reactive auth state (Svelte 5 class with $state)
│   │   ├── components/                 # Reusable Svelte components (PascalCase files)
│   │   │   ├── BookCard.svelte
│   │   │   └── ...
│   │   └── utils/                      # Pure helpers — date formatting, etc.
│   ├── hooks.server.ts                 # Reads JWT cookie → event.locals.user; gates /protected routes
│   ├── app.html                        # HTML template; <html data-theme="..."> for Skeleton
│   ├── app.css                         # Tailwind + Skeleton imports
│   └── app.d.ts                        # Type augmentations (App.Locals, App.PageData)
├── static/                             # Served as-is (favicon, robots.txt)
├── tests/                              # Playwright e2e tests
├── svelte.config.js
├── vite.config.ts
├── tailwind.config.ts                  # If using Tailwind v3; v4 uses CSS-only config
├── package.json
└── AGENTS.md                           # This file
```

**Import alias:** `$lib/...` → `src/lib/...`. Server-only code lives in `$lib/server/` and cannot be imported from client code (SvelteKit enforces this).

---

## 3. Backend API contract

### 3.1 Base URL & environment

- Local dev: `http://127.0.0.1:8000`
- All routes mounted under `/api` prefix
- Configure via `.env` in `frontend/`:
  ```
  PUBLIC_API_BASE_URL=http://127.0.0.1:8000
  ```
  Access in code via `import { PUBLIC_API_BASE_URL } from '$env/static/public'`. Server-only secrets go in `$env/static/private`.

### 3.2 CORS

CORS is configured in `../app/main.py` via `CORSMiddleware`. The allowed origin is built from two backend env vars:

- `FRONTEND_ENDPOINT` — host (with scheme), e.g. `http://localhost`
- `FRONTEND_PORT` — port, e.g. `5173`

These compose into a single allowed origin. If the SvelteKit dev server's origin doesn't match exactly (scheme + host + port), every browser request will fail CORS preflight — adjust the backend `.env` to match wherever Vite is actually serving from.

Server-side calls from SvelteKit `+page.server.ts` files do **not** hit CORS at all (they're server→server), so the recommended pattern (see §6) sidesteps this for most reads. CORS only matters for fetches that originate in the browser.

### 3.3 Authentication

**Scheme:** JWT bearer. Token lifetime 60 min (`ACCESS_TOKEN_EXPIRE_MINUTES` on backend).

**Login flow:**

1. `POST /api/authenticate/token/` with **JSON body** `{ "username": "...", "password": "..." }` (min 7 chars). _Note: this is NOT OAuth2 form-encoded despite the `/token/` name — the backend takes JSON `UserLoginRequest`._
2. Response: `{ "access_token": "<jwt>", "token_type": "bearer" }`
3. Store the JWT in an **httpOnly secure cookie** set by `/login/+page.server.ts` — never `localStorage` (XSS exfil risk).
4. Subsequent requests attach `Authorization: Bearer <jwt>`.

**Public endpoints (no token needed):**
- `POST /api/database/create_user/`
- `POST /api/authenticate/authenticate_user/` (validates creds, does not issue a token)
- `POST /api/authenticate/token/` (issues token)

**Everything else** requires the bearer header. The backend enforces owner-or-admin for user-owned resources; admin-only for `/api/admin_logs/...`.

**Expiry handling:** A 401 with `WWW-Authenticate: Bearer` means token expired or invalid. The client should clear the auth cookie and redirect to `/login`. Implement this centrally in `$lib/api/client.ts`, not per-call.

### 3.4 Endpoint reference

All paths prefixed with `/api`. `Req`/`Res` columns refer to TypeScript types in `$lib/types/` that mirror Pydantic models. Camel-cased query params come from the backend; keep them as-is in the client.

#### Auth — `/api/authenticate`, `/api/database/create_user`

| Method | Path                                | Req                     | Res                                |
| ------ | ----------------------------------- | ----------------------- | ---------------------------------- |
| POST   | `/database/create_user/`            | `CreateUserRequest`     | `UserModel`                        |
| POST   | `/authenticate/authenticate_user/`  | `UserLoginRequest`      | `AuthenticationStatusResponse`     |
| POST   | `/authenticate/token/`              | `UserLoginRequest`      | `TokenResponse`                    |
| POST   | `/authenticate/update_user_password/` | `PasswordUpdateRequest` | `PasswordUpdateResponse`         |

#### Users — `/api/database`

| Method | Path                                | Params/Body                | Res         |
| ------ | ----------------------------------- | -------------------------- | ----------- |
| GET    | `/database/users_by_email/{email}`  | path: email                | `UserModel` |
| GET    | `/database/users_by_username/{username}` | path: username        | `UserModel` |
| GET    | `/database/user_by_id/{user_id}`    | path: user_id              | `UserModel` |
| PUT    | `/database/update_user/`            | body: `UpdateUserRequest`  | `UserModel` |
| DELETE | `/database/delete_user/{user_id}`   | path: user_id              | `{user_id, deleted}` |

#### Books — external (Google Books proxy) — `/api/books`

All take `max_results` (default 10) and `start_index` (default 0) query params.

| Method | Path                                              | Required query           | Res             |
| ------ | ------------------------------------------------- | ------------------------ | --------------- |
| GET    | `/books/name/`                                    | `book_name`              | `BookModel[]`   |
| GET    | `/books/books_by_isbn/`                           | `isbn`                   | `BookModel[]`   |
| GET    | `/books/generic/`                                 | `search_type`, `val`     | `BookModel[]`   |
| GET    | `/books/recommendations/by_author/`               | `author`                 | `BookModel[]`   |
| GET    | `/books/recommendations/by_genre/`                | `genre_name`             | `BookModel[]`   |
| GET    | `/books/recommendations/by_bookshelf_genre/`      | (none beyond pagination) | `BookModel[]`   |

`search_type` ∈ `"author" | "publisher" | "isbn" | "subject"`.

#### Books — internal (DB) — `/api/database`

| Method | Path                                       | Params/Body         | Res                  |
| ------ | ------------------------------------------ | ------------------- | -------------------- |
| POST   | `/database/create_book/`                   | body: `BookModel` (input uses backend aliases — see §3.5) | `BookModel` |
| POST   | `/database/update_book/`                   | body: `BookModel`   | `{detail}`           |
| DELETE | `/database/delete_book/{book_id}`          | path                | `{book_id, deleted}` |
| GET    | `/database/books_by_title/`                | `title`, `limit`, `offset` | `BookModel[]` |
| GET    | `/database/books_by_google_id/{google_id}` | path                | `BookModel`          |
| GET    | `/database/books_by_book_id/{book_id}`     | path                | `BookModel`          |

#### Bookcases — `/api/database`

| Method | Path                                            | Body / Params       | Res                       |
| ------ | ----------------------------------------------- | ------------------- | ------------------------- |
| POST   | `/database/create_bookcase/`                    | `BookcaseModel`     | `BookcaseModel`           |
| POST   | `/database/update_bookcase/`                    | `BookcaseModel`     | `{detail}`                |
| DELETE | `/database/delete_bookcase/{bookcase_id}`       | path                | `{bookcase_id, deleted}`  |
| GET    | `/database/bookcase_by_id/{bookcase_id}`        | path                | `BookcaseModel`           |
| GET    | `/database/bookcases_by_user_id/`               | `user_id`, `limit`, `offset` | `BookcaseModel[]` |

#### User book state — `/api/user_book_state`

Tracks `reading_status` ∈ `"want_to_read" | "reading" | "completed" | "abandoned"`, plus `current_page` and `percent_complete` (0–100).

| Method | Path                                                       | Body / Params                              | Res                            |
| ------ | ---------------------------------------------------------- | ------------------------------------------ | ------------------------------ |
| POST   | `/user_book_state/create_user_book_state/`                 | `UserBookStateModel`                       | `UserBookStateModel`           |
| GET    | `/user_book_state/get_user_book_state_by_id/{id}`          | path                                       | `UserBookStateModel`           |
| POST   | `/user_book_state/get_user_book_states_by_user_id/`        | `GetUserBookStatesByUserIdRequest`         | `UserBookStateModel[]`         |
| POST   | `/user_book_state/get_user_book_state_by_user_and_book/`   | `GetUserBookStateByUserAndBookRequest`     | `UserBookStateModel`           |
| POST   | `/user_book_state/update_user_book_state/`                 | `UserBookStateModel`                       | `UserBookStateModel`           |
| DELETE | `/user_book_state/delete_user_book_state/{id}`             | path                                       | `{user_book_state_id, deleted}`|

#### User book attributes (rating / review) — `/api/user_book_attributes`

`rating` is `0..9` (NOT `0..10` — backend uses `lt=10`).

| Method | Path                                                     | Body / Params                | Res                          |
| ------ | -------------------------------------------------------- | ---------------------------- | ---------------------------- |
| POST   | `/user_book_attributes/create_user_book_attribute/`      | `UserBookAttributesModel`    | `UserBookAttributesModel`    |
| POST   | `/user_book_attributes/update_book_attribute/`           | `UserBookAttributesModel`    | `UserBookAttributesModel`    |
| DELETE | `/user_book_attributes/delete_user_book_attribute/{id}`  | path                         | `{attribute_id, deleted}`    |
| GET    | `/user_book_attributes/book_attribute_by_id/{id}`        | path                         | `UserBookAttributesModel`    |
| GET    | `/user_book_attributes/book_attribute_by_user_id/`       | `user_id`, `limit`, `offset` | `UserBookAttributesModel[]`  |
| GET    | `/user_book_attributes/book_attribute_by_book_id/`       | `book_id`                    | `UserBookAttributesModel[]`  |

#### Other resource endpoints (CRUD shape — see backend routers for exact fields)

- `/api/genre/{create_genre, get_genre, update_genre, delete_genre/{id}}` — `GenreModel`
- `/api/author/{create_author, get_author, update_author, delete_author/{id}}` — `AuthorModel`
- `/api/avatar/{create_avatar, get_avatar, update_avatar, delete_avatar/{id}}` — `AvatarModel`
- `/api/user_status/...` — `UserStatusModel` (Bronze/Platinum tiers)
- `/api/book_access/...` — `AccessInfoModel`
- `/api/book_sale_info/...` — `BookSaleInfoModel`
- `/api/admin_logs/...` — **admin role only**, `AdminLogsModel`

### 3.5 Pydantic-alias asymmetry (gotcha)

The backend's `BookModel` uses field aliases for Google Books compatibility:

- `google_books_id` ↔ alias `id`
- `volume_info` ↔ alias `volumeInfo`
- `sale_info` ↔ alias `saleInfo`
- `access_info` ↔ alias `accessInfo`

**Pydantic v2 default behavior** (and what FastAPI uses): _responses serialize by field name (snake_case)_, but `BookModel` does **not** set `populate_by_name=True`, so _inputs must use the aliases (camelCase)_. In practice the frontend rarely POSTs raw books (they originate from the Google Books proxy), but if you create one directly, the body must look like `{ "id": "...", "volumeInfo": {...} }`.

For TS response types use snake_case (matches what comes off the wire). For POST bodies to `create_book` / `update_book`, define a separate input type with aliased keys.

### 3.6 Error contract

| Status | Meaning                          | Frontend handling                              |
| ------ | -------------------------------- | ---------------------------------------------- |
| 401    | Missing / expired / bad JWT      | Clear cookie, redirect to `/login`             |
| 403    | Auth'd but not owner / not admin | Show "not allowed" page; do not retry          |
| 404    | Resource not found               | Use SvelteKit `error(404, ...)` from load fn   |
| 422    | Pydantic validation failed       | Map `detail[].loc` → inline form field errors  |
| 500    | DB or internal error             | Show generic error; surface `error_id` for support |

500 responses include an `error_id` UUID — display it (small, copyable) so the user can report it.

---

## 4. Domain model

```
User ─┬─< Bookcase ─< (m:n via BookcaseBook) >─ Book
      ├─< UserBookState   (per-user reading progress on a Book)
      └─< UserBookAttributes (per-user rating 0-9 + review on a Book)

Book ─┬─< (m:n) Genre
      ├─< (m:n) Author
      ├──  VolumeInfo (title, authors[], description, image_links, ...)
      ├──  BookSaleInfo (price, currency, ebook?)
      └──  AccessInfo  (epub/pdf availability, viewability)

User has optional Avatar, optional UserStatus (tier).
```

**Mental model:** a User owns Bookcases (named shelves); books land in Bookcases. Independent of shelves, each User↔Book pair can have a *reading state* (where they are in it) and *attributes* (what they thought of it). Genres and Authors are shared across the catalog.

---

## 5. Svelte 5 conventions

Svelte 5 introduced **runes** — `$`-prefixed compiler keywords. Use them. **Do not use legacy syntax** (`export let`, `$:`, `writable()` for component state). The codebase is greenfield, so there's no compatibility burden.

### The runes (cheat sheet)

```svelte
<script lang="ts">
  // $state — reactive local state (replaces `let count`)
  let count = $state(0);

  // $derived — computed values (replaces `$: doubled = count * 2`)
  let doubled = $derived(count * 2);

  // $derived.by — derived with a function body for multi-step compute
  let summary = $derived.by(() => {
    const sign = count >= 0 ? '+' : '-';
    return `${sign}${Math.abs(count)}`;
  });

  // $effect — side effects when deps change (replaces `$: { ... }`)
  $effect(() => {
    document.title = `Count: ${count}`;
  });

  // $props — component inputs (replaces `export let book: BookModel`)
  let { book, onSelect }: { book: BookModel; onSelect?: (b: BookModel) => void } = $props();

  // $bindable — opt-in two-way binding (rare; prefer callbacks)
  // let { value = $bindable() } = $props();
</script>
```

### Rules

- **`.svelte.ts` for reactive classes/modules.** Runes only work in `.svelte` and `.svelte.ts` (or `.svelte.js`) files. Plain `.ts` cannot use `$state` etc.
- **Prefer `$derived` over `$effect` for computed values.** `$effect` is for side effects (DOM, network, logging) — not for assigning to other state. Use `$effect` sparingly; most reactive logic is `$derived`.
- **Untrack carefully.** `$effect` reads of `$state` create subscriptions. To read without subscribing, wrap in `untrack()` from `'svelte'`.
- **Snippets, not slots.** Svelte 5 added `{#snippet}` / `{@render}` — prefer these over the legacy `<slot>` for content projection.
- **Event handlers are properties, not `on:`**: `<button onclick={handle}>` not `<button on:click={handle}>` (Svelte 5 changed this).
- **No global stores for component-local state.** Only use a store-like pattern for cross-route shared state (e.g., the auth user). For everything else, props + load data are enough.

---

## 6. SvelteKit conventions

### Routing

URL ⇔ folder. `src/routes/books/[book_id]/+page.svelte` → `/books/123`. The `[book_id]` is a path param available as `params.book_id`.

### The route files

| File              | Runs on        | Use for                                                   |
| ----------------- | -------------- | --------------------------------------------------------- |
| `+page.svelte`    | client + SSR   | The page UI                                               |
| `+page.ts`        | server + client| Universal load — public data, no secrets, can return non-serializable |
| `+page.server.ts` | server only    | Auth'd reads, form actions (`export const actions`), anything touching the JWT cookie |
| `+layout.svelte`  | client + SSR   | Wraps the page (and children); render `{@render children()}` |
| `+layout.server.ts` | server only  | Load data shared by all child routes (e.g., current user) |
| `+server.ts`      | server only    | API endpoints owned by the frontend (rare here)           |
| `+error.svelte`   | client + SSR   | Renders when a load throws                                |

### Auth pattern (the recommended flow)

1. **Login** at `routes/login/+page.server.ts` — form action calls `POST /api/authenticate/token/`, sets an `httpOnly` `Secure` cookie named `session_jwt` with the returned token, then `redirect(303, '/')`.
2. **`hooks.server.ts`** reads `event.cookies.get('session_jwt')` on every request and stores it in `event.locals.jwt`. If the cookie is missing or expired and the route is in a protected group, redirect to `/login`.
3. **Server load functions** read `event.locals.jwt` and pass it into `$lib/api/client.ts` to attach the bearer header. Tokens never reach the browser JS.
4. **Layout exposes user** — `+layout.server.ts` returns `{ user }` (looked up from the JWT subject); `+layout.svelte` reads `data.user` and provides it to children.

### Load functions

Prefer `+page.server.ts` for any auth'd backend call. The SvelteKit-enhanced `fetch` (passed into the load function) handles cookies and same-origin propagation; pass it down into the API client so requests are correctly contextualized.

```ts
// routes/books/search/+page.server.ts
import type { PageServerLoad } from './$types';
import { api } from '$lib/api';

export const load: PageServerLoad = async ({ url, fetch, locals }) => {
  const q = url.searchParams.get('q') ?? '';
  if (!q) return { books: [], q };
  const books = await api(fetch, locals.jwt).books.searchByName(q);
  return { books, q };
};
```

### File naming

- Components: **PascalCase**, `BookCard.svelte`, `LoginForm.svelte`.
- Utility modules: **camelCase**, `formatDate.ts`, `bookGrouping.ts`.
- Reactive modules: end in `.svelte.ts` (e.g., `auth.svelte.ts`).
- Types: one entity per file in `$lib/types/`, snake_case to match backend (`user_book_state.ts`).

---

## 7. Skeleton v3 conventions

Skeleton v3 is **framework-agnostic core + framework-specific components**. For Svelte we install both packages:

```bash
pnpm add @skeletonlabs/skeleton @skeletonlabs/skeleton-svelte
```

### Setup essentials

**`src/app.css`** — Tailwind layers + Skeleton imports + theme:

```css
@import 'tailwindcss';

@import '@skeletonlabs/skeleton';
@import '@skeletonlabs/skeleton/optional/presets';
@import '@skeletonlabs/skeleton/themes/cerberus';  /* pick your theme */

@source '../node_modules/@skeletonlabs/skeleton-svelte/dist';
```

**`src/app.html`** — set `data-theme` on `<html>`:

```html
<html lang="en" data-theme="cerberus">
```

### Component import path

Always from `@skeletonlabs/skeleton-svelte` — never from `@skeletonlabs/skeleton` (that's the framework-agnostic core, no Svelte exports):

```svelte
<script lang="ts">
  import { Avatar, Modal, Switch, Tabs } from '@skeletonlabs/skeleton-svelte';
</script>
```

### When to reach for Skeleton vs. raw Tailwind

- **Use Skeleton components** for: Avatars, Modals, Tabs, Switches, Progress bars, Toasts, Rating bars, App Shell, Navigation rails. These ship accessibility, focus management, and theming for free.
- **Use Skeleton design tokens** (e.g., `bg-surface-100-900`, `text-primary-500`) for all colors. Never use raw Tailwind palette classes like `bg-blue-500` — they bypass the theme.
- **Use raw Tailwind utility classes** for layout (`flex`, `grid`, `gap-*`, spacing). Skeleton doesn't have opinions there.
- **Don't compose your own modal/dropdown/tab logic.** If Skeleton has it, use it.

### Theming

One `data-theme` per page is enough. To support light/dark, toggle the `.dark` class on `<html>` (Tailwind's default). Theme tokens automatically pick the dark variant.

---

## 8. API client pattern

**Rule:** Components never call `fetch` directly. They go through `$lib/api/`. This centralizes the base URL, auth header, error mapping, and gives us one place to add retries / logging.

### `src/lib/api/client.ts`

```ts
import { PUBLIC_API_BASE_URL } from '$env/static/public';

export class ApiError extends Error {
  constructor(public status: number, message: string, public errorId?: string) {
    super(message);
  }
}

type Fetch = typeof globalThis.fetch;

export function makeClient(fetch: Fetch, jwt?: string) {
  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
    query?: Record<string, string | number | undefined>,
  ): Promise<T> {
    const url = new URL(`${PUBLIC_API_BASE_URL}/api${path}`);
    for (const [k, v] of Object.entries(query ?? {})) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }

    const headers: Record<string, string> = { Accept: 'application/json' };
    if (jwt) headers.Authorization = `Bearer ${jwt}`;
    if (body !== undefined) headers['Content-Type'] = 'application/json';

    const res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const payload = await res.json().catch(() => ({}));
      throw new ApiError(res.status, payload.detail ?? res.statusText, payload.error_id);
    }
    return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
  }

  return {
    auth: {
      login: (username: string, password: string) =>
        request<TokenResponse>('POST', '/authenticate/token/', { username, password }),
      // ...
    },
    books: {
      searchByName: (book_name: string, max_results = 10, start_index = 0) =>
        request<BookModel[]>('GET', '/books/name/', undefined, { book_name, max_results, start_index }),
      // ...
    },
    // ...one namespace per backend router
  };
}

export type ApiClient = ReturnType<typeof makeClient>;
```

The client is created **per request** so it picks up the right JWT each time. In load functions: `const api = makeClient(event.fetch, event.locals.jwt)`.

### Error mapping in load functions

```ts
import { error, redirect } from '@sveltejs/kit';
import { ApiError } from '$lib/api/client';

try {
  return { book: await api.books.getById(id) };
} catch (e) {
  if (e instanceof ApiError) {
    if (e.status === 401) throw redirect(303, '/login');
    if (e.status === 404) throw error(404, 'Book not found');
    if (e.status === 403) throw error(403, 'Not allowed');
  }
  throw e;
}
```

---

## 9. State management

The defaults are blunt and on purpose:

1. **Server load data** is the source of truth for page content. Don't copy it into a store.
2. **Component-local state** lives in `$state` inside the component.
3. **The only global store** is auth (the current user, hydrated from the session cookie via `+layout.server.ts`).

### Auth store (`src/lib/stores/auth.svelte.ts`)

Use a Svelte 5 reactive class — no `writable()`, no manual `subscribe`:

```ts
import type { UserModel } from '$lib/types/user';

class AuthStore {
  user = $state<UserModel | null>(null);

  get isAuthenticated() {
    return this.user !== null;
  }
  get isAdmin() {
    return this.user?.role === 'admin';
  }

  hydrate(user: UserModel | null) {
    this.user = user;
  }
  clear() {
    this.user = null;
  }
}

export const auth = new AuthStore();
```

Hydrate it in the root layout:

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  let { data, children } = $props();
  $effect(() => auth.hydrate(data.user));
</script>

{@render children()}
```

If you find yourself wanting another global store, ask whether the data could live in `+layout.server.ts` instead. Almost always yes.

---

## 10. Forms & validation

**Pattern:** Skeleton form components + Zod schema for client-side validation + SvelteKit form actions for server-side submission. The backend Pydantic model is the ultimate source of truth — when a 422 comes back, surface field errors inline.

### Zod schemas mirror Pydantic

```ts
// src/lib/schemas/login.ts
import { z } from 'zod';

export const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(7),  // matches backend UserLoginRequest min_length
});
export type LoginInput = z.infer<typeof loginSchema>;
```

### Form action (server-side)

```ts
// src/routes/login/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import { loginSchema } from '$lib/schemas/login';
import { makeClient } from '$lib/api/client';
import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ request, cookies, fetch }) => {
    const form = Object.fromEntries(await request.formData());
    const parsed = loginSchema.safeParse(form);
    if (!parsed.success) {
      return fail(400, { errors: parsed.error.flatten().fieldErrors });
    }
    try {
      const api = makeClient(fetch);
      const { access_token } = await api.auth.login(parsed.data.username, parsed.data.password);
      cookies.set('session_jwt', access_token, {
        httpOnly: true,
        secure: true,
        sameSite: 'lax',
        path: '/',
        maxAge: 60 * 60,  // 60 min — matches backend ACCESS_TOKEN_EXPIRE_MINUTES
      });
    } catch (e) {
      return fail(401, { error: 'Invalid credentials.' });
    }
    throw redirect(303, '/');
  },
};
```

### Form UI (`+page.svelte`)

Use `use:enhance` from `$app/forms` — keeps progressive enhancement (works without JS) while giving you a nice client-side update path.

---

## 11. Testing

- **Unit / component:** Vitest. Test pure utility functions in `$lib/utils/` and component behavior. Run with `pnpm test:unit`.
- **End-to-end:** Playwright. Tests live in `tests/`. Run with `pnpm test:e2e`.
- **API mocking:** [MSW](https://mswjs.io/) (`msw` package) — intercept the backend at the network level for both unit and e2e tests. Keep one set of fixtures in `tests/fixtures/` keyed by endpoint path.
- **Type checking:** `pnpm check` runs `svelte-check` — must pass before commit.

Run a single Playwright test: `pnpm exec playwright test tests/login.spec.ts --headed`.

---

## 12. Dev workflow

```bash
# One-time install
pnpm install

# Run frontend (port 5173)
pnpm dev

# Run backend in another terminal (port 8000)
cd .. && uv run uvicorn app.main:app --reload

# Type check + lint
pnpm check
pnpm lint

# Build for production
pnpm build && pnpm preview
```

**You must run both servers** — SvelteKit at 5173, FastAPI at 8000. The frontend talks to the backend over HTTP; there's no in-process integration.

**Database:** the backend needs MySQL running and migrations applied (`uv run alembic upgrade heads` from the repo root). See `../README.md`.

---

## 13. Known gotchas

1. **CORS allow-origin must match the dev server exactly.** Backend builds the allowed origin from `FRONTEND_ENDPOINT` + `FRONTEND_PORT` env vars (see §3.2). If the scheme, host, or port drifts from where Vite is actually serving, every browser request will preflight-fail. Server-side load functions sidestep this entirely (server→server).
2. **`/authenticate/token/` takes JSON, not OAuth2 form data.** Despite the name, the body is `{ username, password }` JSON.
3. **JWT expires after 60 minutes.** Centralize 401 handling in `$lib/api/client.ts` to redirect to `/login`.
4. **`BookModel` input vs output aliases differ** — responses are snake_case, but POST bodies need camelCase aliases (`id`, `volumeInfo`, etc.). See §3.5.
5. **`UserBookAttributes.rating` is 0–9, not 0–10.** Backend uses `lt=10`.
6. **`min_length=7` on passwords** — match this in Zod schemas or signup will 422.
7. **Google Books quota** — `/api/books/...` endpoints proxy Google Books and are subject to that API's daily quota / latency.
8. **Server-only secrets in `$env/static/private`** — never `$env/static/public`. The JWT itself should never leave the cookie / server.

---

## 14. Quick reference — when in doubt

| You want to...                              | Go to...                                                        |
| ------------------------------------------- | --------------------------------------------------------------- |
| Call the backend                            | `$lib/api/<router>.ts` (add a method to the existing namespace) |
| Add a new page                              | `src/routes/<path>/+page.svelte` + `+page.server.ts` for data   |
| Share data across all pages                 | `src/routes/+layout.server.ts`                                  |
| Add reactive state to a component           | `$state` — never `let` for anything that updates                |
| Compute a value from state                  | `$derived` — never `$:` and never an `$effect` that assigns     |
| Add a global store                          | Don't, unless it's the auth equivalent — re-read §9 first       |
| Style a button / card / surface             | Skeleton component or Skeleton design token — not raw Tailwind colors |
| Show a modal / drawer / toast               | `@skeletonlabs/skeleton-svelte` — don't build your own          |
| Validate form input                         | Zod schema in `$lib/schemas/` mirroring the backend Pydantic model |
| Handle a 401                                | Already handled centrally in `$lib/api/client.ts` — just `throw` |


## Website Theme
Main color theme can be viewed in the image "color_pallete.png". Otherwise those values are:
#256EFF
#46237A
#3DDC97
#FCFCFC
#FF495C

I want the application to be structured similar to SLACK. Where there is a sidebar.
