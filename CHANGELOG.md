# Changelog

All notable changes to **agent-log** are documented here.

## [1.0.0] — 2026-03-24

### Added
- `AgentLogger` — structured JSON logger with `debug/info/warning/error/critical` methods
- `bind(**fields)` — derives a child logger with permanently attached context fields
- `with_correlation(id)` — derives a child logger with a fixed correlation ID
- `LogRecord` — immutable single log entry with `to_dict()` / `to_json()`
- `LogHandler` — abstract base handler with level-gating via `handle()`
- `InMemoryHandler` — in-memory store with `filter()` by level or correlation ID
- Zero runtime dependencies (stdlib only: `json`, `time`, `sys`)
- Full pytest test suite (22+ tests)
