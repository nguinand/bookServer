from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.admin_logs_crud import delete_admin_logs
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter()


@router.delete("/delete_admin_logs/{admin_log_id}", status_code=status.HTTP_200_OK)
async def admin_logs_delete(
    admin_log_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    ensure_current_user_is_admin(current_user, resource_name="delete_admin_logs")
    deleted = delete_admin_logs(admin_log_id=admin_log_id, session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"admin_log_id": admin_log_id, "deleted": deleted},
    )
