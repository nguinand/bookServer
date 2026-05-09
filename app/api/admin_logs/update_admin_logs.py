from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.admin_logs_crud import convert_admin_logs, update_admin_logs
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.admin_log import AdminLogsModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter()


@router.put(
    "/update_admin_logs/",
    response_model=AdminLogsModel,
    status_code=status.HTTP_200_OK,
)
async def admin_logs_update(
    admin_log_model: AdminLogsModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> AdminLogsModel:
    ensure_current_user_is_admin(current_user, resource_name="update_admin_logs")
    try:
        admin_log_result = update_admin_logs(
            admin_log_replacement=admin_log_model,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if admin_log_result:
        return convert_admin_logs(admin_log_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Admin log not found.",
    )
