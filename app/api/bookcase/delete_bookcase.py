from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.crud.bookcase_crud import delete_bookcase_by_id
from app.db.db_conn import db_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["Bookcase"])


@router.delete("/delete_bookcase/{bookcase_id}", status_code=status.HTTP_200_OK)
async def delete_bookcase(
    bookcase_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_bookcase_by_id(bookcase_id=bookcase_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"bookcase_id": bookcase_id, "deleted": deleted},
    )
