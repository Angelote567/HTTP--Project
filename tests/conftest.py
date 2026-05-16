from __future__ import annotations

import socket
import threading
import time
from typing import Iterator, Optional

import pytest

from usj_http import server as server_module
from usj_http.client import HTTPClient
from usj_http.cookies import CookieJar


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_listening(host: str, port: int, timeout: float = 3.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"The server did not accept connections on {host}:{port}")


def _start_server(api_key: Optional[str] = None) -> tuple[server_module.ThreadingTCPServer, threading.Thread, str]:
    server_module.CAT_STORE = server_module.CatStore()
    server_module.OWNER_STORE = server_module.OwnerStore()
    server_module.SESSIONS.clear()
    server_module.configure_chain(api_key)

    host = "127.0.0.1"
    port = _free_port()
    server = server_module.ThreadingTCPServer((host, port), server_module.HTTPHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    _wait_until_listening(host, port)
    return server, thread, f"http://{host}:{port}"


@pytest.fixture
def base_url() -> Iterator[str]:
    server, thread, url = _start_server()
    try:
        yield url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)


@pytest.fixture
def secured_setup() -> Iterator[tuple[str, str]]:
    api_key = "test-key-123"
    server, thread, url = _start_server(api_key=api_key)
    try:
        yield url, api_key
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)


@pytest.fixture
def client() -> HTTPClient:
    return HTTPClient(cookie_jar=CookieJar())
