from fastapi import APIRouter, Depends

from app.api.genre.create_genre import router as create_genre
from app.api.genre.delete_genre import router as delete_genre
from app.api.genre.get_genre import router as get_genre
from app.api.genre.update_genre import router as update_genre
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/genre",
    tags=["genre"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_genre)
router.include_router(get_genre)
router.include_router(update_genre)
router.include_router(delete_genre)
