from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.db_conn import db_manager

from app.models.user import UserPasswordRequest, UserPasswordResponse
from app.utils.authentication import Authenticator
from app.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/authenticate", tags=["users-password"])


@router.post(
    "/authenticate_user/",
    response_model=UserPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def authenticate_user(
    userPasswordRequest: UserPasswordRequest,
    session: Session = Depends(db_manager.get_db),
) -> UserPasswordResponse:
    user_id = userPasswordRequest.user_id
    password = userPasswordRequest.password
    authenticator = Authenticator(id=user_id, password=password)
    verfied_password = authenticator.verify_password(session=session)
    return UserPasswordResponse(user_id=user_id, valid=verfied_password)
