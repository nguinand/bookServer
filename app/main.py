from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.admin_logs.router import router as admin_logs_route
from app.api.author.router import router as author_route
from app.api.avatar.router import router as avatar_route
from app.api.book_access.router import router as book_access_route
from app.api.book_sale_info.router import router as book_sale_info_route
from app.api.bookcase.router import router as bookcase_route
from app.api.books.router import router as book_route
from app.api.genre.router import router as genre_route
from app.api.user_book_attributes.router import router as user_book_attributes
from app.api.user_book_state.router import router as user_book_state_route
from app.api.user_status.router import router as user_status_route
from app.api.users.router import router as user_router
from app.db.db_conn import DatabaseOperationError
from app.utils.error_logger import ErrorLogRecorder
from app.utils.get_env import get_env_val_or_raise
from app.utils.logger import get_logger

logger = get_logger(__name__)
prefix = "/api"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{get_env_val_or_raise('FRONTEND_ENDPOINT')}:{get_env_val_or_raise('FRONTEND_PORT')})"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(book_route, prefix=prefix)
app.include_router(user_book_attributes, prefix=prefix)
app.include_router(bookcase_route, prefix=prefix)
app.include_router(user_router, prefix=prefix)
app.include_router(admin_logs_route, prefix=prefix)
app.include_router(author_route, prefix=prefix)
app.include_router(genre_route, prefix=prefix)
app.include_router(avatar_route, prefix=prefix)
app.include_router(user_status_route, prefix=prefix)
app.include_router(user_book_state_route, prefix=prefix)
app.include_router(book_access_route, prefix=prefix)
app.include_router(book_sale_info_route, prefix=prefix)


def get_database_error_details(exc: DatabaseOperationError) -> tuple[str, str]:
    wrapped_error = exc.args[0] if exc.args else exc
    original_error = getattr(wrapped_error, "orig", wrapped_error)
    return str(original_error), str(original_error.__class__)


@app.exception_handler(DatabaseOperationError)
async def sqlalchemy_error_handler(request: Request, exc: DatabaseOperationError):
    error_id = str(uuid4())
    logger_description = (
        f"Database error [error_id={error_id}] "
        f"method={request.method} path={request.url.path}"
    )
    error_description, exception_type = get_database_error_details(exc)
    ErrorLogRecorder(
        error_id=error_id,
        name=exc.operation or "unknown_operation",
        exception_type=exception_type,
        description=error_description,
    ).record_error()
    logger.exception(logger_description, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database error occurred. Please try again later.",
            "error_id": error_id,
        },
    )


@app.get("/")
def read_root():
    return "Hello"


if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(
        "main:app",
        host=get_env_val_or_raise("BACKEND_ENDPOINT"),
        port=int(get_env_val_or_raise("BACKEND_PORT")),
        reload=True,
    )
