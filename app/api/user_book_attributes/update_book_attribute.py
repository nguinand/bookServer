from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.db.db_conn import DatabaseOperationError, db_manager
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
        updated_book_attribute = update_book_attribute(book_replacement, session)
    except DatabaseOperationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    if updated_book_attribute:
        status_code = status.HTTP_200_OK
        content = {f"Updated book attribute for book id {book_replacement.id}"}
    else:
        status_code = status.HTTP_204_NO_CONTENT
        content = {f"Book attribute not updated for book id {book_replacement.id}"}
    return JSONResponse(status_code=status_code, content=content)
