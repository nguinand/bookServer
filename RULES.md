# Rules

## Purpose

This document defines the required restrictions and acceptable coding standards
for the `bookServer` codebase.

## Scope

- Applies to all repository changes that affect application code, database
  schema, tests, tooling, or developer-facing documentation.
- Enforced through code review, local validation, and the existing GitHub
  Actions checks.
- Priority levels:
  - `Must` = required
  - `Should` = strongly preferred
  - `May` = optional

## Non-Negotiable Restrictions

### Must Not

- Must not commit secrets, tokens, API keys, passwords, or real connection
  strings.
- Must not hardcode secrets in Python files, migrations, tests, or docs.
- Must not bypass authentication, token validation, or user checks for
  user-scoped or admin-sensitive behavior without explicit approval.
- Must not access SQLAlchemy ORM tables directly from route handlers except for
  session dependency wiring through `db_manager.get_db`.
- Must not return raw SQLAlchemy ORM objects from API handlers.
- Must not change the database schema without a matching Alembic migration.
- Must not introduce breaking API behavior without updating the relevant docs.
- Must not add new runtime dependencies without a clear reason and approval.
- Must not alter `pyproject.toml` without explicit approval.
- Must not leave `print()` debugging, commented-out code, or dead imports in
  committed changes.
- Must not perform manual production-style schema edits outside Alembic.

### Must

- Must keep secrets and connection data in environment variables.
- Must use `uv` for dependency installation and project commands.
- Must keep code compatible with Python 3.12+.
- Must define request and response contracts with Pydantic models in
  `app/models/`.
- Must use the existing FastAPI router structure under `app/api/`.
- Must use `db_manager.commit_or_raise()` for write paths that commit changes.
- Must add or update tests when behavior changes.
- Must update docs when stack, API behavior, schema, or workflow changes.

## Architecture And Layering

- Must keep HTTP concerns in `app/api/`.
- Must keep data validation and API payload contracts in `app/models/`.
- Must keep persistence logic in `app/crud/`.
- Must keep ORM entities and relationship tables in `app/db/db_models/`.
- Must keep engine and session lifecycle concerns in `app/db/db_conn.py`.
- Must route new endpoints through the domain router, then include them through
  the aggregate router used by `app/main.py`.
- Must Not place SQL queries, ORM mutations, or schema logic directly in
  `app/main.py`.
- Must Not create cross-layer shortcuts that skip the CRUD layer for normal DB
  operations.
- Should follow the existing Google Books integration pattern in
  `app/api/books/external_api/` for external HTTP calls and upstream error
  handling.
- Should keep shared infrastructure code in `app/utils/` only when it is
  genuinely reusable.

## File And Module Organization

- Must group endpoints by domain under `app/api/`.
- Must place new ORM models in `app/db/db_models/` instead of mixing them into
  CRUD or route modules.
- Must place conversion helpers with CRUD or model translation logic instead of
  burying them in unrelated utilities.
- Should keep modules focused on one primary responsibility.
- Should create a new domain module instead of extending a generic "misc"
  utility file.
- Should Not add catch-all helper modules without a clear ownership boundary.

## Naming Conventions

- Must use `snake_case` for modules, functions, variables, and helper methods.
- Must use `PascalCase` for classes, SQLAlchemy models, and Pydantic models.
- Must use `UPPER_CASE` for constants and environment variable names.
- Must use f-strings for Python string interpolation, such as
  `f"hello {name}"`.
- Should use descriptive names over abbreviations.
- Should name route handlers after the resource and action they perform.
- Should Not use single-letter names outside short local loops.

Examples:

- Good: `get_user_by_id`, `UserBookAttributesModel`, `GOOGLE_BOOKS_API_URL`
- Avoid: `doStuff`, `UBAModel`, `x`

## Functions And Classes

- Must keep side effects explicit.
- Must separate request parsing, business logic, and database writes when the
  code would otherwise become tangled.
- Must keep conversion between ORM objects and API models explicit.
- Should prefer small composable helpers over large route handlers.
- Should keep constructors and methods focused on one responsibility.
- Should Not mix HTTP response assembly, authentication, and DB mutation inside
  a single long function unless the flow is trivial.

## Error Handling

- Must handle client-visible API failures explicitly and raise
  `HTTPException` or return explicit FastAPI/Starlette responses with
  appropriate HTTP status codes.
- Must use `DatabaseOperationError` as the database failure boundary when
  committing through the shared DB manager.
- Must log handled exceptions at `ERROR` level with a general description of
  the failure.
- Must log operational failures with useful context.
- Must Not use bare `except:`.
- Must Not swallow exceptions silently.
- Must Not include identifiable information in exception messages or
  client-visible error details.
- Should sanitize upstream and database errors before returning them to clients.
- Should preserve the existing Google Books `BooksRequestError` mapping pattern
  for upstream failures.

## Logging

- Must use `app.utils.logger.get_logger()` for application logging.
- Must Not leave `print()` statements in committed code.
- Must Not log passwords, JWTs, API keys, or connection strings.
- Should include route, resource ID, user ID, or other identifying context
  when logging failures if it helps diagnose the issue.
- Should keep logs operational and specific rather than noisy.

## Comments And Documentation

- Must update docs when public behavior, required environment variables,
  persistence model, or workflow changes.
- Should add comments only when intent is not obvious from the code.
- Must Not add comments that merely restate what the code already says.
- Should keep doc references accurate when moving or renaming files.

## API Standards

- Must mount application routes under `/api` through `app/main.py`.
- Must define routes with `APIRouter` and explicit `prefix` and `tags`.
- Must set `response_model` when the endpoint returns structured data,
  including authentication routes.
- Must set an explicit `status_code` on route handlers.
- Must accept Pydantic models for request bodies and use Pydantic models for
  structured responses.
- Must return sanitized errors instead of raw tracebacks or raw DB exceptions.
- Should keep route naming consistent within a domain.
- Should prefer explicit, predictable parameters and response shapes.
- Should return `404` for missing resources and `401` for invalid credentials
  where applicable.
- Must Not expose internal-only fields unless they are intentionally part of the
  API contract.

## Database Standards

- Must define schema changes in SQLAlchemy models and track them in Alembic.
- Must create an Alembic migration for every schema change.
- Must review relationship and constraint changes against `schema_audit.md`.
- Must use the shared database session pattern from `db_manager`.
- Must keep transaction boundaries explicit.
- Should use SQLAlchemy ORM and `select()` patterns consistently with the rest
  of the codebase.
- Should keep write operations inside CRUD modules.
- Must Not perform ad hoc schema edits outside migrations.
- Must Not duplicate schema definitions across multiple modules.
- Must Not run Ruff format or Ruff check against Alembic migration files.

## Security Standards

- Must store secrets in environment variables.
- Must use the existing password hashing flow based on `PasswordHandler` and
  Passlib Argon2 for password operations.
- Must use the JWT helpers in `app/utils/api_token.py` when changing token
  flows.
- Must validate auth-sensitive operations before mutating user-scoped data.
- Must Not log passwords, tokens, or other sensitive credentials.
- Must Not weaken authentication behavior without explicit approval.
- Should default to deny when authentication state is missing or invalid.

## Dependency Standards

- Must prefer existing project libraries before introducing new ones.
- Must document the need for any new dependency during review.
- Should favor `httpx` for outbound HTTP work instead of mixing HTTP clients
  without a clear reason.
- Should avoid duplicate libraries that solve the same problem.
- Must Not add tooling or runtime dependencies that overlap existing project
  capabilities without a concrete justification.

## Testing Standards

- Must add or update tests for behavior changes.
- Must run lint, type-check, and relevant tests before merging a change.
- Should place tests near the affected domain when practical.
- Should add regression coverage for bug fixes.
- Must Not treat the GitHub Actions pytest job as sufficient proof of test
  health, because it currently runs with `continue-on-error: true`.
- Must Not merge known failing behavior without explicit approval.

Validation commands:

```bash
uv sync --dev
uv run ruff format --check app/
uv run ruff check app/
uv run ty check app/
uv run pytest -q
uv run alembic upgrade heads
```

## Performance And Reliability Standards

- Should avoid unnecessary queries inside loops.
- Should avoid avoidable N+1 query patterns.
- Should preserve the current sync/async boundary intentionally:
  - SQLAlchemy DB access is synchronous
  - Google Books HTTP calls are async through `httpx.AsyncClient`
- Should keep external API error handling centralized and predictable.
- Must Not introduce repeated DB writes or repeated upstream calls when a single
  operation would be sufficient.

## Git And Review Standards

- Must keep changes scoped to the task.
- Must keep refactors separate from behavior changes when practical.
- Must explain API, schema, dependency, and security-relevant changes clearly in
  review.
- Should include validation results in review notes for non-trivial changes.
- Should avoid unrelated formatting churn.
- Must Not merge undocumented breaking changes.
- Most Not commit any changes.

## Documentation Sync Requirements

- If stack or tooling changes, update:
  - `README.md`
  - `ARCHITECHTURE.md`
  - `AGENTS.md`
  - `SKILL.md`
  - `RULES.md`
- If schema changes, update:
  - `schema_audit.md`
  - `ARCHITECHTURE.md` when the persistence model description changes
    materially
- If API behavior changes, update:
  - `README.md`
  - `ARCHITECHTURE.md` when route structure or integration behavior changes
    materially
- If repo workflow expectations change, update:
  - `AGENTS.md`
  - `SKILL.md`
  - `RULES.md`

## Exceptions Process

- Exceptions must be called out explicitly during review.
- The reason for the exception must be documented.
- Temporary exceptions should include a follow-up action or removal plan.
- Security and schema exceptions require explicit approval before merge.

## Open Decisions

- Decide whether future endpoints should continue the current operation-style
  naming pattern or move toward a more resource-oriented REST layout.
- Decide whether authentication should become mandatory for all internal
  database mutation routes.

## Change Log

- `2026-04-20` Prefilled the project rules based on the current FastAPI,
  SQLAlchemy, Alembic, and `uv` workflow.
