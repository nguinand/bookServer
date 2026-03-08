from fastapi import APIRouter
from app.api.users.get_user import router as get_user
from app.api.users.delete_user import router as delete_user
from app.api.users.create_user import router as create_user
from app.api.users.authenticate_user import router as authenticate_user
from app.api.users.update_password import router as update_password

router = APIRouter()

router.include_router(get_user)
router.include_router(delete_user)
router.include_router(create_user)
router.include_router(authenticate_user)
router.include_router(update_password)
