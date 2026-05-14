from __future__ import annotations

from typing import Iterable, Optional

from .http_messages import Response, make_json_response
from .middleware import Handler, Middleware, RequestContext

API_KEY_HEADER = "X-API-Key"


def api_key_middleware(
    expected_key: Optional[str],
    public_paths: Optional[Iterable[str]] = None,
) -> Middleware:
    public = set(public_paths or [])

    def middleware(ctx: RequestContext, next_handler: Handler) -> Response:
        if not expected_key:
            return next_handler(ctx)
        if ctx.path in public:
            return next_handler(ctx)
        provided = ctx.headers.get(API_KEY_HEADER) or ctx.headers.get(API_KEY_HEADER.lower())
        if provided != expected_key:
            response = make_json_response(401, {"error": "API key inválida o ausente"})
            response.headers["WWW-Authenticate"] = f'ApiKey header="{API_KEY_HEADER}"'
            return response
        ctx.state["authenticated"] = True
        return next_handler(ctx)

    return middleware
