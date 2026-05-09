from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.genre_crud import delete_genre
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete("/delete_genre/{genre_id}", status_code=status.HTTP_200_OK)
async def genre_delete(
    genre_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_genre(genre_id=genre_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"genre_id": genre_id, "deleted": deleted},
    )
