from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_status_crud import update_user_status
from app.db.db_conn import db_manager
from app.models.user_status import UserStatusModel

router = APIRouter()


@router.put(
    "/update_user_status/",
    response_model=UserStatusModel,
    status_code=status.HTTP_200_OK,
)
async def user_status_update(
    user_status_model: UserStatusModel,
    session: Session = Depends(db_manager.get_db),
) -> UserStatusModel:
    try:
        user_status_result = update_user_status(
            user_status_replacement=user_status_model,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if user_status_result:
        return UserStatusModel.model_validate(user_status_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User status not found.",
    )
