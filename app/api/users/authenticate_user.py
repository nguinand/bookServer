from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.db_conn import db_manager
from app.models.user import (
    AuthenticationStatusResponse,
    TokenResponse,
    UserLoginRequest,
)
from app.utils.api_token import create_access_token
from app.utils.authentication import PasswordHandler
from app.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/authenticate", tags=["users-password"])


@router.post(
    "/authenticate_user/",
    response_model=AuthenticationStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def authenticate_user(
    user_login_request: UserLoginRequest,
    session: Session = Depends(db_manager.get_db),
) -> AuthenticationStatusResponse:
    authenticator = PasswordHandler(
        username=user_login_request.username,
        password=user_login_request.password,
    )
    authenticated_user = authenticator.get_authenticated_user(session=session)
    if authenticated_user is None:
        logger.error(
            "Authentication failed for credential validation. "
            f"username={user_login_request.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticationStatusResponse(
        user_id=authenticated_user.id,
        username=authenticated_user.username,
        authenticated=True,
        details="User authenticated.",
    )


@router.post(
    "/token/",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def authenticate_for_token(
    user_login_request: UserLoginRequest,
    session: Session = Depends(db_manager.get_db),
) -> TokenResponse:
    authenticator = PasswordHandler(
        username=user_login_request.username,
        password=user_login_request.password,
    )
    authenticated_user = authenticator.get_authenticated_user(session=session)
    if authenticated_user is None:
        logger.error(
            f"Authentication failed during token issuance. "
            f"username={user_login_request.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(subject=authenticated_user.id),
        token_type="bearer",
    )
