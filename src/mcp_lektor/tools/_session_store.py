"""In-memory session store for document processing sessions."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

_SESSION_TTL_MINUTES = 30

_lock = threading.Lock()
_store: dict[str, dict[str, Any]] = {}


def create_session(data: dict[str, Any]) -> str:
    """Create a new session, return its id."""
    session_id = uuid4().hex
    with _lock:
        _store[session_id] = {
            **data,
            "_created_at": datetime.utcnow(),
        }
    return session_id


def get_session(session_id: str) -> dict[str, Any]:
    """Return session data or raise KeyError."""
    _cleanup_expired()
    with _lock:
        if session_id not in _store:
            raise KeyError(f"Session not found: {session_id}")
        return _store[session_id]


def update_session(session_id: str, data: dict[str, Any]) -> None:
    """Merge *data* into an existing session."""
    with _lock:
        if session_id not in _store:
            raise KeyError(f"Session not found: {session_id}")
        _store[session_id].update(data)


def delete_session(session_id: str) -> None:
    """Remove a session (idempotent)."""
    with _lock:
        _store.pop(session_id, None)


def list_sessions() -> list[str]:
    """Return all active session ids."""
    _cleanup_expired()
    with _lock:
        return list(_store.keys())


def clear_all() -> None:
    """Remove every session – useful for tests."""
    with _lock:
        _store.clear()


def _cleanup_expired() -> None:
    cutoff = datetime.utcnow() - timedelta(minutes=_SESSION_TTL_MINUTES)
    with _lock:
        expired = [
            sid
            for sid, s in _store.items()
            if s.get("_created_at", datetime.min) < cutoff
        ]
        for sid in expired:
            del _store[sid]
