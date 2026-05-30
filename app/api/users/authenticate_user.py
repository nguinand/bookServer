from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.login_status_crud import (
    get_login_status_by_user_id,
    record_failed_login_attempt,
    reset_login_status_after_successful_login,
)
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.models.user import (
    AuthenticationStatusResponse,
    TokenResponse,
    UserLoginRequest,
)
from app.utils.api_token import create_access_token
from app.utils.authentication import PasswordHandler


router = APIRouter(prefix="/authenticate", tags=["users-password"])


def authenticate_login_request(
    user_login_request: UserLoginRequest, session: Session
) -> User:
    authenticator = PasswordHandler(
        username=user_login_request.username,
        password=user_login_request.password,
    )
    user = authenticator.get_user(session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_status = get_login_status_by_user_id(user.id, session)
    if login_status is not None and login_status.locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is locked. Contact an admin.",
        )

    if not authenticator.verify_password_for_user(user):
        record_failed_login_attempt(user.id, session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if login_status is not None:
        reset_login_status_after_successful_login(user.id, session)
    return user


@router.post(
    "/authenticate_user/",
    response_model=AuthenticationStatusResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Validate username and password credentials without issuing a JWT. "
        "This endpoint confirms credentials only and is not sufficient to "
        "establish an authenticated app session."
    ),
)
async def authenticate_user(
    user_login_request: UserLoginRequest,
    session: Session = Depends(db_manager.get_db),
) -> AuthenticationStatusResponse:
    authenticated_user = authenticate_login_request(user_login_request, session)

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
    description=(
        "Authenticate username and password credentials for login and issue a "
        "JWT bearer token. Clients use the returned token in the Authorization "
        "header for protected routes."
    ),
)
async def authenticate_for_token(
    user_login_request: UserLoginRequest,
    session: Session = Depends(db_manager.get_db),
) -> TokenResponse:
    authenticated_user = authenticate_login_request(user_login_request, session)

    return TokenResponse(
        access_token=create_access_token(subject=authenticated_user.id),
        token_type="bearer",
    )
