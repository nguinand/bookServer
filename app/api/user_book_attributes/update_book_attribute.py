from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.crud.user_book_attributes_crud import update_user_book_attribute_entry
from app.db.db_conn import db_manager
from app.models.user_book_attributes import UserBookAttributesModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/update_book_attribute",
    response_model=UserBookAttributesModel,
    status_code=status.HTTP_200_OK,
)
async def update_book_attribute(
    book_replacement: UserBookAttributesModel,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    try:
        updated_book_attribute = update_user_book_attribute_entry(
            book_replacement, session
        )
    except ValueError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    if updated_book_attribute:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "detail": f"Updated book attribute for book id {book_replacement.id}"
            },
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book attribute not fround.",
    )
