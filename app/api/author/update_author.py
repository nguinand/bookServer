from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.author_crud import convert_author, update_author
from app.db.db_conn import db_manager
from app.models.author import AuthorModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.put(
    "/update_author/", response_model=AuthorModel, status_code=status.HTTP_200_OK
)
async def author_update(
    author_model: AuthorModel,
    session: Session = Depends(db_manager.get_db),
) -> AuthorModel:
    try:
        author_result = update_author(author_replacement=author_model, session=session)
    except ValueError as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if author_result:
        return convert_author(author_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Author not found.",
    )
