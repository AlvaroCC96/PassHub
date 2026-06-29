from fastapi import APIRouter
from src.modules.drivepass.vehicles.presentation.router import router as vehicles_router

router = APIRouter()
router.include_router(vehicles_router, prefix="/vehicles", tags=["drivepass-vehicles"])

# Sprint 3 mounts the documents sub-module here, e.g.:
# from src.modules.drivepass.documents.presentation.router import router as documents_router
# router.include_router(documents_router, prefix="/vehicles/{vehicle_id}/documents", tags=["drivepass-documents"])
