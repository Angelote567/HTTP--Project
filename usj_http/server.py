"""Servidor HTTP/1.1 básico construido sobre sockets TCP.

Versión inicial con CRUD en memoria para gatos y owners.
"""

from __future__ import annotations

import argparse
import json
import re
import socketserver
from typing import Optional
from urllib.parse import urlsplit

from .http_messages import HTTPParseError, make_json_response
from .parser import parse_request, recv_http_message
from .store import CatStore, OwnerStore


CAT_STORE = CatStore()
OWNER_STORE = OwnerStore()


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class HTTPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        try:
            raw_request = recv_http_message(self.request)
            request = parse_request(raw_request)
            response = dispatch(
                request.method,
                urlsplit(request.target).path,
                request.headers,
                request.body,
            )
        except HTTPParseError as exc:
            response = make_json_response(400, {"error": str(exc)})
        except Exception as exc:  # pragma: no cover
            response = make_json_response(500, {"error": f"Error interno: {exc}"})
        self.request.sendall(response.to_bytes())


def dispatch(method: str, path: str, headers: dict, body: bytes):
    if path == "/cats":
        if method == "GET":
            return make_json_response(200, {"items": CAT_STORE.list_all()})
        if method == "POST":
            payload = parse_json_body(headers, body)
            validate_cat_payload(payload)
            ensure_owner_exists(payload.get("owner_id"))
            created = CAT_STORE.create(payload)
            response = make_json_response(201, created)
            response.headers["Location"] = f"/cats/{created['id']}"
            return response
        return method_not_allowed(["GET", "POST"])

    if path.startswith("/cats/"):
        item_id = parse_resource_id(path, "/cats/")
        if item_id is None:
            return make_json_response(404, {"error": "Recurso no encontrado"})
        if method == "GET":
            item = CAT_STORE.get(item_id)
            return make_json_response(200, item) if item else make_json_response(404, {"error": "Recurso no encontrado"})
        if method == "PUT":
            payload = parse_json_body(headers, body)
            validate_cat_payload(payload)
            ensure_owner_exists(payload.get("owner_id"))
            item = CAT_STORE.update(item_id, payload)
            return make_json_response(200, item) if item else make_json_response(404, {"error": "Recurso no encontrado"})
        if method == "DELETE":
            deleted = CAT_STORE.delete(item_id)
            return make_json_response(204, None) if deleted else make_json_response(404, {"error": "Recurso no encontrado"})
        return method_not_allowed(["GET", "PUT", "DELETE"])

    if path == "/owners":
        if method == "GET":
            return make_json_response(200, {"items": OWNER_STORE.list_all()})
        if method == "POST":
            payload = parse_json_body(headers, body)
            validate_owner_payload(payload)
            created = OWNER_STORE.create(payload)
            response = make_json_response(201, created)
            response.headers["Location"] = f"/owners/{created['id']}"
            return response
        return method_not_allowed(["GET", "POST"])

    nested_match = re.fullmatch(r"/owners/(\d+)/cats", path)
    if nested_match:
        owner_id = int(nested_match.group(1))
        if not OWNER_STORE.exists(owner_id):
            return make_json_response(404, {"error": "Owner no encontrado"})
        if method == "GET":
            return make_json_response(200, {"items": CAT_STORE.list_all(owner_id=owner_id)})
        return method_not_allowed(["GET"])

    if path.startswith("/owners/"):
        item_id = parse_resource_id(path, "/owners/")
        if item_id is None:
            return make_json_response(404, {"error": "Recurso no encontrado"})
        if method == "GET":
            item = OWNER_STORE.get(item_id)
            return make_json_response(200, item) if item else make_json_response(404, {"error": "Recurso no encontrado"})
        if method == "PUT":
            payload = parse_json_body(headers, body)
            validate_owner_payload(payload)
            item = OWNER_STORE.update(item_id, payload)
            return make_json_response(200, item) if item else make_json_response(404, {"error": "Recurso no encontrado"})
        if method == "DELETE":
            removed = OWNER_STORE.delete(item_id)
            if not removed:
                return make_json_response(404, {"error": "Recurso no encontrado"})
            CAT_STORE.delete_by_owner(item_id)
            return make_json_response(204, None)
        return method_not_allowed(["GET", "PUT", "DELETE"])

    return make_json_response(404, {"error": "Ruta no encontrada"})


def parse_json_body(headers: dict, body: bytes) -> dict:
    content_type = headers.get("Content-Type", "")
    if "application/json" not in content_type.lower():
        raise HTTPParseError("El cuerpo debe enviarse como application/json")
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPParseError(f"JSON inválido: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise HTTPParseError("El JSON debe ser un objeto")
    return payload


def validate_cat_payload(payload: dict) -> None:
    required = {"name": str, "breed": str, "age": int}
    for key, expected_type in required.items():
        if key not in payload:
            raise HTTPParseError(f"Falta el campo obligatorio: {key}")
        if not isinstance(payload[key], expected_type):
            raise HTTPParseError(f"El campo {key} debe ser de tipo {expected_type.__name__}")
    if payload["age"] < 0:
        raise HTTPParseError("El campo age no puede ser negativo")
    if "owner_id" in payload and payload["owner_id"] is not None and not isinstance(payload["owner_id"], int):
        raise HTTPParseError("El campo owner_id debe ser entero o null")


def validate_owner_payload(payload: dict) -> None:
    required = {"name": str, "email": str}
    for key, expected_type in required.items():
        if key not in payload:
            raise HTTPParseError(f"Falta el campo obligatorio: {key}")
        if not isinstance(payload[key], expected_type):
            raise HTTPParseError(f"El campo {key} debe ser de tipo {expected_type.__name__}")
    if "@" not in payload["email"]:
        raise HTTPParseError("El campo email no es válido")


def ensure_owner_exists(owner_id) -> None:
    if owner_id is None:
        return
    if not OWNER_STORE.exists(owner_id):
        raise HTTPParseError(f"No existe owner con id {owner_id}")


def parse_resource_id(path: str, prefix: str) -> Optional[int]:
    rest = path[len(prefix):]
    if "/" in rest:
        return None
    try:
        return int(rest)
    except ValueError:
        return None


def method_not_allowed(allowed_methods: list[str]):
    response = make_json_response(405, {"error": "Método no permitido"})
    response.headers["Allow"] = ", ".join(allowed_methods)
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor HTTP/1.1 básico con sockets TCP")
    parser.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    parser.add_argument("--port", type=int, default=8080, help="Puerto de escucha")
    args = parser.parse_args()

    with ThreadingTCPServer((args.host, args.port), HTTPHandler) as server:
        print(f"Servidor escuchando en http://{args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Servidor detenido")


if __name__ == "__main__":
    main()
