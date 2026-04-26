from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user import PasswordUpdateRequest, PasswordUpdateResponse
from app.utils.api_token import get_current_user
from app.utils.authentication import PasswordHandler
from app.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/authenticate", tags=["users-password"])


@router.post(
    "/update_user_password/",
    response_model=PasswordUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_password(
    password_update_request: PasswordUpdateRequest,
    session: Session = Depends(db_manager.get_db),
    current_user: User = Depends(get_current_user),
) -> PasswordUpdateResponse:
    authenticator = PasswordHandler(
        id=current_user.id, password=password_update_request.current_password
    )
    if not authenticator.verify_password(session=session):
        logger.error(
            "Password update denied because the current password was invalid. "
            f"user_id={current_user.id}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    authenticator.update_password(
        password_hash=authenticator.hash_password(password_update_request.new_password),
        user=current_user,
        session=session,
    )
    return PasswordUpdateResponse(
        user_id=current_user.id,
        updated=True,
        details="Password updated.",
    )
