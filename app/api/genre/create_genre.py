from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.genre_crud import create_genre, convert_genre_model
from app.db.db_conn import db_manager
from app.models.genre import GenreModel

router = APIRouter()


@router.post(
    "/create_genre/",
    response_model=GenreModel,
    status_code=status.HTTP_200_OK,
)
async def genre_create(
    genre_model: GenreModel,
    session: Session = Depends(db_manager.get_db),
) -> GenreModel:
    genre_data = create_genre(genre_model=genre_model, session=session)
    return convert_genre_model(genre_data)
