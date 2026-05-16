from __future__ import annotations

from usj_http.http_messages import make_json_response
from usj_http.middleware import MiddlewareChain, RequestContext


def make_ctx() -> RequestContext:
    return RequestContext(
        method="GET",
        target="/test",
        path="/test",
        headers={},
        body=b"",
    )


def test_chain_calls_in_order():
    order: list[str] = []

    def first(ctx, nxt):
        order.append("first-before")
        response = nxt(ctx)
        order.append("first-after")
        return response

    def second(ctx, nxt):
        order.append("second-before")
        response = nxt(ctx)
        order.append("second-after")
        return response

    def handler(ctx):
        order.append("handler")
        return make_json_response(200, {"ok": True})

    chain = MiddlewareChain()
    chain.use(first)
    chain.use(second)
    response = chain.run(make_ctx(), handler)

    assert response.status_code == 200
    assert order == [
        "first-before",
        "second-before",
        "handler",
        "second-after",
        "first-after",
    ]


def test_middleware_can_short_circuit():
    def deny(ctx, nxt):
        return make_json_response(401, {"error": "denied"})

    def handler(ctx):
        raise AssertionError("handler should not be called")

    chain = MiddlewareChain()
    chain.use(deny)
    response = chain.run(make_ctx(), handler)
    assert response.status_code == 401


def test_middleware_can_mutate_state():
    def tag(ctx, nxt):
        ctx.state["user"] = "alice"
        return nxt(ctx)

    def handler(ctx):
        assert ctx.state["user"] == "alice"
        return make_json_response(200, None)

    chain = MiddlewareChain()
    chain.use(tag)
    response = chain.run(make_ctx(), handler)
    assert response.status_code == 200
