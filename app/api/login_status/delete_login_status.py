from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.login_status_crud import delete_login_status_by_user_id
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter()


@router.delete(
    "/delete_login_status/{user_id}",
    status_code=status.HTTP_200_OK,
    description=(
        "Delete a login-status row by user ID. Requires an authenticated admin "
        "user and returns whether a row was deleted."
    ),
)
async def login_status_delete(
    user_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    ensure_current_user_is_admin(current_user, resource_name="delete_login_status")
    deleted = delete_login_status_by_user_id(user_id, session)
    content = {
        "user_id": user_id,
        "deleted": deleted,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content,
    )
