from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_crud import convert_user_to_model, update_user
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user import UpdateUserRequest, UserModel
from app.utils.api_token import get_current_user
from app.utils.authorization import ensure_current_user_matches_user_id
from app.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["users-database"])


@router.put("/update_user/", response_model=UserModel, status_code=status.HTTP_200_OK)
async def user_update(
    user_request: UpdateUserRequest,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> UserModel:
    user_model = user_request.user_model
    if user_model.id is None:
        logger.error(
            "User update denied because the request did not include a user id. "
            f"current_user_id={current_user.id}",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required.",
        )

    ensure_current_user_matches_user_id(
        current_user,
        user_model.id,
        resource_name="update_user",
        resource_id=user_model.id,
    )
    updated_user = update_user(user_replacement=user_model, session=session)
    if updated_user:
        return convert_user_to_model(updated_user)

    logger.error(
        "Requested user record was not found for update. "
        f"current_user_id={current_user.id} requested_user_id={user_model.id}",
    )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found.",
    )
