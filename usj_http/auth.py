from __future__ import annotations

from typing import Iterable, Optional

from .http_messages import Response, make_json_response


API_KEY_HEADER = "X-API-Key"


def check_api_key(
    headers: dict,
    path: str,
    expected_key: Optional[str],
    public_paths: Optional[Iterable[str]] = None,
) -> Optional[Response]:
    """Comprueba la API key en la cabecera ``X-API-Key``.

    Devuelve ``None`` si la petición está autorizada o si no hay ``expected_key``
    configurada. Si la clave falta o no coincide, devuelve una respuesta 401.
    """
    if not expected_key:
        return None
    public = set(public_paths or [])
    if path in public:
        return None
    provided = headers.get(API_KEY_HEADER) or headers.get(API_KEY_HEADER.lower())
    if provided != expected_key:
        response = make_json_response(401, {"error": "API key inválida o ausente"})
        response.headers["WWW-Authenticate"] = f'ApiKey header="{API_KEY_HEADER}"'
        return response
    return None
