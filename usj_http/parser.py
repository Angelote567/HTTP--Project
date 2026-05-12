from __future__ import annotations

from typing import Dict
from .http_messages import HTTPParseError, Request, Response


MAX_HEADER_BYTES = 64 * 1024


def _split_head_body(data: bytes) -> tuple[bytes, bytes]:
    marker = b"\r\n\r\n"
    idx = data.find(marker)
    if idx == -1:
        raise HTTPParseError("No se encontró el final de cabeceras")
    return data[:idx], data[idx + len(marker):]


def parse_headers(lines: list[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for line in lines:
        if not line:
            continue
        if ":" not in line:
            raise HTTPParseError(f"Cabecera inválida: {line!r}")
        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def parse_request(data: bytes) -> Request:
    head, body = _split_head_body(data)
    lines = head.decode("iso-8859-1").split("\r\n")
    if not lines:
        raise HTTPParseError("Petición vacía")
    try:
        method, target, version = lines[0].split(" ", 2)
    except ValueError as exc:
        raise HTTPParseError("Línea de petición inválida") from exc
    headers = parse_headers(lines[1:])
    content_length = int(headers.get("Content-Length", "0"))
    if len(body) != content_length:
        raise HTTPParseError("El cuerpo no coincide con Content-Length")
    return Request(method=method.upper(), target=target, version=version, headers=headers, body=body)


def parse_response(data: bytes) -> Response:
    head, body = _split_head_body(data)
    lines = head.decode("iso-8859-1").split("\r\n")
    try:
        version, status_code, reason = lines[0].split(" ", 2)
    except ValueError as exc:
        raise HTTPParseError("Línea de estado inválida") from exc
    headers: dict[str, str] = {}
    set_cookies: list[str] = []
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            raise HTTPParseError(f"Cabecera inválida: {line!r}")
        name, value = line.split(":", 1)
        name = name.strip()
        value = value.strip()
        if name.lower() == "set-cookie":
            set_cookies.append(value)
        else:
            headers[name] = value
    content_length = int(headers.get("Content-Length", "0"))
    if len(body) != content_length:
        raise HTTPParseError("El cuerpo no coincide con Content-Length")
    return Response(
        version=version,
        status_code=int(status_code),
        reason=reason,
        headers=headers,
        body=body,
        set_cookies=set_cookies,
    )


def recv_http_message(sock) -> bytes:
    data = bytearray()
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data.extend(chunk)
        if len(data) > MAX_HEADER_BYTES:
            raise HTTPParseError("Cabeceras demasiado grandes")

    marker = b"\r\n\r\n"
    idx = data.find(marker)
    if idx == -1:
        raise HTTPParseError("No se recibieron cabeceras completas")

    head = data[:idx]
    rest = data[idx + len(marker):]
    header_text = head.decode("iso-8859-1")
    content_length = 0
    for line in header_text.split("\r\n")[1:]:
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break

    while len(rest) < content_length:
        chunk = sock.recv(4096)
        if not chunk:
            break
        rest.extend(chunk)

    return bytes(head + marker + rest)
