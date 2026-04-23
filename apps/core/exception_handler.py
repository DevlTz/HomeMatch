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
    # Deixa o DRF tratar o que ele já conhece (JWT, ValidationError, etc.)
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ResourceNotFound):
        return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, (AuthenticationError,)):
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
        logger.warning("Timeout em serviço externo: %s", exc)
        return Response(
            {"error": "Serviço externo demorou demais. Tente novamente."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, ExternalServiceError):
        logger.error("Erro de serviço externo: %s", exc)
        return Response(
            {"error": "Serviço externo indisponível. Tente novamente."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, ConfigurationError):
        logger.critical("Erro de configuração: %s", exc)
        return Response(
            {"error": "Erro de configuração do servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, DatabaseError):
        logger.error("Erro de banco de dados: %s", exc)
        return Response(
            {"error": "Erro interno. Tente novamente mais tarde."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Qualquer coisa não tratada — loga e retorna 500 limpo
    logger.exception("Erro não tratado: %s", exc)
    return Response(
        {"error": "Erro interno. Tente novamente mais tarde."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )