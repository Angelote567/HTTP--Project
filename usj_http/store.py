from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional


class CatStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._items: Dict[int, dict] = {
            1: {"id": 1, "name": "Hercules", "breed": "European", "age": 3, "owner_id": 1},
            2: {"id": 2, "name": "Nina", "breed": "Siamese", "age": 2, "owner_id": 2},
        }
        self._next_id = 3

    def list_all(self, owner_id: Optional[int] = None) -> List[dict]:
        with self._lock:
            items = [self._items[k].copy() for k in sorted(self._items)]
        if owner_id is None:
            return items
        return [item for item in items if item.get("owner_id") == owner_id]

    def get(self, item_id: int) -> Optional[dict]:
        with self._lock:
            item = self._items.get(item_id)
            return None if item is None else item.copy()

    def create(self, payload: dict) -> dict:
        with self._lock:
            item = {"id": self._next_id, **payload}
            self._items[self._next_id] = item
            self._next_id += 1
            return item.copy()

    def update(self, item_id: int, payload: dict) -> Optional[dict]:
        with self._lock:
            if item_id not in self._items:
                return None
            self._items[item_id] = {"id": item_id, **payload}
            return self._items[item_id].copy()

    def delete(self, item_id: int) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None

    def delete_by_owner(self, owner_id: int) -> int:
        with self._lock:
            target_ids = [k for k, item in self._items.items() if item.get("owner_id") == owner_id]
            for k in target_ids:
                self._items.pop(k, None)
            return len(target_ids)


class OwnerStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._items: Dict[int, dict] = {
            1: {"id": 1, "name": "Ángel", "email": "angel@example.com"},
            2: {"id": 2, "name": "Marta", "email": "marta@example.com"},
        }
        self._next_id = 3

    def list_all(self) -> List[dict]:
        with self._lock:
            return [self._items[k].copy() for k in sorted(self._items)]

    def get(self, item_id: int) -> Optional[dict]:
        with self._lock:
            item = self._items.get(item_id)
            return None if item is None else item.copy()

    def exists(self, item_id: int) -> bool:
        with self._lock:
            return item_id in self._items

    def create(self, payload: dict) -> dict:
        with self._lock:
            item = {"id": self._next_id, **payload}
            self._items[self._next_id] = item
            self._next_id += 1
            return item.copy()

    def update(self, item_id: int, payload: dict) -> Optional[dict]:
        with self._lock:
            if item_id not in self._items:
                return None
            self._items[item_id] = {"id": item_id, **payload}
            return self._items[item_id].copy()

    def delete(self, item_id: int) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None


class UserSessionStore:
    """Simple in-memory store for cookie-based sessions."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: Dict[str, dict] = {}

    def create(self, session_id: str, data: dict) -> None:
        with self._lock:
            self._sessions[session_id] = data

    def get(self, session_id: str) -> Optional[dict]:
        with self._lock:
            data = self._sessions.get(session_id)
            return None if data is None else dict(data)

    def delete(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None
