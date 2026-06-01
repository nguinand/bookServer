from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.login_status_crud import (
    convert_login_status,
    get_login_status_by_user_id,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.login_status import LoginStatusModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/login_status_by_user_id/{user_id}",
    response_model=LoginStatusModel,
    status_code=status.HTTP_200_OK,
    description=(
        "Get a login-status row by user ID. Requires an authenticated admin user "
        "and returns 404 when the row does not exist."
    ),
)
async def login_status_by_user_id(
    user_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> LoginStatusModel:
    ensure_current_user_is_admin(
        current_user,
        resource_name="login_status_by_user_id",
    )
    login_status = get_login_status_by_user_id(user_id, session)
    if login_status:
        return convert_login_status(login_status)

    logger.error(
        "Requested login-status record was not found for id lookup. "
        f"current_user_id={current_user.id} requested_user_id={user_id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Login status not found.",
    )
