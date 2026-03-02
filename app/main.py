import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.bookcase.router import router as bookcase_route
from app.api.books.router import router as book_route
from app.api.user_book_attributes.router import router as user_book_attributes
from app.db.db_conn import DatabaseOperationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI()

app.include_router(book_route, prefix="/api")
app.include_router(user_book_attributes, prefix="/api")
app.include_router(bookcase_route, prefix="/api")


@app.exception_handler(DatabaseOperationError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error")
    return JSONResponse(status_code=500, content={"detail": "Database error"})


@app.get("/")
def read_root():
    return "Hello"


if __name__ == "__main__":
    load_dotenv()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
