from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.admin_logs_crud import convert_admin_logs, get_admin_logs_by_id
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.admin_log import AdminLogsModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter()


@router.get(
    "/get_admin_logs_by_id/{admin_log_id}",
    response_model=AdminLogsModel,
    status_code=status.HTTP_200_OK,
)
async def admin_logs_by_id(
    admin_log_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> AdminLogsModel:
    ensure_current_user_is_admin(current_user, resource_name="get_admin_logs_by_id")
    admin_log_result = get_admin_logs_by_id(
        admin_log_id=admin_log_id,
        session=session,
    )
    if admin_log_result:
        return convert_admin_logs(admin_log_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Admin log not found.",
    )
