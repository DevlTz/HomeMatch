class HomeMatchException(Exception):
    """Base class for all project exceptions."""
    pass
class ResourceNotFound(HomeMatchException):
    pass
class PermissionDenied(HomeMatchException):
    pass
class ExternalServiceError(HomeMatchException):
    """Errors from external services: R2, AI, email."""
    pass
class ValidationError(HomeMatchException):
    pass
class AuthenticationError(HomeMatchException):
    pass
class AuthorizationError(HomeMatchException):
    pass
class ConflictError(HomeMatchException):
    pass
class ConfigurationError(HomeMatchException):
    pass
class ExternalServiceTimeout(ExternalServiceError):
    pass
class DatabaseError(HomeMatchException):
    pass
class RateLimitExceeded(HomeMatchException):
    pass