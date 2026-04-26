from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.crud.user_crud import get_user_by_id
from app.db.db_conn import db_manager
from app.db.db_models.user import User
from app.utils.get_env import get_env_val_or_raise
from app.utils.logger import get_logger

logger = get_logger(__name__)

SECRET_KEY = get_env_val_or_raise("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/authenticate/token/")


def create_access_token(subject: int, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(db_manager.get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise ValueError("Token subject is missing or invalid.")
        user_id = int(subject)
    except ExpiredSignatureError:
        logger.error("JWT authentication failed because the token expired.")
        raise credentials_exception
    except (JWTError, TypeError, ValueError):
        logger.error("JWT authentication failed because the token was invalid.")
        raise credentials_exception

    user = get_user_by_id(user_id=user_id, session=session)
    if user is None:
        logger.error(
            "JWT authentication failed because the user could not be resolved. "
            f"user_id={user_id}",
        )
        raise credentials_exception

    return user
