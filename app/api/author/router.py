from fastapi import APIRouter, Depends

from app.api.author.create_author import router as create_author
from app.api.author.delete_author import router as delete_author
from app.api.author.get_author import router as get_author
from app.api.author.update_author import router as update_author
from app.utils.api_token import get_current_user

router = APIRouter(
    prefix="/author",
    tags=["authors"],
    dependencies=[Depends(get_current_user)],
)

router.include_router(create_author)
router.include_router(get_author)
router.include_router(update_author)
router.include_router(delete_author)
