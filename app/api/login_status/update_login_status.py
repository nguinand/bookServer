from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.login_status_crud import convert_login_status, update_login_status
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.login_status import LoginStatusModel
from app.utils.api_token import get_authenticated_user
from app.utils.authorization import ensure_current_user_is_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.put(
    "/update_login_status/",
    response_model=LoginStatusModel,
    status_code=status.HTTP_200_OK,
    description=(
        "Replace a login-status row by user ID. Requires an authenticated admin "
        "user and returns the updated login-status record."
    ),
)
async def login_status_update(
    login_status_model: LoginStatusModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_authenticated_user),
) -> LoginStatusModel:
    ensure_current_user_is_admin(current_user, resource_name="update_login_status")
    login_status = update_login_status(
        login_status_model,
        session,
    )
    if login_status:
        return convert_login_status(login_status)

    logger.error(
        "Login-status update failed because the record was not found. "
        f"current_user_id={current_user.id} "
        f"requested_user_id={login_status_model.user_id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Login status not found.",
    )
