from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.avatar_crud import convert_avatar_to_model, update_avatar
from app.db.db_conn import db_manager
from app.models.avatar import AvatarModel

router = APIRouter()


@router.put(
    "/update_avatar/",
    response_model=AvatarModel,
    status_code=status.HTTP_200_OK,
)
async def avatar_update(
    avatar_model: AvatarModel,
    session: Session = Depends(db_manager.get_db),
) -> AvatarModel:
    try:
        avatar_result = update_avatar(
            avatar_replacement=avatar_model,
            session=session,
        )
    except AttributeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    if avatar_result:
        return convert_avatar_to_model(avatar_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Avatar not found.",
    )
