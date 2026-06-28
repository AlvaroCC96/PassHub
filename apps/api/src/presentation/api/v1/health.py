from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings, get_settings
from src.infrastructure.database import get_db_session

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Liveness-agnostic overview, safe for uptime checks and load balancers."""
    return HealthResponse(status="ok", service=settings.app_name, environment=settings.environment)


@router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    """Process is up and able to serve requests — no external dependency check."""
    return {"status": "alive"}


@router.get("/health/readiness", response_model=ReadinessResponse)
async def readiness(session: AsyncSession = Depends(get_db_session)) -> ReadinessResponse:
    """Process can serve traffic — verifies the database connection is usable."""
    await session.execute(text("SELECT 1"))
    return ReadinessResponse(status="ready", database="up")
