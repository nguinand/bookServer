from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.genre_crud import (
    convert_genre_model,
    get_genre_by_id,
    get_genre_by_name,
)
from app.db.db_conn import db_manager
from app.models.genre import GenreModel

router = APIRouter()


@router.get(
    "/get_genre_by_id/{genre_id}",
    response_model=GenreModel,
    status_code=status.HTTP_200_OK,
)
async def genre_by_id(
    genre_id: int,
    session: Session = Depends(db_manager.get_db),
) -> GenreModel:
    genre_result = get_genre_by_id(genre_id=genre_id, session=session)
    if genre_result:
        return convert_genre_model(genre_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Genre not found.",
    )


@router.get(
    "/get_genre_by_name/",
    response_model=GenreModel,
    status_code=status.HTTP_200_OK,
)
async def genre_by_name(
    name: str,
    session: Session = Depends(db_manager.get_db),
) -> GenreModel:
    genre_result = get_genre_by_name(name=name, session=session)
    if genre_result:
        return convert_genre_model(genre_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Genre not found.",
    )
