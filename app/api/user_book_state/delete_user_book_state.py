from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.user_book_state_crud import delete_user_book_state_by_id
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete(
    "/delete_user_book_state_by_id/{user_book_state_id}",
    status_code=status.HTTP_200_OK,
)
async def user_book_state_delete(
    user_book_state_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_user_book_state_by_id(
        user_book_state_id=user_book_state_id,
        session=session,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"user_book_state_id": user_book_state_id, "deleted": deleted},
    )
