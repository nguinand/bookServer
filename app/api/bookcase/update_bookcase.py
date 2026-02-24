from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.crud.bookcase_crud import (
    convert_bookcase,
)
from app.crud.bookcase_crud import (
    update_bookcase as update_bookcase_entry,
)
from app.db.db_conn import db_manager
from app.models.bookcase import BookcaseModel
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["Bookcase"])


@router.post(
    "/update_bookcase/", response_model=BookcaseModel, status_code=status.HTTP_200_OK
)
async def update_bookcase(
    bookcase_replacement: BookcaseModel,
    session: Session = Depends(db_manager.get_db),
) -> BookcaseModel:
    try:
        updated_bookcase = update_bookcase_entry(
            bookcase_replacement=bookcase_replacement, session=session
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )

    if not updated_bookcase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookcase was not found"
        )

    return convert_bookcase(updated_bookcase)
