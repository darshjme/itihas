"""LogHandler — abstract base handler."""

from abc import ABC, abstractmethod
from .record import LogRecord


class LogHandler(ABC):
    """Base handler; subclasses implement emit()."""

    def __init__(self, level: str = "DEBUG") -> None:
        self._level: str = level.upper()

    @property
    def level(self) -> str:
        return self._level

    @level.setter
    def level(self, value: str) -> None:
        self._level = value.upper()

    def handle(self, record: LogRecord) -> None:
        """Pass *record* to emit() if its level meets the threshold."""
        if LogRecord.LEVELS.get(record.level, 0) >= LogRecord.LEVELS.get(self._level, 0):
            self.emit(record)

    @abstractmethod
    def emit(self, record: LogRecord) -> None:
        """Write / store the record. Must be overridden."""
