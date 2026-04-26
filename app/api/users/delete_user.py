from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.user_crud import delete_user
from app.utils.logger import get_logger
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id


logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["users-database"])


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_200_OK)
async def user_delete(
    user_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    ensure_current_user_matches_user_id(
        current_user,
        user_id,
        resource_name="delete_user",
        resource_id=user_id,
    )
    deleted = delete_user(user_id=user_id, session=session)
    content = {
        "user_id": user_id,
        "deleted": deleted,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content,
    )
