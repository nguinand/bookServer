# Architecture

## Overview

`bookServer` is a layered FastAPI backend for managing a user's book library.
The backend exposes routes under `/api`, persists data in MySQL through
SQLAlchemy ORM models, issues JWT bearer tokens for authentication, and calls
the Google Books API for search and recommendations.

The repository also contains a SvelteKit frontend under `frontend/`, but this
document describes the backend server architecture. Frontend-specific guidance
lives in `frontend/AGENTS.md`.

## Current Stack

| Area | Stack | Notes |
| --- | --- | --- |
| Language | Python 3.12+ | `pyproject.toml` requires Python 3.12+; CI uses Python 3.13. |
| API framework | FastAPI | The application object and top-level router inclusion live in `app/main.py`. |
| App server | Uvicorn | Used by local development commands. |
| Data validation | Pydantic v2 | API contracts live under `app/models/`. |
| ORM / DB access | SQLAlchemy 2.x | The backend uses synchronous `Session` objects. |
| Database | MySQL | Connected through `mysqlclient` and `mysql+mysqldb://...`. |
| Migrations | Alembic | Revision files live under `alembic/versions/`. |
| External HTTP | HTTPX | Google Books calls use `httpx.AsyncClient`. |
| Authentication | OAuth2 bearer + JWT | JWT encode/decode uses `python-jose`. |
| Password hashing | Passlib Argon2 | Password flows use `PasswordHandler`. |
| Configuration | Environment variables + python-dotenv | Required values are read through `get_env_val_or_raise()`. |
| Logging | Python `logging` | Logger setup is centralized in `app/utils/logger.py`. |
| Error audit logging | `error_logs` table | DB failures are recorded with a public correlation ID. |
| Package management | `uv` | Dependencies are defined in `pyproject.toml` and locked in `uv.lock`. |
| Lint / format | Ruff | Run against `app/`, not Alembic migration files. |
| Type checking | Ty | CI and local docs use `ty check app/`. |
| Testing | pytest | API tests use FastAPI `TestClient`; CRUD tests use mocks. |
| Hooks | pre-commit | Includes formatting, lint, JSON/YAML/TOML, secrets, and merge-conflict checks. |
| CI | GitHub Actions | Runs Ruff, Ty, and pytest on pushes to `main` and pull requests. |

## Runtime Entry Point

`app/main.py` owns the FastAPI application:

1. Creates `app = FastAPI()`.
2. Configures CORS using `FRONTEND_ENDPOINT` and `FRONTEND_PORT`.
3. Includes all domain routers with the shared `/api` prefix.
4. Registers a global `DatabaseOperationError` exception handler.
5. Exposes a simple root route at `/`.

The `if __name__ == "__main__"` block loads environment variables and starts
Uvicorn using `BACKEND_ENDPOINT` and `BACKEND_PORT`.

## Layered Shape

The backend follows a conventional API -> model -> CRUD -> ORM layering:

1. `app/api/` contains FastAPI route handlers grouped by domain.
2. `app/models/` contains Pydantic request and response models.
3. `app/crud/` contains database operations and ORM-to-model conversion helpers.
4. `app/db/db_models/` contains SQLAlchemy ORM entities and association tables.
5. `app/db/db_conn.py` owns engine creation, session lifecycle, and commit error
   wrapping.
6. `app/utils/` contains cross-cutting support for auth, authorization, logging,
   environment variables, and error recording.
7. `alembic/` tracks schema migrations.

Route handlers should be thin. Normal database reads and writes belong in CRUD
modules, and route responses should return Pydantic models or explicit response
objects rather than raw ORM entities.

## API Domains

All application routes are mounted under `/api`.

| Domain | Router | Responsibility |
| --- | --- | --- |
| Books | `app/api/books/router.py` | Google Books search, recommendations, and stored-book CRUD |
| Users | `app/api/users/router.py` | User CRUD, credential validation, token issuance, password update |
| Bookcases | `app/api/bookcase/router.py` | User-owned bookcase CRUD |
| User book attributes | `app/api/user_book_attributes/router.py` | Per-user ratings and review metadata |
| User book state | `app/api/user_book_state/router.py` | Reading status, progress, and user/book lookup |
| Admin logs | `app/api/admin_logs/router.py` | Admin log CRUD and paginated log retrieval |
| Authors | `app/api/author/router.py` | Author CRUD |
| Genres | `app/api/genre/router.py` | Genre CRUD |
| Avatars | `app/api/avatar/router.py` | Avatar CRUD |
| User status | `app/api/user_status/router.py` | User status CRUD |
| Book access | `app/api/book_access/router.py` | Book access metadata CRUD |
| Book sale info | `app/api/book_sale_info/router.py` | Book sale metadata CRUD |

The API currently uses operation-style route names such as
`/database/create_user/`, `/database/update_book/`,
`/books/recommendations/by_author/`, and `/admin_logs/get_admin_logs_by_id/{id}`.

## Authentication And Authorization

Authentication uses JWT bearer tokens.

Public endpoints:

- `POST /api/database/create_user/`
- `POST /api/authenticate/authenticate_user/`
- `POST /api/authenticate/token/`

Protected behavior:

- Most other routes require `Authorization: Bearer <token>`.
- `get_current_user()` in `app/utils/api_token.py` decodes the JWT, validates the
  `sub` claim, loads the user by ID, and returns a SQLAlchemy `User`.
- `PasswordHandler` in `app/utils/authentication.py` verifies and hashes
  passwords with Argon2.
- Owner/admin authorization helpers live in `app/utils/authorization.py`.
- Admin override is represented by `current_user.role == "admin"`.

Some domains apply auth at the aggregate router level, including books, author,
genre, avatar, user status, user book state, book access, and book sale info.
Other domains enforce auth or admin access inside individual route handlers
because they need resource-specific owner checks.

## Database Access

`app/db/db_conn.py` defines the database boundary:

- `DatabaseManager` builds the SQLAlchemy engine and session factory from env
  vars.
- `db_manager.get_db` is the FastAPI dependency for request-scoped sessions.
- `db_manager.session` creates a direct session for internal helper workflows.
- `db_manager.commit_or_raise()` commits writes, rolls back SQLAlchemy failures,
  and raises `DatabaseOperationError`.

CRUD modules use SQLAlchemy ORM operations and `select()` queries. Writes call
`commit_or_raise()`, and some operations pass an `ErrorLogOperation` so the
global error handler can record the failing operation name.

## Persistence Model

ORM entities live under `app/db/db_models/`. The active persistence model
includes:

- `Book`
- `Author`
- `Genre`
- `Bookcase`
- `User`
- `Avatar`
- `UserStatus`
- `UserBookAttributes`
- `UserBookState`
- `BookAccess`
- `BookSaleInfo`
- `BookIdentifier`
- `AdminLogs`
- `ErrorLog`

Relationship tables include:

- `book_authors`
- `book_genres`
- `bookcase_books`

Books are the central resource and connect to authors, genres, sale metadata,
access metadata, identifiers, bookcases, ratings/reviews, and reading state.
Users own bookcases, ratings/reviews, and reading-state records, and can have an
avatar and status.

## Pydantic Contracts

Pydantic models live under `app/models/`.

Important model groups:

- `user.py`: login, token response, password update, create/update user, user
  response.
- `book.py`, `volume_info.py`, `identifiers.py`, `book_sale_info.py`,
  `access_info.py`: Google Books and stored-book contracts.
- `bookcase.py`, `user_book_attributes.py`, `user_book_state.py`: user-owned
  library state.
- `admin_log.py`: admin event contracts and paginated log responses.
- Supporting resources: author, genre, avatar, user status.

The API accepts request bodies as Pydantic models and returns structured
Pydantic responses where possible. ORM conversion is explicit through helpers
such as `convert_user_to_model()` and `convert_book_to_model()`.

## Error Handling

Database write failures flow through this path:

1. CRUD write calls `db_manager.commit_or_raise()`.
2. SQLAlchemy failures are rolled back and wrapped in `DatabaseOperationError`.
3. FastAPI routes bubble the exception to the global handler in `app/main.py`.
4. The handler creates an `error_id`, extracts the wrapped DBAPI message and
   exception class, records an `ErrorLog`, logs operational context, and returns
   a sanitized HTTP 500 response:

```json
{
  "detail": "A database error occurred. Please try again later.",
  "error_id": "<uuid>"
}
```

Google Books failures use a separate path:

- Shared upstream request behavior lives in `app/api/books/external_api/__init__.py`.
- HTTP status failures and network failures are converted to `BooksRequestError`.
- Route handlers return sanitized `JSONResponse` objects for those failures.

## Google Books Integration

Google Books is the only active external API integration.

Configuration:

- `GOOGLE_BOOKS_API_URL`
- `GOOGLE_BOOKS_API_KEY`

Search endpoints:

- `/api/books/name/`
- `/api/books/books_by_isbn/`
- `/api/books/generic/`

Recommendation endpoints:

- `/api/books/recommendations/by_author/`
- `/api/books/recommendations/by_genre/`
- `/api/books/recommendations/by_bookshelf_genre/`

Recommendation routes parse Google Books results into `BookModel`, deduplicate
by Google Books ID, and keep fetching pages until the requested `max_results`
count is filled or upstream results are exhausted. Bookshelf recommendations use
database aggregation helpers from `bookcase_crud.py` to select the user's most
common genre and filter already-owned Google Books IDs.

## Configuration

Backend environment variables used across runtime, migrations, and tests:

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

Tests commonly set safe defaults for required import-time variables before
importing `app.main`.

## Development Tooling

Common backend commands:

```bash
uv sync --dev
uv run uvicorn app.main:app --reload
uv run ruff format --check app/
uv run ruff check app/
uv run ty check app/
uv run pytest -q
```

Migration commands exist but should only be run when intentionally working on
schema changes:

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade heads
uv run alembic current
```

Ruff is scoped to `app/`; migration files under `alembic/` are not part of the
Ruff check/format target.

## Testing Architecture

API tests live under `app/tests/` and generally:

- set required environment variables before importing the app,
- use `TestClient(app)`,
- override `db_manager.get_db` through `app.dependency_overrides`,
- monkeypatch auth resolution or CRUD functions to avoid live infrastructure,
- assert route status codes, response shapes, auth gates, and error behavior.

CRUD tests live under `app/crud/crud_tests/` and rely heavily on `MagicMock`
sessions and monkeypatching.

`app/db/test_db_conn.py` is an integration-style MySQL connection check. It
skips when the database is unavailable so the suite remains usable without a
local MySQL instance.

## CI And Hooks

GitHub Actions runs three jobs:

1. Ruff format and lint checks.
2. Ty type checks.
3. pytest.

The pytest CI job currently has `continue-on-error: true`, so local test results
still matter.

Pre-commit includes repository hygiene checks, Ruff, and JSON/YAML/TOML checks.
`frontend/tsconfig.json` is excluded from `check-json` because SvelteKit's
generated TypeScript config uses JSONC-style comments.

## Architectural Constraints

- Keep HTTP concerns in `app/api/`.
- Keep API contracts in `app/models/`.
- Keep persistence logic in `app/crud/`.
- Keep schema definitions in `app/db/db_models/`.
- Keep shared infrastructure in `app/utils/`.
- Do not put normal SQL queries or ORM mutations in `app/main.py`.
- Do not bypass JWT validation, owner checks, or admin checks for protected
  resources.
- Do not hardcode secrets or connection strings.
- Add Alembic revisions for schema changes, but do not run migration commands
  unless explicitly requested.

## Current Notes

- The backend mixes sync DB access with async Google Books calls; preserve that
  boundary unless there is a deliberate architecture change.
- `requests`, `inquirer`, and `mypy` are declared in `pyproject.toml`, but the
  active backend path primarily uses HTTPX for outbound HTTP and Ty for type
  checking.
- The root `AGENTS.md`, `RULES.md`, and `SKILL.md` are the Codex-facing
  operating docs that sit alongside this architecture document.
