from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.user_crud import convert_user_to_model, create_user
from app.models.user import CreateUserRequest, UserModel
from app.utils.logger import get_logger
from app.db.db_conn import db_manager


logger = get_logger(__name__)
router = APIRouter(prefix="/database", tags=["users-database"])


@router.post("/create_user/", response_model=UserModel, status_code=status.HTTP_200_OK)
async def user_create(
    user_request: CreateUserRequest, session: Session = Depends(db_manager.get_db)
) -> UserModel:
    user_data = create_user(
        user_model=user_request.user_model,
        password=user_request.password,
        session=session,
    )
    return convert_user_to_model(user_data)
