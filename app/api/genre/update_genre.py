from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.genre_crud import convert_genre_model, update_genre
from app.db.db_conn import db_manager
from app.models.genre import GenreModel

router = APIRouter()


@router.put(
    "/update_genre/",
    response_model=GenreModel,
    status_code=status.HTTP_200_OK,
)
async def genre_update(
    genre_model: GenreModel,
    session: Session = Depends(db_manager.get_db),
) -> GenreModel:
    try:
        genre_result = update_genre(genre_replacement=genre_model, session=session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if genre_result:
        return convert_genre_model(genre_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Genre not found.",
    )
