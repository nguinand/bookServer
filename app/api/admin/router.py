from fastapi import APIRouter

from app.api.admin.unlock_user_account import router as unlock_user_account

router = APIRouter(prefix="/admin", tags=["admin"])

router.include_router(unlock_user_account)
