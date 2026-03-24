"""InMemoryHandler — stores LogRecords in a list (ideal for testing)."""

from typing import Optional
from .handler import LogHandler
from .record import LogRecord


class InMemoryHandler(LogHandler):
    """Stores up to *max_size* records in memory."""

    def __init__(self, level: str = "DEBUG", max_size: int = 1000) -> None:
        super().__init__(level)
        self._max_size: int = max_size
        self._records: list[LogRecord] = []

    @property
    def records(self) -> list[LogRecord]:
        """All stored records (read-only view)."""
        return list(self._records)

    def emit(self, record: LogRecord) -> None:
        if len(self._records) >= self._max_size:
            self._records.pop(0)
        self._records.append(record)

    def filter(
        self,
        level: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> list[LogRecord]:
        """Return records matching *level* and/or *correlation_id*."""
        result = self._records
        if level is not None:
            target = level.upper()
            result = [r for r in result if r.level == target]
        if correlation_id is not None:
            result = [r for r in result if r.correlation_id == correlation_id]
        return list(result)

    def clear(self) -> None:
        """Remove all stored records."""
        self._records.clear()
