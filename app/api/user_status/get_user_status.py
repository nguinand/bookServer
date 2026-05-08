from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_status_crud import get_user_status_by_id
from app.db.db_conn import db_manager
from app.models.user_status import UserStatusModel

router = APIRouter()


@router.get(
    "/get_user_status_by_id/{status_id}",
    response_model=UserStatusModel,
    status_code=status.HTTP_200_OK,
)
async def user_status_by_id(
    status_id: int,
    session: Session = Depends(db_manager.get_db),
) -> UserStatusModel:
    user_status_result = get_user_status_by_id(status_id=status_id, session=session)
    if user_status_result:
        return UserStatusModel.model_validate(user_status_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User status not found.",
    )
