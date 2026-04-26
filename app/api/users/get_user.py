from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_crud import (
    convert_user_to_model,
    get_user_by_id,
    get_users_by_email,
    get_users_by_username,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user import UserModel
from app.utils.api_token import get_current_user
from app.utils.authorization import (
    ensure_current_user_matches_email,
    ensure_current_user_matches_user_id,
    ensure_current_user_matches_username,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["users-database"])


@router.get(
    "/users_by_email/{email}", response_model=UserModel, status_code=status.HTTP_200_OK
)
async def user_by_email(
    email: str,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> UserModel:
    ensure_current_user_matches_email(
        current_user,
        email,
        resource_name="user_by_email",
    )
    user_result = get_users_by_email(email=email, session=session)
    if user_result:
        return convert_user_to_model(user_result)

    logger.error(
        "Requested user record was not found for email lookup. "
        f"current_user_id={current_user.id} email={email}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )


@router.get(
    "/users_by_username/{username}",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
)
async def user_by_username(
    username: str,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> UserModel:
    ensure_current_user_matches_username(
        current_user,
        username,
        resource_name="user_by_username",
    )
    user_result = get_users_by_username(username=username, session=session)
    if user_result:
        return convert_user_to_model(user_result)

    logger.error(
        "Requested user record was not found for username lookup. "
        f"current_user_id={current_user.id} username={username}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )


@router.get(
    "/user_by_id/{user_id}", response_model=UserModel, status_code=status.HTTP_200_OK
)
async def user_by_id(
    user_id: int,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> UserModel:
    ensure_current_user_matches_user_id(
        current_user,
        user_id,
        resource_name="user_by_id",
        resource_id=user_id,
    )
    user_result = get_user_by_id(user_id=user_id, session=session)
    if user_result:
        return convert_user_to_model(user_result)

    logger.error(
        "Requested user record was not found for id lookup. "
        f"current_user_id={current_user.id} requested_user_id={user_id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )
