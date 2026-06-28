from uuid import UUID

from src.core.exceptions import UnauthorizedError
from src.modules.identity.application.ports import UserRepository
from src.modules.identity.domain.entities import User


class GetCurrentUserUseCase:
    def __init__(self, *, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, *, user_id: UUID) -> User:
        user = await self._user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("User not found or inactive", error_code="invalid_session")
        return user
