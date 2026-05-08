from fastapi import APIRouter

from app.api.admin_logs.create_admin_logs import router as create_admin_logs
from app.api.admin_logs.delete_admin_logs import router as delete_admin_logs
from app.api.admin_logs.get_admin_logs import router as get_admin_logs
from app.api.admin_logs.get_admin_logs_by_id import router as get_admin_logs_by_id
from app.api.admin_logs.update_admin_logs import router as update_admin_logs

router = APIRouter(prefix="/admin_logs", tags=["admin-logs"])

router.include_router(create_admin_logs)
router.include_router(get_admin_logs_by_id)
router.include_router(get_admin_logs)
router.include_router(update_admin_logs)
router.include_router(delete_admin_logs)
