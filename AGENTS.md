# Codex Guide For bookServer

This file is the startup context Codex loads from the repository root. It should
be enough to begin backend work in a fresh window without depending on stale
conversation history.

## Project Snapshot

`bookServer` is a FastAPI backend for a personal book library. It exposes HTTP
APIs under `/api`, stores data in MySQL through SQLAlchemy ORM models, and uses
Google Books for external book lookup and recommendations.

The root of this repo is backend-first. Frontend work lives under `frontend/`
and has its own `frontend/AGENTS.md`.

## Read When Needed

- `README.md` for setup commands, environment variables, and public route notes.
- `ARCHITECHTURE.md` for the longer architecture summary. Keep the current file
  spelling unless the user explicitly asks to rename it.
- `RULES.md` for detailed code review rules and project restrictions.
- `SKILL.md` for the compact backend workflow reference.

## Runtime Stack

- Python 3.12+; CI uses Python 3.13.
- FastAPI + Uvicorn.
- Pydantic v2 request and response models.
- SQLAlchemy 2.x ORM with synchronous sessions.
- MySQL through `mysqlclient`.
- Alembic for migration files.
- HTTPX for Google Books calls.
- JWT bearer auth with `python-jose`.
- Password hashing through Passlib Argon2.
- Tooling: `uv`, Ruff, Ty, pytest, pre-commit.

## Backend Layout

| Path | Role |
| --- | --- |
| `app/main.py` | FastAPI app, CORS setup, router registration, global DB error handler |
| `app/api/` | Route handlers grouped by API domain |
| `app/models/` | Pydantic API contracts |
| `app/crud/` | SQLAlchemy persistence operations and conversion helpers |
| `app/db/db_models/` | SQLAlchemy ORM entities and relationship tables |
| `app/db/db_conn.py` | Engine, session factory, `db_manager`, and `DatabaseOperationError` |
| `app/utils/` | Auth, authorization, env lookup, logging, and error-log helpers |
| `app/tests/` | FastAPI/TestClient API tests |
| `app/crud/crud_tests/` | CRUD unit tests |
| `alembic/` | Migration environment and revision files |

## Routing Model

`app/main.py` mounts all domain routers with the `/api` prefix.

Important domains:

- `app/api/books/`: Google Books search, recommendations, and stored-book CRUD.
- `app/api/users/`: user CRUD, JSON login, JWT token issuance, password update.
- `app/api/bookcase/`: user-owned bookcase CRUD.
- `app/api/user_book_attributes/`: per-user ratings and review metadata.
- `app/api/user_book_state/`: per-user reading status/progress.
- `app/api/admin_logs/`: admin log CRUD and paginated retrieval.
- `app/api/author/`, `genre/`, `avatar/`, `user_status/`, `book_access/`,
  `book_sale_info/`: supporting CRUD domains.

When adding endpoints, follow the existing per-domain pattern:

1. Add or update a focused route module under `app/api/<domain>/`.
2. Keep request/response models in `app/models/`.
3. Put DB work in `app/crud/`.
4. Include route modules through the domain `router.py`.
5. Ensure the domain router is included from `app/main.py` when creating a new
   top-level API domain.

## API Contracts

- Use explicit Pydantic models for request bodies and structured responses.
- Set `response_model` and `status_code` on route decorators when returning
  structured data.
- Raise `HTTPException` for handled client-visible failures.
- Do not return SQLAlchemy ORM objects directly from route handlers.
- Convert ORM objects to API models explicitly, either with local conversion
  helpers or `Model.model_validate()` when the Pydantic model is configured for
  ORM-style validation.
- Keep route naming consistent with the current operation-style API paths such
  as `/database/create_user/`, `/database/update_book/`, and
  `/books/recommendations/by_author/`.

## Authentication And Authorization

Public endpoints:

- `POST /api/database/create_user/`
- `POST /api/authenticate/authenticate_user/`
- `POST /api/authenticate/token/`

All other application routes should require `Authorization: Bearer <token>`
unless the user explicitly approves a public route.

Auth details:

- Login uses JSON `UserLoginRequest` with `username` and `password`; it is not
  OAuth2 form-encoded even though the token path is named `/token/`.
- Token creation and token-to-user resolution live in `app/utils/api_token.py`.
- Password verification and hashing live in `app/utils/authentication.py` via
  `PasswordHandler`.
- Owner/admin checks live in `app/utils/authorization.py`.
- Admin override is based on `current_user.role == "admin"`.
- For simple admin gates, keep the role check direct in the relevant helper or
  handler flow; do not add a private `_is_admin` helper.

Router-level auth exists on several routers, including books, author, genre,
avatar, user status, user book state, book access, and book sale info. User,
bookcase, user-book-attributes, and admin-log routes often enforce auth or
admin checks inside individual handlers. Check the current route before adding
duplicate dependencies.

## Database And Persistence

- Use `db_manager.get_db` for FastAPI session injection.
- Use `db_manager.commit_or_raise(session, operation=...)` for write paths.
- Keep ORM mutations and SQLAlchemy queries out of route handlers unless the
  route is only wiring a session dependency.
- Keep normal DB operations in `app/crud/`.
- Keep ORM entities and association tables in `app/db/db_models/`.
- Use SQLAlchemy ORM and `select()` patterns consistent with the surrounding
  CRUD module.
- Prefer positional helper arguments when practical. Avoid bare `*`
  keyword-only helper signatures unless the surrounding code already uses that
  style.

Schema changes:

- Update ORM models and add a matching Alembic revision file for schema changes.
- Do not run Alembic commands unless the user explicitly asks.
- Do not run Ruff format or Ruff check against `alembic/` migration files.

## Error Handling And Logging

- `DatabaseOperationError` is the commit failure boundary.
- `app/main.py` has the global `DatabaseOperationError` handler. It returns a
  sanitized HTTP 500 body with an `error_id`.
- Database failures are recorded through `ErrorLogRecorder`.
- Preserve both the wrapped DBAPI message and the exception class string when
  touching database error logging.
- Do not expose raw DB exceptions, tracebacks, secrets, passwords, JWTs, or API
  keys in client responses or logs.
- Use `app.utils.logger.get_logger()` instead of `print()`.
- Use f-strings for Python runtime interpolation and logging messages where
  practical.

## Google Books Integration

- Shared upstream setup lives in `app/api/books/external_api/__init__.py`.
- Use `httpx.AsyncClient` for Google Books requests.
- Reuse `book_api_request()` and handle `BooksRequestError` with the existing
  sanitized JSON response pattern.
- Build returned books as `BookModel` from Google Books `id`, `volumeInfo`,
  `saleInfo`, and `accessInfo`.
- On invalid upstream payloads, return the existing 422 validation response
  shape unless intentionally changing the API contract.
- Recommendation routes live under
  `app/api/books/external_api/recommendations/` and are mounted by the books
  router, so they require bearer auth through the books router dependency.

## Tests And Validation

Use the smallest validation set that proves the change.

Common commands:

```bash
uv run ruff format --check app/
uv run ruff check app/
uv run ty check app/
uv run pytest -q
```

Useful targeted tests:

- Auth/user routes: `uv run pytest -q app/tests/test_auth_api.py`
- Recommendations: `uv run pytest -q app/tests/test_recommendations_api.py`
- Admin logs: `uv run pytest -q app/tests/test_admin_logs_api.py app/crud/crud_tests/test_admin_logs_crud.py`
- Error logging: `uv run pytest -q app/tests/test_database_error_handler.py app/crud/crud_tests/test_error_log_crud.py app/crud/crud_tests/test_user_crud_error_logging.py`

Local test patterns:

- Tests set required env vars before importing `app.main`.
- FastAPI tests use `TestClient(app)`.
- Tests override `db_manager.get_db` with `app.dependency_overrides`.
- Auth tests commonly monkeypatch `app.utils.api_token.get_user_by_id`.
- CRUD tests use mocks heavily and should not require a live MySQL server.
- `app/db/test_db_conn.py` is an integration check and skips when MySQL is
  unavailable.

Pre-commit notes:

- `check-json` excludes `frontend/tsconfig.json` because it is JSONC-style.
- If pre-commit cache permissions fail in this environment, validate config
  with `PRE_COMMIT_HOME=/tmp/pre-commit-cache .venv/bin/pre-commit validate-config`
  or use direct `.venv/bin/ruff` / `.venv/bin/ty` checks.

## Environment Variables

The backend expects these values depending on import path and run mode:

- `DATABASE_URL`
- `DATABASE_NAME`
- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_CONNECTION_STRING`
- `GOOGLE_BOOKS_API_URL`
- `GOOGLE_BOOKS_API_KEY`
- `SECRET_KEY`
- `FRONTEND_ENDPOINT`
- `FRONTEND_PORT`
- `BACKEND_ENDPOINT`
- `BACKEND_PORT`

Do not hardcode real values in code, migrations, tests, or docs.

## Editing Boundaries

- Keep changes scoped to the requested backend behavior.
- Do not alter `pyproject.toml` or add dependencies without explicit approval.
- Do not commit changes unless the user explicitly asks.
- Do not remove or rewrite user changes in a dirty worktree.
- Update `README.md`, `ARCHITECHTURE.md`, `RULES.md`, `SKILL.md`, and this file
  when stack, API behavior, schema, or workflow expectations change.
