from fastapi import APIRouter

from src.modules.identity.presentation.router import router as identity_router
from src.presentation.api.v1.health import router as health_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(identity_router, prefix="/auth", tags=["identity"])

# Future modules register their routers here, e.g.:
# from src.modules.drivepass.presentation.router import router as drivepass_router
# api_v1_router.include_router(drivepass_router, prefix="/drivepass", tags=["drivepass"])
