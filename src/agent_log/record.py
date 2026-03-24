"""LogRecord — a single structured log entry."""

import json
import time
from typing import Optional


class LogRecord:
    """A single structured log entry."""

    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def __init__(
        self,
        level: str,
        message: str,
        logger_name: str,
        fields: Optional[dict] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.timestamp: float = time.time()
        self.level: str = level.upper()
        self.message: str = message
        self.logger_name: str = logger_name
        self.fields: dict = dict(fields) if fields else {}
        self.correlation_id: Optional[str] = correlation_id

    def to_dict(self) -> dict:
        """Return record as a plain dict (JSON-serialisable)."""
        d: dict = {
            "timestamp": self.timestamp,
            "level": self.level,
            "logger": self.logger_name,
            "message": self.message,
            "correlation_id": self.correlation_id,
        }
        d.update(self.fields)
        return d

    def to_json(self) -> str:
        """Return record serialised as a JSON string."""
        return json.dumps(self.to_dict())

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LogRecord level={self.level} message={self.message!r}>"
