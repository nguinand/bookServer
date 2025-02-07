
from fastapi import FastAPI
import uvicorn

from app.api import book_route


app = FastAPI()

app.include_router(book_route.router, prefix="/api")


@app.get("/")
def read_root():
    return "Hello"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
