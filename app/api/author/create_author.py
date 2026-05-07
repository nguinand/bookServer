from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.author_crud import convert_author, create_author
from app.db.db_conn import db_manager
from app.models.author import AuthorModel

router = APIRouter()


@router.post(
    "/create_author/", response_model=AuthorModel, status_code=status.HTTP_200_OK
)
async def author_create(
    author_model: AuthorModel,
    session: Session = Depends(db_manager.get_db),
) -> AuthorModel:
    author_data = create_author(author_model=author_model, session=session)
    return convert_author(author_data)
