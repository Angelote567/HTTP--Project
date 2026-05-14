from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .http_messages import Request, Response


@dataclass
class RequestContext:
    method: str
    target: str
    path: str
    headers: Dict[str, str]
    body: bytes
    state: Dict[str, object] = field(default_factory=dict)


Handler = Callable[[RequestContext], Response]
Middleware = Callable[[RequestContext, Handler], Response]


class MiddlewareChain:
    def __init__(self) -> None:
        self._middlewares: List[Middleware] = []

    def use(self, middleware: Middleware) -> None:
        self._middlewares.append(middleware)

    def clear(self) -> None:
        self._middlewares.clear()

    def run(self, ctx: RequestContext, final_handler: Handler) -> Response:
        def build(index: int) -> Handler:
            if index >= len(self._middlewares):
                return final_handler
            current = self._middlewares[index]

            def call(c: RequestContext) -> Response:
                return current(c, build(index + 1))

            return call

        return build(0)(ctx)
