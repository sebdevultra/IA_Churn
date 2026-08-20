from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.app.core.logging import logger


class AppBaseException(Exception):
    """Base exception for application domain errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DuplicateInteractionError(AppBaseException):
    """Raised when an incoming interaction has already been processed or ingested."""
    def __init__(self, message: str = "Interaction has already been ingested (duplicate hash detected)", hash_val: str = ""):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT, details={"interaction_hash": hash_val})


class EmptyContentError(AppBaseException):
    """Raised when interaction content is empty or contains only whitespace."""
    def __init__(self, message: str = "Interaction content cannot be empty or whitespace only."):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ResourceNotFoundError(AppBaseException):
    """Raised when a requested entity does not exist."""
    def __init__(self, resource_name: str, resource_id: any):
        super().__init__(
            message=f"{resource_name} with identifier '{resource_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource_name, "id": str(resource_id)}
        )


class AIProcessingError(AppBaseException):
    """Raised when AI provider fails and retries are exhausted."""
    def __init__(self, message: str, provider: str = "", details: dict = None):
        super().__init__(
            message=f"AI Processing failed: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"provider": provider, **(details or {})}
        )


class InvalidStateTransitionError(AppBaseException):
    """Raised when attempting an invalid state transition on alerts or interactions."""
    def __init__(self, current_state: str, requested_state: str):
        super().__init__(
            message=f"Cannot transition from state '{current_state}' to '{requested_state}'.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"current_state": current_state, "requested_state": requested_state}
        )


async def app_exception_handler(request: Request, exc: AppBaseException):
    """Global handler for domain exceptions."""
    logger.warning(f"Domain error handled: {exc.message} (status: {exc.status_code}) - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Global catch-all exception handler to avoid leaking internal stack traces."""
    logger.exception(f"Unhandled internal server error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred while processing your request. Please check server logs.",
                "details": {}
            }
        }
    )
