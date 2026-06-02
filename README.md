# bookServer

`bookServer` is a FastAPI backend for managing a personal book library, storing
library data in MySQL, and querying Google Books for search and recommendations.
The repo also includes a SvelteKit frontend under `frontend/`.

## Stack

- Backend: Python 3.12+, FastAPI, SQLAlchemy, MySQL, Alembic
- Auth: JWT bearer tokens with `python-jose`, Passlib Argon2 password hashing
- External API: Google Books through HTTPX
- Validation/tooling: Pydantic v2, Ruff, Ty, pytest, pre-commit
- Frontend: SvelteKit, Svelte 5, TypeScript, Vite, Tailwind/Skeleton
- Package tools: `uv` for Python, npm for the frontend

## Repository Map

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app, router registration, CORS, DB error handler |
| `app/api/` | Route handlers by domain |
| `app/models/` | Pydantic request/response models |
| `app/crud/` | Database operations and conversion helpers |
| `app/db/db_models/` | SQLAlchemy ORM models and association tables |
| `app/utils/` | Auth, authorization, env, logging, error recording |
| `alembic/` | Database migrations |
| `frontend/` | SvelteKit client |
| `AGENTS.md` | Codex startup guide |
| `ARCHITECHTURE.md` | Backend architecture notes |
| `RULES.md` | Project rules and constraints |
| `TASK_TEMPLATE.md` | Ad hoc task brief template |

## Backend Setup

Install dependencies:

```bash
uv sync --dev
```

Create a root `.env` with these variables:

```text
PYTHONPATH
DATABASE_URL
DATABASE_NAME
DATABASE_USERNAME
DATABASE_PASSWORD
DATABASE_CONNECTION_STRING
GOOGLE_BOOKS_API_URL
GOOGLE_BOOKS_API_KEY
SECRET_KEY
FRONTEND_ENDPOINT
FRONTEND_PORT
BACKEND_ENDPOINT
BACKEND_PORT
```

Load env vars:

```bash
source .env
```

Apply migrations:

```bash
uv run alembic upgrade heads
```

Start the backend:

```bash
uv run uvicorn app.main:app --reload
```

API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Frontend Setup

Install dependencies:

```bash
npm --prefix frontend install
```

Create `frontend/.env` with this variable:

```text
PUBLIC_API_BASE_URL
```

Start the frontend:

```bash
npm --prefix frontend run dev
```

## Authentication

Public endpoints:

- `POST /api/database/create_user/`
- `POST /api/authenticate/authenticate_user/`
- `POST /api/authenticate/token/`

All other application routes should be treated as bearer-token protected unless
the route code explicitly says otherwise. Protected requests use:

```text
Authorization: Bearer <token>
```

Login uses JSON, not OAuth2 form encoding:

```json
{
  "username": "user",
  "password": "password"
}
```

Account lockout is tracked per existing username. Failed attempts for
nonexistent usernames return `401 Invalid credentials.` and do not create
login-status rows. User creation also does not create a login-status row.

For existing users, the fourth failed password attempt within a rolling
10-minute window stores the lockout state but still returns
`401 Invalid credentials.` Requests after the account is locked return
`423 Locked` with:

```json
{
  "detail": "Account is locked. Contact an admin."
}
```

Locked users are also rejected from protected routes even when they already
have a valid JWT.

## Route Overview

All application routes are mounted under `/api`.

### Auth And Users

| Method | Path |
| --- | --- |
| POST | `/api/database/create_user/` |
| POST | `/api/authenticate/authenticate_user/` |
| POST | `/api/authenticate/token/` |
| POST | `/api/authenticate/update_user_password/` |
| GET | `/api/database/user_by_id/{user_id}` |
| GET | `/api/database/users_by_email/{email}` |
| GET | `/api/database/users_by_username/{username}` |
| PUT | `/api/database/update_user/` |
| DELETE | `/api/database/delete_user/{user_id}` |

### Login Status And Admin Unlock

All login-status CRUD and admin unlock routes require an authenticated admin
user.

| Method | Path |
| --- | --- |
| POST | `/api/login_status/create_login_status/` |
| GET | `/api/login_status/login_status_by_user_id/{user_id}` |
| PUT | `/api/login_status/update_login_status/` |
| DELETE | `/api/login_status/delete_login_status/{user_id}` |
| POST | `/api/admin/unlock_user_account_by_id/` |
| POST | `/api/admin/unlock_user_account_by_username/` |

### Books And Google Books

| Method | Path |
| --- | --- |
| GET | `/api/books/name/` |
| GET | `/api/books/books_by_isbn/` |
| GET | `/api/books/generic/` |
| GET | `/api/books/recommendations/by_author/` |
| GET | `/api/books/recommendations/by_genre/` |
| GET | `/api/books/recommendations/by_bookshelf_genre/` |
| POST | `/api/database/create_book/` |
| POST | `/api/database/update_book/` |
| DELETE | `/api/database/delete_book/{book_id}` |
| GET | `/api/database/books_by_title/` |
| GET | `/api/database/books_by_google_id/{google_id}` |
| GET | `/api/database/books_by_book_id/{book_id}` |

### Library State

| Method | Path |
| --- | --- |
| POST | `/api/database/create_bookcase/` |
| POST | `/api/database/update_bookcase/` |
| DELETE | `/api/database/delete_bookcase/{bookcase_id}` |
| GET | `/api/database/bookcase_by_id/{bookcase_id}` |
| GET | `/api/database/bookcases_by_user_id/` |
| POST | `/api/user_book_attributes/create_user_book_attribute/` |
| POST | `/api/update_book_attribute` |
| DELETE | `/api/user_book_attributes/delete_user_book_attribute/{attribute_id}` |
| GET | `/api/user_book_attributes/book_attribute_by_id/{attribute_id}` |
| GET | `/api/user_book_attributes/book_attribute_by_user_id/` |
| GET | `/api/user_book_attributes/book_attribute_by_book_id/` |
| GET | `/api/user_book_attributes/book_attribute_by_book_and_user_id/` |
| POST | `/api/user_book_state/create_user_book_state/` |
| PUT | `/api/user_book_state/update_user_book_state/` |
| DELETE | `/api/user_book_state/delete_user_book_state_by_id/{user_book_state_id}` |
| GET | `/api/user_book_state/get_user_book_state_by_id/{user_book_state_id}` |
| POST | `/api/user_book_state/get_user_book_states_by_user_id/` |
| POST | `/api/user_book_state/get_user_book_state_by_user_and_book/` |

### Supporting Resources

| Domain | Routes |
| --- | --- |
| Authors | `/api/author/...` |
| Genres | `/api/genre/...` |
| Avatars | `/api/avatar/...` |
| User status | `/api/user_status/...` |
| Book access | `/api/book_access/...` |
| Book sale info | `/api/book_sale_info/...` |
| Admin logs | `/api/admin_logs/...` |
| Login status | `/api/login_status/...` |
| Admin actions | `/api/admin/...` |

Admin log routes require an authenticated admin user.

## Development Commands

Run backend checks from the repo root:

```bash
uv run ruff format --check app/
uv run ruff check app/
uv run ty check app/
uv run pytest -q
```

Run frontend checks:

```bash
npm --prefix frontend run check
```

Pre-commit:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Migrations

Create a migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
uv run alembic upgrade heads
```

Current revision:

```bash
uv run alembic current
```

## Notes

- Keep secrets out of version control.
- `DATABASE_CONNECTION_STRING` is required by Alembic.
- Use `AGENTS.md`, `ARCHITECHTURE.md`, and `RULES.md` for Codex and backend
  workflow context, including the global `grill-me` planning skill.
- Use `frontend/AGENTS.md` for frontend-specific guidance.
