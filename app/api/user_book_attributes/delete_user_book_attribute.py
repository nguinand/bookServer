from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.crud.user_book_attributes_crud import delete_user_book_attribute_by_id
from app.db.db_conn import db_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/user_book_attributes", tags=["User Book Attributes"])


@router.delete(
    "/delete_user_book_attribute/{attribute_id}", status_code=status.HTTP_200_OK
)
async def delete_user_book_attribute(
    attribute_id: int, session: Session = Depends(db_manager.get_db)
) -> JSONResponse:
    deleted = delete_user_book_attribute_by_id(attribute_id, session)

    content = {"user_attribute_id": attribute_id, "deleted": deleted}
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)
