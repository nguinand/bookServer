from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.user_status_crud import delete_user_status
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete("/delete_user_status/{status_id}", status_code=status.HTTP_200_OK)
async def user_status_delete(
    status_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_user_status(id=status_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status_id": status_id, "deleted": deleted},
    )
