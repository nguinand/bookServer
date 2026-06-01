from fastapi import APIRouter

from app.api.login_status.create_login_status import router as create_login_status
from app.api.login_status.delete_login_status import router as delete_login_status
from app.api.login_status.get_login_status import router as get_login_status
from app.api.login_status.update_login_status import router as update_login_status

router = APIRouter(prefix="/login_status", tags=["login-status"])

router.include_router(create_login_status)
router.include_router(get_login_status)
router.include_router(update_login_status)
router.include_router(delete_login_status)
