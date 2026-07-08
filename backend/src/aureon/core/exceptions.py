from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AureonError(Exception):
    """Base class for domain-level errors raised anywhere below the API layer."""

    status_code: int = 500
    message: str = "Internal error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class NotFoundError(AureonError):
    status_code = 404
    message = "Resource not found"


class ConfidenceGateError(AureonError):
    """Raised when an operation attempts to bypass the confidence safety floor."""

    status_code = 409
    message = "Blocked by confidence safety gate"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AureonError)
    async def handle_aureon_error(_: Request, exc: AureonError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
