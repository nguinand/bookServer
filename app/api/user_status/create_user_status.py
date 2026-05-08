from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.user_status_crud import create_user_status
from app.db.db_conn import db_manager
from app.models.user_status import UserStatusModel

router = APIRouter()


@router.post(
    "/create_user_status/",
    response_model=UserStatusModel,
    status_code=status.HTTP_200_OK,
)
async def user_status_create(
    user_status_model: UserStatusModel,
    session: Session = Depends(db_manager.get_db),
) -> UserStatusModel:
    return create_user_status(user_status_model=user_status_model, session=session)
