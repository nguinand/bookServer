---
name: bookserver-backend
description: Use when working on the bookServer repository. Covers FastAPI
  routes, Pydantic models, SQLAlchemy ORM models, Alembic migrations, Google
  Books integration, authentication, and project documentation. Follow the
  existing app/api -> app/crud -> app/db layering, use uv-based commands, and
  keep README plus the root project markdown files aligned with meaningful
  changes.
---

# bookServer Backend

## Use This Skill When

- adding or changing FastAPI endpoints
- updating request or response models
- changing CRUD behavior or SQLAlchemy models
- creating or reviewing Alembic migrations
- working on user authentication or token handling
- touching Google Books integration code
- updating repository docs to match backend behavior

## Read First

- `README.md`
- `ARCHITECHTURE.md`
- `AGENTS.md`
- `RULES.md`
- `SKILL.md`
- `schema_audit.md` when the task touches schema design or relationships

## Repo Shape

| Path | Role |
| --- | --- |
| `app/main.py` | FastAPI bootstrap and top-level router inclusion |
| `app/api/` | Route handlers by domain |
| `app/models/` | Pydantic models |
| `app/crud/` | DB operations and conversion helpers |
| `app/db/db_models/` | SQLAlchemy entities and association tables |
| `app/db/db_conn.py` | Engine, sessions, and commit/error helpers |
| `app/utils/` | Authentication, env, token, and logger utilities |
| `alembic/` | Migration configuration and revisions |

## Expected Patterns

- Keep HTTP concerns in `app/api/`.
- Keep validation and payload contracts in `app/models/`.
- Keep persistence logic in `app/crud/`.
- Keep schema definitions in `app/db/db_models/`.
- Use `db_manager.get_db` for injected sessions.
- Use `httpx.AsyncClient` and the existing `BooksRequestError` pattern for
  Google Books upstream calls.
- Use `PasswordHandler` for password hashing and verification.
- Use JWT token helpers from `app/utils/api_token.py` when auth flows change.
- Load config through environment variables; do not hardcode secrets.

## Workflow

1. Inspect the route, model, CRUD, and ORM files connected to the task.
2. Change the owning layer first, then update adjacent layers that depend on
   it.
3. If payload shape changes, update Pydantic models and any conversion logic in
   the same pass.
4. If schema changes, update ORM models, add an Alembic migration, and review
   affected queries.
5. If routes or behavior change, update `README.md` and any relevant root
   project docs.
6. Run targeted validation before broader project checks.

## Validation

- Install dependencies: `uv sync --dev`
- Start the app: `uv run uvicorn app.main:app --reload`
- Apply migrations: `uv run alembic upgrade heads`
- Lint: `uv run ruff check app/`
- Type-check: `uv run ty check app/`
- Test: `uv run pytest -q`

## Change Triggers For Docs

Update documentation when any of the following changes:

- runtime stack or tooling
- route layout or public API behavior
- persistence model or migration workflow
- agent workflow or repo editing expectations

When that happens, review:

- `README.md`
- `ARCHITECHTURE.md`
- `AGENTS.md`
- `SKILL.md`
- `RULES.md`

## Pitfalls

- CI uses Python 3.13, while the project requires Python 3.12+ locally.
- The repository declares some packages that are not prominent in the current
  application flow; prefer established in-code patterns before introducing new
  libraries.
- The pytest GitHub Actions job currently continues on error, so do not rely on
  CI alone to confirm test health.
