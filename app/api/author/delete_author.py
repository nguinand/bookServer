from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.author_crud import delete_author_by_id
from app.db.db_conn import db_manager

router = APIRouter()


@router.delete("/delete_author_by_id/{author_id}", status_code=status.HTTP_200_OK)
async def author_delete(
    author_id: int,
    session: Session = Depends(db_manager.get_db),
) -> JSONResponse:
    deleted = delete_author_by_id(author_id=author_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"author_id": author_id, "deleted": deleted},
    )
