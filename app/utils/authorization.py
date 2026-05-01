from fastapi import HTTPException, status

from app.db.db_models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

FORBIDDEN_DETAIL = "You do not have access to this resource."


def ensure_current_user_is_admin(
    current_user: User,
    resource_name: str,
) -> None:
    if current_user.role == "admin":
        return

    logger.error(
        f"Authorization denied for {resource_name}. current_user_id={current_user.id}",
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=FORBIDDEN_DETAIL,
    )


def ensure_current_user_matches_user_id(
    current_user: User,
    target_user_id: int,
    resource_name: str,
    resource_id: int | None = None,
) -> None:
    if current_user.role == "admin" or current_user.id == target_user_id:
        return

    logger.error(
        f"Authorization denied for {resource_name}. current_user_id={current_user.id} "
        f"target_user_id={target_user_id} resource_id={resource_id}",
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=FORBIDDEN_DETAIL,
    )


def ensure_current_user_matches_username(
    current_user: User,
    target_username: str,
    resource_name: str,
) -> None:
    if current_user.role == "admin" or current_user.username == target_username:
        return

    logger.error(
        f"Authorization denied for {resource_name}. current_user_id={current_user.id} "
        f"target_username={target_username}",
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=FORBIDDEN_DETAIL,
    )


def ensure_current_user_matches_email(
    current_user: User,
    target_email: str,
    resource_name: str,
) -> None:
    if current_user.role == "admin" or current_user.email == target_email:
        return

    logger.error(
        f"Authorization denied for {resource_name}. current_user_id={current_user.id} "
        f"target_email={target_email}",
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=FORBIDDEN_DETAIL,
    )
