from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.admin_logs_crud import convert_admin_logs, create_admin_logs
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.admin_log import AdminLogsModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter()


@router.post(
    "/create_admin_logs/",
    response_model=AdminLogsModel,
    status_code=status.HTTP_200_OK,
)
async def admin_logs_create(
    admin_log_model: AdminLogsModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> AdminLogsModel:
    ensure_current_user_is_admin(current_user, resource_name="create_admin_logs")
    admin_log_data = create_admin_logs(
        admin_log_model=admin_log_model,
        session=session,
    )
    return convert_admin_logs(admin_log_data)
