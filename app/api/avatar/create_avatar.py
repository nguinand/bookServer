from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.avatar_crud import convert_avatar_to_model, create_avatar
from app.db.db_conn import db_manager
from app.models.avatar import AvatarModel

router = APIRouter()


@router.post(
    "/create_avatar/",
    response_model=AvatarModel,
    status_code=status.HTTP_200_OK,
)
async def avatar_create(
    avatar_model: AvatarModel,
    session: Session = Depends(db_manager.get_db),
) -> AvatarModel:
    avatar_data = create_avatar(avatar_model=avatar_model, session=session)
    return convert_avatar_to_model(avatar_data)
