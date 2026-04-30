from fastapi import APIRouter

from app.api.admin_logs.get_admin_logs import router as get_admin_logs

router = APIRouter()

router.include_router(get_admin_logs)
