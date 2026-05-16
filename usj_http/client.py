from __future__ import annotations

import argparse
import json
import os
import socket
from typing import Dict, Optional

from .auth import API_KEY_HEADER
from .cookies import CookieJar
from .http_messages import Request, parse_url
from .parser import parse_response, recv_http_message


DEFAULT_HEADERS = {
    "User-Agent": "USJPythonHTTPClient/1.0",
    "Accept": "*/*",
    "Connection": "close",
}


class HTTPClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        cookie_jar: Optional[CookieJar] = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_key = api_key
        self.cookies = cookie_jar or CookieJar()
        self.timeout = timeout

    def request(
        self,
        method: str,
        url: str,
        extra_headers: Optional[Dict[str, str]] = None,
        body_text: str = "",
    ):
        host, port, request = self._build_request(method, url, extra_headers or {}, body_text)
        with socket.create_connection((host, port), timeout=self.timeout) as sock:
            sock.sendall(request.to_bytes())
            raw_response = recv_http_message(sock)
        response = parse_response(raw_response)
        if response.set_cookies:
            self.cookies.store(host, response.set_cookies)
        return request, response

    def _build_request(
        self,
        method: str,
        url: str,
        extra_headers: Dict[str, str],
        body_text: str,
    ) -> tuple[str, int, Request]:
        host, port, target = parse_url(url)
        body = body_text.encode("utf-8") if body_text else b""
        headers = dict(DEFAULT_HEADERS)
        headers["Host"] = host if port == 80 else f"{host}:{port}"

        if body:
            headers["Content-Length"] = str(len(body))
            if "Content-Type" not in extra_headers:
                headers["Content-Type"] = "application/json; charset=utf-8"
        else:
            headers["Content-Length"] = "0"

        if self.api_key and API_KEY_HEADER not in extra_headers:
            headers[API_KEY_HEADER] = self.api_key

        cookie_header = self.cookies.header_for(host, target.split("?", 1)[0])
        if cookie_header:
            headers["Cookie"] = cookie_header

        headers.update(extra_headers)
        request = Request(method=method.upper(), target=target, headers=headers, body=body)
        return host, port, request


def print_exchange(request: Request, response) -> None:
    print("\n=== REQUEST ===")
    print(request.to_bytes().decode("utf-8", errors="replace"))
    print("=== RESPONSE STATUS ===")
    print(f"{response.status_code} {response.reason}")
    print("=== RESPONSE HEADERS ===")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
    for cookie_value in response.set_cookies:
        print(f"Set-Cookie: {cookie_value}")
    print("=== RESPONSE BODY ===")
    if not response.body:
        print("<empty>")
        return

    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            parsed = json.loads(response.body.decode("utf-8"))
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            return
        except json.JSONDecodeError:
            pass
    print(response.body.decode("utf-8", errors="replace"))


def parse_header_lines(raw_headers: str) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if not raw_headers.strip():
        return headers
    for line in raw_headers.split(","):
        if ":" not in line:
            raise ValueError(f"Invalid header: {line!r}")
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def interactive_loop(client: HTTPClient) -> None:
    print("Interactive HTTP client. Press Enter on URL to exit.\n")
    while True:
        url = input("URL (e.g. http://127.0.0.1:8080/cats): ").strip()
        if not url:
            print("Exiting...")
            break
        method = input("Method [GET/HEAD/POST/PUT/DELETE]: ").strip().upper() or "GET"
        raw_headers = input("Extra headers (format K:V,K:V) or empty: ").strip()
        body_text = input("Body (empty if not applicable): ").strip()
        try:
            headers = parse_header_lines(raw_headers)
            request, response = client.request(method, url, headers, body_text)
            print_exchange(request, response)
        except Exception as exc:
            print(f"Error sending the request: {exc}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic HTTP/1.1 client using TCP sockets")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--method", default="GET", help="HTTP method")
    parser.add_argument("--url", help="Full URL, e.g. http://127.0.0.1:8080/cats")
    parser.add_argument("--headers", default="", help="Extra headers K:V,K:V")
    parser.add_argument("--body", default="", help="Request body")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("USJ_HTTP_API_KEY"),
        help="API key. Also via env USJ_HTTP_API_KEY.",
    )
    args = parser.parse_args()

    client = HTTPClient(api_key=args.api_key)

    if args.interactive:
        interactive_loop(client)
        return

    if not args.url:
        parser.error("You must provide --url or use --interactive")

    extra_headers = parse_header_lines(args.headers)
    request, response = client.request(args.method, args.url, extra_headers, args.body)
    print_exchange(request, response)


if __name__ == "__main__":
    main()
