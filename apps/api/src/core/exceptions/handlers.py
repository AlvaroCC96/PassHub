from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions.base import ApplicationError
from src.core.logging import get_logger

logger = get_logger(__name__)


def _error_response(status_code: int, error_code: str, message: str, request: Request) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        logger.warning("application_error", error_code=exc.error_code, message=exc.message)
        return _error_response(exc.status_code, exc.error_code, exc.message, request)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error", str(exc.errors()), request
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception")
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "Internal server error", request
        )
