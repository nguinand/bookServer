from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.crud.user_crud import get_user_by_id
from app.db.db_conn import db_manager

from app.models.user import UserPasswordRequest, UserPasswordResponse
from app.utils.authentication import PasswordHandler
from app.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/authenticate", tags=["users-password"])


@router.post(
    "/update_user_password/",
    response_model=UserPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def update_password(
    user_password_request: UserPasswordRequest,
    session: Session = Depends(db_manager.get_db),
) -> UserPasswordResponse:
    user_id = user_password_request.user_id
    password = user_password_request.password
    user_record = get_user_by_id(user_id=user_id, session=session)
    details = "Password not updated"
    if user_record:
        authenticator = PasswordHandler(id=user_id, password=password)
        hashed_password = authenticator.hash_password(password=password)
        password_updated = authenticator.update_password(
            password_hash=hashed_password, user=user_record, session=session
        )
        if password_updated:
            details = f"Password updated for {user_record.email}"
        return UserPasswordResponse(
            user_id=user_id, valid=password_updated, details=details
        )

    return UserPasswordResponse(user_id=user_id, valid=False, details=details)
