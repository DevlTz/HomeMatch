import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from .exceptions import (
    ResourceNotFound,
    ExternalServiceError,
    ExternalServiceTimeout,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ConfigurationError,
    DatabaseError,
    RateLimitExceeded,
)

logger = logging.getLogger(__name__)
def homematch_exception_handler(exc, context):
    # Let DRF handle exceptions it already knows (JWT, ValidationError, etc.)
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ResourceNotFound):
        return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, AuthenticationError):
        return Response({"error": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, AuthorizationError):
        return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, ConflictError):
        return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)

    if isinstance(exc, ValidationError):
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, RateLimitExceeded):
        return Response({"error": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    if isinstance(exc, ExternalServiceTimeout):
        logger.warning("External service timeout: %s", exc)
        return Response(
            {"error": "External service took too long. Please try again."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, ExternalServiceError):
        logger.error("External service error: %s", exc)
        return Response(
            {"error": "External service unavailable. Please try again."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, ConfigurationError):
        logger.critical("Configuration error: %s", exc)
        return Response(
            {"error": "Server configuration error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, DatabaseError):
        logger.error("Database error: %s", exc)
        return Response(
            {"error": "Internal error. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Any unhandled exception — log it and return a clean 500
    logger.exception("Unhandled error: %s", exc)
    return Response(
        {"error": "Internal error. Please try again later."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
