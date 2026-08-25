from dataclasses import dataclass
from fastapi import Request
from fastapi.responses import JSONResponse


@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400
    field_errors: dict | None = None


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "field_errors": exc.field_errors or {},
        },
    )
