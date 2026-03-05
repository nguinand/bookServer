from fastapi import APIRouter
from app.api.users.get_user import router as get_user

router = APIRouter()

router.include_router(get_user)
