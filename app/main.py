from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from app.api.books.router import router as book_route

app = FastAPI()

app.include_router(book_route, prefix="/api")


@app.get("/")
def read_root():
    return "Hello"


if __name__ == "__main__":
    load_dotenv()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
