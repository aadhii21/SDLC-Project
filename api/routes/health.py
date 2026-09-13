from fastapi import APIRouter
from config.settings import settings
#APIRouter is used to group related API endpoints together.
router = APIRouter()
#router can be anything its jus a decorator
@router.get("/health")
async def health_check():
    return{
        "status":"healthy",
        "application":settings.app_name,
        "environment":settings.app_env,
    }