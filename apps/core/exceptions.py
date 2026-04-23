class HomeMatchException(Exception):
    """Base de todas as exceções do projeto."""
    pass

class ResourceNotFound(HomeMatchException):
    pass

class PermissionDenied(HomeMatchException):
    pass

class ExternalServiceError(HomeMatchException):
    """Erros de serviços externos: R2, IA, email."""
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