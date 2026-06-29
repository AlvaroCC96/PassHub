from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports import AIProvider, StorageProvider
from src.core.config import Settings, get_settings
from src.core.di import get_container
from src.core.exceptions import ForbiddenError
from src.infrastructure.database import get_db_session
from src.modules.drivepass.documents.application.ports import (
    DocumentVersionRepository,
    VehicleDocumentRepository,
)
from src.modules.drivepass.documents.presentation.dependencies import (
    get_document_version_repository,
    get_storage_provider,
    get_vehicle_document_repository,
)
from src.modules.drivepass.infrastructure.intelligence_gateway import DrivePassDocumentGateway
from src.modules.drivepass.vehicles.application.services import VehicleService
from src.modules.drivepass.vehicles.presentation.dependencies import get_vehicle_service
from src.modules.intelligence.application.cost_estimator import AICostEstimator
from src.modules.intelligence.application.ports import (
    DocumentExtractedFieldRepository,
    DocumentExtractionRepository,
    VehicleDocumentGateway,
)
from src.modules.intelligence.application.services import DocumentExtractionService
from src.modules.intelligence.infrastructure.repositories import (
    SqlAlchemyDocumentExtractedFieldRepository,
    SqlAlchemyDocumentExtractionRepository,
)
from src.modules.platform.application.services import FeatureFlagService
from src.modules.platform.presentation.dependencies import get_feature_flag_service

AI_EXTRACTION_FEATURE_FLAG = "ai.document_extraction.enabled"


def get_ai_provider() -> AIProvider:
    return get_container().resolve(AIProvider)  # type: ignore[type-abstract]


def get_extraction_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentExtractionRepository:
    return SqlAlchemyDocumentExtractionRepository(session)


def get_extracted_field_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentExtractedFieldRepository:
    return SqlAlchemyDocumentExtractedFieldRepository(session)


def get_document_gateway(
    document_repository: VehicleDocumentRepository = Depends(get_vehicle_document_repository),
    version_repository: DocumentVersionRepository = Depends(get_document_version_repository),
    storage_provider: StorageProvider = Depends(get_storage_provider),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleDocumentGateway:
    """Composes DrivePass's own dependency providers into the adapter for
    Intelligence's port — the same presentation-layer composition pattern
    Identity's router already uses to hand Platform's services to
    `PlatformUserProvisioner`."""
    return DrivePassDocumentGateway(
        document_repository=document_repository,
        version_repository=version_repository,
        storage_provider=storage_provider,
        vehicle_service=vehicle_service,
    )


def get_extraction_service(
    extraction_repository: DocumentExtractionRepository = Depends(get_extraction_repository),
    field_repository: DocumentExtractedFieldRepository = Depends(get_extracted_field_repository),
    gateway: VehicleDocumentGateway = Depends(get_document_gateway),
    ai_provider: AIProvider = Depends(get_ai_provider),
    settings: Settings = Depends(get_settings),
) -> DocumentExtractionService:
    return DocumentExtractionService(
        extraction_repository=extraction_repository,
        field_repository=field_repository,
        gateway=gateway,
        ai_provider=ai_provider,
        cost_estimator=AICostEstimator(),
        provider_name=settings.ai.provider,
        model=settings.ai.model,
    )


async def require_ai_extraction_enabled(
    feature_flag_service: FeatureFlagService = Depends(get_feature_flag_service),
) -> None:
    if not await feature_flag_service.is_enabled(AI_EXTRACTION_FEATURE_FLAG):
        raise ForbiddenError(
            "AI document extraction is not enabled", error_code="ai_extraction_disabled"
        )
