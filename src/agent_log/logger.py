"""AgentLogger — structured JSON logger for LLM agents."""

import json
import sys
from typing import Optional
from .record import LogRecord
from .handler import LogHandler


class AgentLogger:
    """
    Structured JSON logger.  Writes to stdout by default; attach handlers
    via add_handler() to direct output elsewhere.
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        correlation_id: Optional[str] = None,
    ) -> None:
        self._name: str = name
        self._level: str = level.upper()
        self._correlation_id: Optional[str] = correlation_id
        self._bound_fields: dict = {}
        self._handlers: list[LogHandler] = []

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def add_handler(self, handler: LogHandler) -> None:
        self._handlers.append(handler)

    def remove_handler(self, handler: LogHandler) -> None:
        self._handlers.remove(handler)

    # ------------------------------------------------------------------
    # Derived-logger factories
    # ------------------------------------------------------------------

    def bind(self, **fields) -> "AgentLogger":
        """Return a new logger with *fields* always attached to every record."""
        child = AgentLogger(self._name, self._level, self._correlation_id)
        child._bound_fields = {**self._bound_fields, **fields}
        child._handlers = self._handlers  # share handlers
        return child

    def with_correlation(self, id: str) -> "AgentLogger":
        """Return a new logger with the given *correlation_id*."""
        child = AgentLogger(self._name, self._level, id)
        child._bound_fields = dict(self._bound_fields)
        child._handlers = self._handlers  # share handlers
        return child

    # ------------------------------------------------------------------
    # Logging methods
    # ------------------------------------------------------------------

    def _log(self, level: str, message: str, **fields) -> None:
        if LogRecord.LEVELS.get(level, 0) < LogRecord.LEVELS.get(self._level, 0):
            return
        merged = {**self._bound_fields, **fields}
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self._name,
            fields=merged,
            correlation_id=self._correlation_id,
        )
        if self._handlers:
            for handler in self._handlers:
                handler.handle(record)
        else:
            print(record.to_json(), file=sys.stdout, flush=True)

    def debug(self, message: str, **fields) -> None:
        self._log("DEBUG", message, **fields)

    def info(self, message: str, **fields) -> None:
        self._log("INFO", message, **fields)

    def warning(self, message: str, **fields) -> None:
        self._log("WARNING", message, **fields)

    def error(self, message: str, **fields) -> None:
        self._log("ERROR", message, **fields)

    def critical(self, message: str, **fields) -> None:
        self._log("CRITICAL", message, **fields)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> str:
        return self._level

    @level.setter
    def level(self, value: str) -> None:
        self._level = value.upper()

    @property
    def correlation_id(self) -> Optional[str]:
        return self._correlation_id
