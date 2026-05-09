from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.avatar_crud import delete_avatar
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete("/delete_avatar/{avatar_id}", status_code=status.HTTP_200_OK)
async def avatar_delete(
    avatar_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_avatar(avatar_id=avatar_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"avatar_id": avatar_id, "deleted": deleted},
    )
