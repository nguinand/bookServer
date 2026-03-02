# bookServer

FastAPI service for managing a user's book library and querying Google Books.

## Tech Stack
- Python 3.12+ (CI runs on 3.13)
- FastAPI
- SQLAlchemy + MySQL (`mysqlclient`)
- Alembic migrations
- Ruff, Ty, pytest

## Features
- External Google Books search endpoints
- Internal database CRUD operations

## Prerequisites
- Python 3.12+
- MySQL server
- `uv`
- System libraries required by `mysqlclient`

## Quick Start
1. Install dependencies.

```bash
uv sync --dev
```

2. Create a `.env` in the project root.

```bash
PYTHONPATH=.
export DATABASE_URL="127.0.0.1"
export DATABASE_NAME="books_server"
export DATABASE_USERNAME="your_username"
export DATABASE_PASSWORD="your_password"
export DATABASE_CONNECTION_STRING="mysql+mysqldb://your_username:your_password@127.0.0.1/books_server"
export GOOGLE_BOOKS_API_URL="https://www.googleapis.com/books/v1/volumes"
export GOOGLE_BOOKS_API_KEY="your_google_books_api_key"
```

3. Load environment variables.

```bash
source .env
```

4. Run database migrations.

```bash
uv run alembic upgrade heads
```

5. Start the API server.

```bash
uv run uvicorn app.main:app --reload
```

## API Docs
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Route Overview
All routes are mounted under `/api`.

### External Google Books
| Method | Path | Query Params |
|---|---|---|
| GET | `/api/books/name/` | `book_name`, `max_results`, `start_index` |
| GET | `/api/books/books_by_isbn/` | `isbn`, `max_results`, `start_index` |
| GET | `/api/books/generic/` | `search_type` (`author`, `publisher`, `isbn`, `subject`), `val`, `max_results`, `start_index` |

### Internal Books (DB)
| Method | Path | Notes |
|---|---|---|
| POST | `/api/database/create_book/` | Body: `BookModel` |
| POST | `/api/database/update_book/` | Body: `BookModel` |
| DELETE | `/api/database/delete_book/{book_id}` | Deletes by `book_id` |
| GET | `/api/database/books_by_title/` | Query: `title`, `limit`, `offset` |
| GET | `/api/database/books_by_google_id/{google_id}` | Lookup by Google ID |
| GET | `/api/database/books_by_book_id/{book_id}` | Lookup by DB `book_id` |

### Bookcases (DB)
| Method | Path | Notes |
|---|---|---|
| POST | `/api/database/create_bookcase/` | Body: `BookcaseModel` |
| POST | `/api/database/update_bookcase/` | Body: `BookcaseModel` |
| DELETE | `/api/database/delete_bookcase/{bookcase_id}` | Deletes by `bookcase_id` |
| GET | `/api/database/bookcase_by_id/{bookcase_id}` | Single bookcase |
| GET | `/api/database/bookcases_by_user_id/` | Query: `user_id`, `limit`, `offset` |

### User Book Attributes (DB)
| Method | Path | Notes |
|---|---|---|
| POST | `/api/user_book_attributes/create_user_book_attribute/` | Body: `UserBookAttributesModel` |
| POST | `/api/update_book_attribute` | Body: `UserBookAttributesModel` |
| DELETE | `/api/user_book_attributes/delete_user_book_attribute/{attribute_id}` | Deletes by `attribute_id` |
| GET | `/api/user_book_attributes/book_attribute_by_id/{attribute_id}` | Single attribute |
| GET | `/api/user_book_attributes/book_attribute_by_user_id/` | Query: `user_id`, `limit`, `offset` |
| GET | `/api/user_book_attributes/book_attribute_by_book_id/` | Query: `book_id` |

## Development Commands
Run these from the project root.

```bash
uv run ruff format --check app/
uv run ruff check app/
uv run ty check app/
uv run pytest -q
```

## Pre-commit
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
