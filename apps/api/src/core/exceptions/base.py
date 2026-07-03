class ApplicationError(Exception):
    """Base class for all application-level errors. Carries an HTTP-agnostic status code."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if error_code:
            self.error_code = error_code


class NotFoundError(ApplicationError):
    status_code = 404
    error_code = "not_found"


class ConflictError(ApplicationError):
    status_code = 409
    error_code = "conflict"


class ValidationError(ApplicationError):
    status_code = 422
    error_code = "validation_error"


class UnauthorizedError(ApplicationError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(ApplicationError):
    status_code = 403
    error_code = "forbidden"


class LockedError(ApplicationError):
    """423 Locked — resource is temporarily locked (e.g. too many failed PIN attempts)."""

    status_code = 423
    error_code = "locked"
