from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.admin_logs_crud import create_admin_logs
from app.crud.login_status_crud import (
    convert_login_status,
    unlock_login_status_by_user_id,
    unlock_login_status_by_username,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.admin_log import AdminEventType, AdminLogsModel
from app.models.login_status import (
    LoginStatusModel,
    UnlockLoginStatusByUserIdRequest,
    UnlockLoginStatusByUsernameRequest,
)
from app.utils.api_token import get_authenticated_user
from app.utils.authorization import ensure_current_user_is_admin

router = APIRouter()


@router.post(
    "/unlock_user_account_by_id/",
    response_model=LoginStatusModel,
    status_code=status.HTTP_200_OK,
    description=(
        "Unlock a user account by user ID. Requires an authenticated admin user, "
        "resets the existing login-status row, and records an admin modify log."
    ),
)
async def unlock_user_account_by_id(
    unlock_request: UnlockLoginStatusByUserIdRequest,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_authenticated_user),
) -> LoginStatusModel:
    ensure_current_user_is_admin(current_user, resource_name="unlock_user_account")
    unlocked_login_status = unlock_login_status_by_user_id(
        unlock_request.user_id,
        session,
    )
    if unlocked_login_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Login status not found.",
        )

    create_admin_logs(
        AdminLogsModel(
            id=None,
            event_type=AdminEventType.MODIFY,
            event_description=(
                f"Admin user {current_user.id} unlocked account for user "
                f"{unlocked_login_status.user_id}."
            ),
        ),
        session,
    )
    return convert_login_status(unlocked_login_status)


@router.post(
    "/unlock_user_account_by_username/",
    response_model=LoginStatusModel,
    status_code=status.HTTP_200_OK,
    description=(
        "Unlock a user account by username. Requires an authenticated admin user, "
        "resets the existing login-status row, and records an admin modify log."
    ),
)
async def unlock_user_account_by_username(
    unlock_request: UnlockLoginStatusByUsernameRequest,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_authenticated_user),
) -> LoginStatusModel:
    ensure_current_user_is_admin(current_user, resource_name="unlock_user_account")
    try:
        unlocked_login_status = unlock_login_status_by_username(
            unlock_request.username,
            session,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if unlocked_login_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Login status not found.",
        )

    create_admin_logs(
        AdminLogsModel(
            id=None,
            event_type=AdminEventType.MODIFY,
            event_description=(
                f"Admin user {current_user.id} unlocked account for user "
                f"{unlocked_login_status.user_id}."
            ),
        ),
        session,
    )
    return convert_login_status(unlocked_login_status)
