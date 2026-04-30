from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.admin_logs_crud import (
    convert_admin_logs,
    get_admin_logs,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.admin_log import GetAdminLogsRequest, GetAdminLogsResponse
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter(prefix="/database", tags=["admin-logs"])


@router.post(
    "/get_admin_logs/",
    response_model=GetAdminLogsResponse,
    status_code=status.HTTP_200_OK,
)
async def admin_logs_get(
    admin_logs_request: GetAdminLogsRequest,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> GetAdminLogsResponse:
    ensure_current_user_is_admin(
        current_user,
        resource_name="get_admin_logs",
    )
    admin_logs, total = get_admin_logs(
        admin_logs_request.start_time,
        admin_logs_request.end_time,
        admin_logs_request.limit,
        admin_logs_request.offset,
        session,
    )
    log_models = [convert_admin_logs(admin_log) for admin_log in admin_logs]
    return GetAdminLogsResponse(
        logs=log_models,
        limit=admin_logs_request.limit,
        offset=admin_logs_request.offset,
        count=len(log_models),
        total=total,
    )
