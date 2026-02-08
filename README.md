# bookServer

FastAPI service for managing a user's book library and for querying the Google Books API.

## Features
- External search endpoints for Google Books (by name, ISBN, or generic search)
- Internal database CRUD endpoints for books
- SQLAlchemy ORM with MySQL
- Alembic migrations

## Requirements
- Python 3.12+
- MySQL

## Setup
Dependencies are defined in `pyproject.toml`.

Example install options:
```bash
# If you use uv
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Environment variables
These are read at runtime (see `app/db/db_conn.py` and `app/api/books/external_api/__init__.py`):

```
DATABASE_USERNAME=...
DATABASE_PASSWORD=...
DATABASE_URL=localhost:3306
DATABASE_NAME=...
GOOGLE_BOOKS_API_URL=https://www.googleapis.com/books/v1/volumes
GOOGLE_BOOKS_API_KEY=...
```

Note: `GOOGLE_BOOKS_API_URL` must include the `http://` or `https://` scheme.

## Migrations
```bash
alembic upgrade head
```

To create a new migration:
```bash
alembic revision --autogenerate -m "your message"
```

## Run the app
```bash
uvicorn app.main:app --reload
```

API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints (high level)
Base prefix: `/api`

### External (Google Books)
- `GET /api/books/name/` (query params: `book_name`, `max_results`, `start_index`)
- `GET /api/books/books_by_isbn/` (query params: `isbn`, `max_results`, `start_index`)
- `GET /api/books/generic/` (query params: `search_type`, `val`, `max_results`, `start_index`)

### Internal (Database)
- `POST /api/database/create_book/`
- `POST /api/database/update_book/`
- `DELETE /api/database/delete_book/{book_id}`
- `GET /api/database/books_by_title/{title}`
- `GET /api/database/books_by_google_id/{google_id}`
- `GET /api/database/books_by_book_id/{book_id}`

## Tests and linting
```bash
pytest
ruff .
```
