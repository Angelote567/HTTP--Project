from __future__ import annotations

import time

from usj_http.cookies import (
    CookieJar,
    format_set_cookie,
    parse_request_cookies,
    parse_set_cookie,
)


def test_format_set_cookie_includes_attributes():
    header = format_set_cookie("token", "abc", max_age=3600, path="/api")
    assert header.startswith("token=abc")
    assert "Max-Age=3600" in header
    assert "Path=/api" in header


def test_parse_request_cookies():
    cookies = parse_request_cookies("a=1; b=2; c=hello%20world")
    assert cookies == {"a": "1", "b": "2", "c": "hello%20world"}


def test_parse_set_cookie_with_max_age():
    cookie = parse_set_cookie("session=xyz; Max-Age=10; Path=/")
    assert cookie is not None
    assert cookie.name == "session"
    assert cookie.value == "xyz"
    assert cookie.path == "/"
    assert cookie.expires_at is not None
    assert cookie.expires_at > time.time()


def test_cookie_jar_path_scoping():
    jar = CookieJar()
    jar.store("example.com", ["root=1; Path=/", "scoped=2; Path=/api"])
    assert jar.header_for("example.com", "/") == "root=1"
    header = jar.header_for("example.com", "/api/users") or ""
    assert "root=1" in header
    assert "scoped=2" in header


def test_cookie_jar_expiry():
    jar = CookieJar()
    jar.store("example.com", ["short=1; Max-Age=0"])
    assert jar.header_for("example.com", "/") is None
