"""Small in-memory limiter for costly failed decryption attempts."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class AttemptLimiter:
    def __init__(self, maximum: int = 6, window_seconds: int = 300):
        self.maximum = maximum
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allowed(self, identity: str) -> bool:
        now = time.monotonic()
        with self._lock:
            attempts = self._attempts[identity]
            while attempts and attempts[0] <= now - self.window_seconds:
                attempts.popleft()
            return len(attempts) < self.maximum

    def failed(self, identity: str) -> None:
        with self._lock:
            self._attempts[identity].append(time.monotonic())

    def clear(self, identity: str) -> None:
        with self._lock:
            self._attempts.pop(identity, None)
