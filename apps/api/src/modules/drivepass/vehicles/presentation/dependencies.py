from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_db_session
from src.modules.drivepass.vehicles.application.ports import VehicleRepository
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.infrastructure.repositories import SqlAlchemyVehicleRepository


def get_vehicle_repository(session: AsyncSession = Depends(get_db_session)) -> VehicleRepository:
    return SqlAlchemyVehicleRepository(session)


def get_vehicle_service(
    repository: VehicleRepository = Depends(get_vehicle_repository),
) -> VehicleService:
    return VehicleService(repository)
