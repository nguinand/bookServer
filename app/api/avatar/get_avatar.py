from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.avatar_crud import convert_avatar_to_model, get_avatar_by_id
from app.db.db_conn import db_manager
from app.models.avatar import AvatarModel

router = APIRouter()


@router.get(
    "/get_avatar_by_id/{avatar_id}",
    response_model=AvatarModel,
    status_code=status.HTTP_200_OK,
)
async def avatar_by_id(
    avatar_id: int,
    session: Session = Depends(db_manager.get_db),
) -> AvatarModel:
    avatar_result = get_avatar_by_id(avatar_id=avatar_id, session=session)
    if avatar_result:
        return convert_avatar_to_model(avatar_result)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Avatar not found.",
    )
