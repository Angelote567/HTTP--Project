from __future__ import annotations

import time
from dataclasses import dataclass, field
from email.utils import formatdate, parsedate_to_datetime
from threading import Lock
from typing import Dict, List, Optional

from .http_messages import Response


@dataclass
class Cookie:
    name: str
    value: str
    expires_at: Optional[float] = None
    path: str = "/"

    def is_expired(self, now: Optional[float] = None) -> bool:
        if self.expires_at is None:
            return False
        return (now if now is not None else time.time()) >= self.expires_at

    def matches_path(self, request_path: str) -> bool:
        if self.path == "/":
            return True
        if request_path == self.path:
            return True
        return request_path.startswith(self.path.rstrip("/") + "/")


def format_set_cookie(
    name: str,
    value: str,
    max_age: Optional[int] = None,
    expires: Optional[float] = None,
    path: str = "/",
) -> str:
    parts = [f"{name}={value}"]
    if max_age is not None:
        parts.append(f"Max-Age={int(max_age)}")
    if expires is not None:
        parts.append(f"Expires={formatdate(expires, usegmt=True)}")
    parts.append(f"Path={path}")
    return "; ".join(parts)


def add_set_cookie(response: Response, header_value: str) -> None:
    response.set_cookies.append(header_value)


def parse_request_cookies(header_value: Optional[str]) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    if not header_value:
        return cookies
    for piece in header_value.split(";"):
        piece = piece.strip()
        if not piece or "=" not in piece:
            continue
        name, value = piece.split("=", 1)
        cookies[name.strip()] = value.strip()
    return cookies


def parse_set_cookie(header_value: str) -> Optional[Cookie]:
    parts = [p.strip() for p in header_value.split(";") if p.strip()]
    if not parts:
        return None
    if "=" not in parts[0]:
        return None
    name, value = parts[0].split("=", 1)
    cookie = Cookie(name=name.strip(), value=value.strip())
    for attr in parts[1:]:
        if "=" in attr:
            key, val = attr.split("=", 1)
            key = key.strip().lower()
            val = val.strip()
        else:
            key = attr.strip().lower()
            val = ""
        if key == "max-age":
            try:
                cookie.expires_at = time.time() + int(val)
            except ValueError:
                continue
        elif key == "expires" and cookie.expires_at is None:
            try:
                cookie.expires_at = parsedate_to_datetime(val).timestamp()
            except (TypeError, ValueError):
                continue
        elif key == "path":
            cookie.path = val or "/"
    return cookie


class CookieJar:
    def __init__(self) -> None:
        self._lock = Lock()
        self._cookies: Dict[tuple[str, str, str], Cookie] = {}

    def store(self, host: str, set_cookie_values: List[str]) -> None:
        with self._lock:
            for raw in set_cookie_values:
                cookie = parse_set_cookie(raw)
                if cookie is None:
                    continue
                if cookie.is_expired():
                    self._cookies.pop((host, cookie.path, cookie.name), None)
                    continue
                self._cookies[(host, cookie.path, cookie.name)] = cookie

    def header_for(self, host: str, path: str) -> Optional[str]:
        now = time.time()
        with self._lock:
            stale = [
                key for key, cookie in self._cookies.items()
                if cookie.is_expired(now)
            ]
            for key in stale:
                self._cookies.pop(key, None)

            matching = [
                cookie for (h, _, _), cookie in self._cookies.items()
                if h == host and cookie.matches_path(path)
            ]
        if not matching:
            return None
        return "; ".join(f"{c.name}={c.value}" for c in matching)

    def clear(self) -> None:
        with self._lock:
            self._cookies.clear()
