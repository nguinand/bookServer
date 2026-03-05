from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.user_crud import convert_user_to_model, create_user
from app.models.user import UserModel
from app.utils.logger import get_logger
from app.db.db_conn import db_manager


logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["users-database"])


@router.post("/create_user/", response_model=UserModel, status_code=status.HTTP_200_OK)
async def user_create(
    user_model: UserModel, session: Session = Depends(db_manager.get_db)
) -> UserModel:
    user_data = create_user(user_model=user_model, session=session)
    return convert_user_to_model(user_data)
