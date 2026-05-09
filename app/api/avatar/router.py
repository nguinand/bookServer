from fastapi import APIRouter, Depends

from app.api.avatar.create_avatar import router as create_avatar
from app.api.avatar.delete_avatar import router as delete_avatar
from app.api.avatar.get_avatar import router as get_avatar
from app.api.avatar.update_avatar import router as update_avatar
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/avatar",
    tags=["avatar"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_avatar)
router.include_router(get_avatar)
router.include_router(update_avatar)
router.include_router(delete_avatar)
