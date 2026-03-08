from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.db_conn import db_manager

from app.models.user import UserPasswordRequest, UserPasswordResponse
from app.utils.authentication import PasswordHandler
from app.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/authenticate", tags=["users-password"])


@router.post(
    "/authenticate_user/",
    response_model=UserPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def authenticate_user(
    user_password_request: UserPasswordRequest,
    session: Session = Depends(db_manager.get_db),
) -> UserPasswordResponse:
    user_id = user_password_request.user_id
    password = user_password_request.password
    authenticator = PasswordHandler(id=user_id, password=password)
    verified_password = authenticator.verify_password(session=session)
    return UserPasswordResponse(
        user_id=user_id, valid=verified_password, details="User authenticated"
    )
