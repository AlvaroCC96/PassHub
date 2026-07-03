from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.public_access.domain.entities import PublicSession, VehiclePublicAccess
from src.modules.public_access.infrastructure.models import (
    PublicSessionModel,
    VehiclePublicAccessModel,
)


def _access_to_domain(model: VehiclePublicAccessModel) -> VehiclePublicAccess:
    return VehiclePublicAccess(
        id=model.id,
        vehicle_id=model.vehicle_id,
        public_token=model.public_token,
        pin_hash=model.pin_hash,
        enabled=model.enabled,
        failed_attempts=model.failed_attempts,
        locked_until=model.locked_until,
        last_access_at=model.last_access_at,
        last_success_at=model.last_success_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
        deleted_at=model.deleted_at,
    )


def _session_to_domain(model: PublicSessionModel) -> PublicSession:
    return PublicSession(
        id=model.id,
        vehicle_public_access_id=model.vehicle_public_access_id,
        session_token_hash=model.session_token_hash,
        expires_at=model.expires_at,
        ip_address=model.ip_address,
        user_agent=model.user_agent,
        created_at=model.created_at,
        revoked_at=model.revoked_at,
    )


class SqlAlchemyPublicAccessRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, access_id: UUID) -> VehiclePublicAccess | None:
        model = await self._session.get(VehiclePublicAccessModel, access_id)
        return _access_to_domain(model) if model and not model.is_deleted else None

    async def get_by_vehicle_id(self, vehicle_id: UUID) -> VehiclePublicAccess | None:
        stmt = select(VehiclePublicAccessModel).where(
            VehiclePublicAccessModel.vehicle_id == vehicle_id,
            VehiclePublicAccessModel.deleted_at.is_(None),
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _access_to_domain(model) if model else None

    async def get_by_public_token(self, public_token: str) -> VehiclePublicAccess | None:
        stmt = select(VehiclePublicAccessModel).where(
            VehiclePublicAccessModel.public_token == public_token,
            VehiclePublicAccessModel.deleted_at.is_(None),
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _access_to_domain(model) if model else None

    async def add(self, access: VehiclePublicAccess) -> None:
        self._session.add(
            VehiclePublicAccessModel(
                id=access.id,
                vehicle_id=access.vehicle_id,
                public_token=access.public_token,
                pin_hash=access.pin_hash,
                enabled=access.enabled,
                failed_attempts=access.failed_attempts,
                locked_until=access.locked_until,
                last_access_at=access.last_access_at,
                last_success_at=access.last_success_at,
            )
        )
        await self._session.flush()

    async def save(self, access: VehiclePublicAccess) -> None:
        model = await self._session.get(VehiclePublicAccessModel, access.id)
        if model is None:
            raise LookupError(f"VehiclePublicAccess {access.id} does not exist")
        model.public_token = access.public_token
        model.pin_hash = access.pin_hash
        model.enabled = access.enabled
        model.failed_attempts = access.failed_attempts
        model.locked_until = access.locked_until
        model.last_access_at = access.last_access_at
        model.last_success_at = access.last_success_at
        model.deleted_at = access.deleted_at
        await self._session.flush()


class SqlAlchemyPublicSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, session_id: UUID) -> PublicSession | None:
        model = await self._session.get(PublicSessionModel, session_id)
        return _session_to_domain(model) if model else None

    async def get_by_token_hash(self, token_hash: str) -> PublicSession | None:
        stmt = select(PublicSessionModel).where(
            PublicSessionModel.session_token_hash == token_hash,
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return _session_to_domain(model) if model else None

    async def add(self, session: PublicSession) -> None:
        self._session.add(
            PublicSessionModel(
                id=session.id,
                vehicle_public_access_id=session.vehicle_public_access_id,
                session_token_hash=session.session_token_hash,
                expires_at=session.expires_at,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                revoked_at=session.revoked_at,
            )
        )
        await self._session.flush()

    async def save(self, session: PublicSession) -> None:
        model = await self._session.get(PublicSessionModel, session.id)
        if model is None:
            raise LookupError(f"PublicSession {session.id} does not exist")
        model.revoked_at = session.revoked_at
        await self._session.flush()

    async def revoke_all_for_access(self, vehicle_public_access_id: UUID) -> None:
        now = datetime.now(UTC)
        stmt = (
            update(PublicSessionModel)
            .where(
                PublicSessionModel.vehicle_public_access_id == vehicle_public_access_id,
                PublicSessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def expire_stale(self) -> int:
        now = datetime.now(UTC)
        stmt = (
            update(PublicSessionModel)
            .where(
                PublicSessionModel.expires_at <= now,
                PublicSessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        result: CursorResult[tuple[()]] = await self._session.execute(stmt)  # type: ignore[assignment]
        await self._session.flush()
        return int(result.rowcount)
