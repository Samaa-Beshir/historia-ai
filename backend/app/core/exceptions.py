"""Standardized exception hierarchy.

Services and the AI layer raise these; the API layer's exception handlers
(see app.main) translate them into consistent JSON error responses so no
route needs its own try/except business logic.
"""


class HistoriaError(Exception):
    """Base class for all application errors."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(HistoriaError):
    status_code = 404
    code = "not_found"


class ValidationFailedError(HistoriaError):
    status_code = 422
    code = "validation_failed"


class RetrievalError(HistoriaError):
    status_code = 502
    code = "retrieval_failed"


class LLMProviderError(HistoriaError):
    status_code = 502
    code = "llm_provider_failed"


class ConfigurationError(HistoriaError):
    status_code = 500
    code = "configuration_error"


class RateLimitExceededError(HistoriaError):
    status_code = 429
    code = "rate_limit_exceeded"


class UnauthorizedError(HistoriaError):
    status_code = 401
    code = "unauthorized"
