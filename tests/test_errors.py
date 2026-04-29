import asyncio
from fastapi import HTTPException
from starlette.requests import Request

from app.errors import _status_name, error_response, generic_exception_handler, http_exception_handler


def _request(path: str) -> Request:
    return Request({"type": "http", "method": "GET", "path": path, "headers": [], "scheme": "http", "server": ("testserver", 80)})


def test_error_response_uses_expected_payload():
    response = error_response(400, "Bad Request", "bad input", "/tokenize")

    assert response.status_code == 400
    assert response.body == (
        b'{"status":400,"error":"Bad Request","message":"bad input","path":"/tokenize"}'
    )


def test_http_exception_handler_formats_response():
    response = asyncio.run(
        http_exception_handler(
            _request("/detokenize"),
            HTTPException(status_code=404, detail="Token not found"),
        )
    )

    assert response.status_code == 404
    assert response.body == (
        b'{"status":404,"error":"Not Found","message":"Token not found","path":"/detokenize"}'
    )


def test_generic_exception_handler_hides_internal_details():
    response = asyncio.run(
        generic_exception_handler(_request("/tokenize"), RuntimeError("boom"))
    )

    assert response.status_code == 500
    assert response.body == (
        b'{"status":500,"error":"Internal Server Error","message":"Unexpected server error","path":"/tokenize"}'
    )


def test_status_name_falls_back_to_error():
    assert _status_name(418) == "Error"
