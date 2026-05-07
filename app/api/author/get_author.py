from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.author_crud import (
    convert_author,
    get_author_by_id,
    get_author_by_name,
)
from app.db.db_conn import db_manager
from app.models.author import AuthorModel

router = APIRouter()


@router.get(
    "/get_author_by_name/",
    response_model=AuthorModel,
    status_code=status.HTTP_200_OK,
)
async def author_by_name(
    name: str,
    session: Session = Depends(db_manager.get_db),
) -> AuthorModel:
    author_result = get_author_by_name(name=name, session=session)
    if author_result:
        return convert_author(author_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Author not found.",
    )


@router.get(
    "/get_author_by_id/{author_id}",
    response_model=AuthorModel,
    status_code=status.HTTP_200_OK,
)
async def author_by_id(
    author_id: int,
    session: Session = Depends(db_manager.get_db),
) -> AuthorModel:
    author_result = get_author_by_id(author_id=author_id, session=session)
    if author_result:
        return convert_author(author_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Author not found.",
    )
