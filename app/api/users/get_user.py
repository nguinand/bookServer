from sqlalchemy.orm import Session
from app.crud.user_crud import (
    convert_user_to_model,
    get_user_by_id,
    get_users_by_email,
    get_users_by_username,
)
from app.models.user import UserModel
from app.utils.logger import get_logger
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.db_conn import db_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["users-database"])


@router.get(
    "/users_by_email/{email}", response_model=UserModel, status_code=status.HTTP_200_OK
)
async def user_by_email(
    email: str, session: Session = Depends(db_manager.get_db)
) -> UserModel:
    user_result = get_users_by_email(email=email, session=session)
    if user_result:
        return convert_user_to_model(user_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User by email {email} not found.",
    )


@router.get(
    "/users_by_username/{username}",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
)
async def user_by_username(
    username: str, session: Session = Depends(db_manager.get_db)
) -> UserModel:
    user_result = get_users_by_username(username=username, session=session)
    if user_result:
        return convert_user_to_model(user_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User by username {username} not found",
    )


@router.get(
    "/user_by_id/{user_id}", response_model=UserModel, status_code=status.HTTP_200_OK
)
async def user_by_id(
    user_id: int, session: Session = Depends(db_manager.get_db)
) -> UserModel:
    user_result = get_user_by_id(user_id=user_id, session=session)
    if user_result:
        return convert_user_to_model(user_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User by id {user_id} not found"
    )
