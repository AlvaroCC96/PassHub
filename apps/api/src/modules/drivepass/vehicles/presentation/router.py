from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import get_db_session
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.presentation.dependencies import get_vehicle_service
from src.modules.drivepass.vehicles.presentation.schemas import (
    VehicleCreateRequest,
    VehicleResponse,
    VehicleUpdateRequest,
)
from src.modules.identity.presentation.dependencies import CurrentUser

router = APIRouter()


@router.get("/", response_model=list[VehicleResponse])
async def list_vehicles(
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> list[VehicleResponse]:
    vehicles = await vehicle_service.list_for_user(current_user.id)
    return [VehicleResponse.from_domain(v) for v in vehicles]


# Must be declared before `/{vehicle_id}` — otherwise FastAPI would match
# "favorite" as a vehicle_id path parameter.
@router.get("/favorite", response_model=VehicleResponse)
async def get_favorite_vehicle(
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleResponse:
    vehicle = await vehicle_service.get_favorite_for_user(current_user.id)
    return VehicleResponse.from_domain(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleResponse:
    vehicle = await vehicle_service.get_for_user(user_id=current_user.id, vehicle_id=vehicle_id)
    return VehicleResponse.from_domain(vehicle)


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    payload: VehicleCreateRequest,
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
    session: AsyncSession = Depends(get_db_session),
) -> VehicleResponse:
    vehicle = await vehicle_service.create(user_id=current_user.id, **payload.model_dump())
    await session.commit()
    return VehicleResponse.from_domain(vehicle)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    payload: VehicleUpdateRequest,
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
    session: AsyncSession = Depends(get_db_session),
) -> VehicleResponse:
    vehicle = await vehicle_service.update(
        user_id=current_user.id, vehicle_id=vehicle_id, **payload.model_dump()
    )
    await session.commit()
    return VehicleResponse.from_domain(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await vehicle_service.delete(user_id=current_user.id, vehicle_id=vehicle_id)
    await session.commit()


@router.patch("/{vehicle_id}/favorite", response_model=VehicleResponse)
async def set_favorite_vehicle(
    vehicle_id: UUID,
    current_user: CurrentUser,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
    session: AsyncSession = Depends(get_db_session),
) -> VehicleResponse:
    vehicle = await vehicle_service.set_favorite(user_id=current_user.id, vehicle_id=vehicle_id)
    await session.commit()
    return VehicleResponse.from_domain(vehicle)
