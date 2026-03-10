"""
Central session management for document processing.
Handles in-memory storage, expiration, and cleanup.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from mcp_lektor.config.settings import get_settings
from mcp_lektor.config.models import SessionConfig

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Thread-safe manager for document sessions.
    
    In a production multi-worker environment, this should be replaced
    by a Redis or database-backed store (see DEV_OPEN_QUESTIONS-0001).
    """
    
    def __init__(self, config: SessionConfig | None = None):
        # Use provided config or load from global settings
        self._config = config or get_settings().session
        self._lock = threading.Lock()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._cleanup_task: asyncio.Task | None = None

    def create_session(self, data: dict[str, Any]) -> str:
        """
        Initialize a new session with provided data.
        Returns a unique session_id.
        """
        session_id = uuid4().hex
        with self._lock:
            self._sessions[session_id] = {
                **data,
                "created_at": datetime.now(timezone.utc),
                "last_accessed": datetime.now(timezone.utc),
            }
        logger.info(f"Created session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any]:
        """
        Retrieve session data by ID. 
        Updates 'last_accessed' timestamp.
        Raises KeyError if session is missing or expired.
        """
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Session not found: {session_id}")
            
            session = self._sessions[session_id]
            # Check expiration manually as a safety measure
            if self._is_expired(session):
                del self._sessions[session_id]
                raise KeyError(f"Session expired: {session_id}")
            
            session["last_accessed"] = datetime.now(timezone.utc)
            return session

    def update_session(self, session_id: str, data: dict[str, Any]) -> None:
        """Merge new data into the existing session."""
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Session not found: {session_id}")
            self._sessions[session_id].update(data)
            self._sessions[session_id]["last_accessed"] = datetime.now(timezone.utc)

    def delete_session(self, session_id: str) -> None:
        """Remove a session from the store."""
        with self._lock:
            self._sessions.pop(session_id, None)
        logger.info(f"Deleted session: {session_id}")

    def list_sessions(self) -> list[str]:
        """Return list of all active session IDs."""
        with self._lock:
            return [
                sid for sid, s in self._sessions.items() 
                if not self._is_expired(s)
            ]

    def _is_expired(self, session: dict[str, Any]) -> bool:
        """Check if a single session has exceeded its TTL."""
        expiry_limit = datetime.now(timezone.utc) - timedelta(minutes=self._config.ttl_minutes)
        # Use last_accessed for sliding window expiration, or created_at for fixed.
        # Design choice: sliding window.
        return session.get("last_accessed", datetime.min.replace(tzinfo=timezone.utc)) < expiry_limit

    async def start_cleanup_task(self, interval_seconds: int | None = None):
        """
        Background task to periodically prune expired sessions.
        Should be started during server initialization.
        """
        if self._cleanup_task:
            return
        
        interval = interval_seconds or self._config.cleanup_interval_seconds
        logger.info(f"Starting background session cleanup task (interval: {interval}s).")
        self._cleanup_task = asyncio.create_task(self._run_cleanup_loop(interval))

    async def _run_cleanup_loop(self, interval: int):
        while True:
            try:
                await asyncio.sleep(interval)
                self.prune_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup loop: {e}")

    def prune_expired(self) -> int:
        """Remove all expired sessions. Returns count of removed sessions."""
        count = 0
        with self._lock:
            expired_ids = [
                sid for sid, s in self._sessions.items() 
                if self._is_expired(s)
            ]
            for sid in expired_ids:
                del self._sessions[sid]
                count += 1
        
        if count > 0:
            logger.info(f"Pruned {count} expired sessions.")
        return count

# Global instance for easy access across tools
# In a more complex app, this would be injected via dependency injection
session_manager = SessionManager()
