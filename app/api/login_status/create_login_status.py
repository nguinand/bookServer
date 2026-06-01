from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.login_status_crud import convert_login_status, create_login_status
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.login_status import LoginStatusModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_is_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/create_login_status/",
    response_model=LoginStatusModel,
    status_code=status.HTTP_200_OK,
    description=(
        "Create a login-status row for an existing user. Requires an authenticated "
        "admin user and returns the created login-status record."
    ),
)
async def login_status_create(
    login_status_model: LoginStatusModel,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> LoginStatusModel:
    ensure_current_user_is_admin(current_user, resource_name="create_login_status")
    try:
        login_status = create_login_status(
            login_status_model,
            session,
        )
    except ValueError as exc:
        detail = str(exc)
        if detail == "User not found.":
            logger.debug(
                "Login-status create failed because the requested user was not found. "
                f"current_user_id={current_user.id} "
                f"requested_user_id={login_status_model.user_id}",
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )
        if detail == "Login status already exists.":
            logger.debug(
                "Login-status create failed because the row already exists. "
                f"current_user_id={current_user.id} "
                f"requested_user_id={login_status_model.user_id}",
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail,
            )
        logger.error(
            "Login-status create failed because the request was invalid. "
            f"current_user_id={current_user.id} "
            f"requested_user_id={login_status_model.user_id} detail={detail}",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )

    return convert_login_status(login_status)
