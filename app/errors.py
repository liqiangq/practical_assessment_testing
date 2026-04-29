from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


def error_response(status: int, error: str, message: str, path: str):
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "error": error,
            "message": message,
            "path": path,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        status=exc.status_code,
        error=_status_name(exc.status_code),
        message=str(exc.detail),
        path=request.url.path,
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return error_response(
        status=HTTP_500_INTERNAL_SERVER_ERROR,
        error="Internal Server Error",
        message="Unexpected server error",
        path=request.url.path,
    )


def _status_name(status_code: int) -> str:
    mapping = {
        400: "Bad Request",
        404: "Not Found",
        500: "Internal Server Error",
    }
    return mapping.get(status_code, "Error")
