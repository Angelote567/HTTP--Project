from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urlsplit
import json

CRLF = "\r\n"


class HTTPParseError(Exception):
    """Raised when an HTTP message is malformed."""


@dataclass
class Request:
    method: str
    target: str
    version: str = "HTTP/1.1"
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def to_bytes(self) -> bytes:
        start_line = f"{self.method} {self.target} {self.version}{CRLF}"
        header_lines = "".join(f"{k}: {v}{CRLF}" for k, v in self.headers.items())
        return (start_line + header_lines + CRLF).encode("utf-8") + self.body


@dataclass
class Response:
    version: str
    status_code: int
    reason: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    set_cookies: List[str] = field(default_factory=list)

    def to_bytes(self) -> bytes:
        start_line = f"{self.version} {self.status_code} {self.reason}{CRLF}"
        header_lines = "".join(f"{k}: {v}{CRLF}" for k, v in self.headers.items())
        cookie_lines = "".join(f"Set-Cookie: {v}{CRLF}" for v in self.set_cookies)
        return (start_line + header_lines + cookie_lines + CRLF).encode("utf-8") + self.body

    @property
    def status_line(self) -> str:
        return f"{self.version} {self.status_code} {self.reason}"


HTTP_REASONS = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    415: "Unsupported Media Type",
    500: "Internal Server Error",
}


def make_json_response(status_code: int, payload: Optional[dict]) -> Response:
    body = b"" if payload is None else json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    headers = {
        "Server": "USJPythonHTTP/1.0",
        "Connection": "close",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        headers["Content-Length"] = str(len(body))
    else:
        headers["Content-Length"] = "0"
    return Response("HTTP/1.1", status_code, HTTP_REASONS[status_code], headers, body)


def make_text_response(status_code: int, text: str, content_type: str = "text/plain; charset=utf-8") -> Response:
    body = text.encode("utf-8")
    headers = {
        "Server": "USJPythonHTTP/1.0",
        "Connection": "close",
        "Content-Type": content_type,
        "Content-Length": str(len(body)),
    }
    return Response("HTTP/1.1", status_code, HTTP_REASONS[status_code], headers, body)


def parse_url(url: str) -> tuple[str, int, str]:
    parts = urlsplit(url)
    if parts.scheme.lower() != "http":
        raise ValueError("Solo se soporta el esquema http:// en esta base obligatoria.")
    host = parts.hostname
    if not host:
        raise ValueError("La URL debe incluir host.")
    port = parts.port or 80
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"
    return host, port, path
