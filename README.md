# agent-log

**Structured JSON logging for LLM agents.** Zero dependencies. Python ≥ 3.10.

Stop grepping through walls of text. Every agent decision becomes a queryable, filterable, correlation-traceable JSON record.

---

## Installation

```bash
pip install agent-log
```

---

## Quick Start

```python
from agent_log import AgentLogger, InMemoryHandler

# Basic structured logging
logger = AgentLogger("my-agent", level="DEBUG", correlation_id="req-42")

logger.info("Agent started", model="gpt-4o", task="summarise")
logger.debug("Calling tool", tool="web_search", query="structured logging python")
logger.warning("Rate limit approaching", remaining=5)
logger.error("Tool call failed", tool="web_search", status=429)
```

Each call prints to stdout:

```json
{"timestamp": 1711234567.89, "level": "INFO", "logger": "my-agent", "message": "Agent started", "correlation_id": "req-42", "model": "gpt-4o", "task": "summarise"}
{"timestamp": 1711234568.01, "level": "DEBUG", "logger": "my-agent", "message": "Calling tool", "correlation_id": "req-42", "tool": "web_search", "query": "structured logging python"}
```

---

## Bind Persistent Fields

```python
step_logger = logger.bind(step=1, agent_version="2.0")
step_logger.info("Reasoning started")   # always has step=1, agent_version="2.0"
step_logger.info("Reasoning complete", tokens_used=312)
```

---

## Correlation IDs

```python
request_logger = logger.with_correlation("trace-abc-123")
request_logger.info("Processing request")
request_logger.error("Unexpected tool output", tool="calculator")
```

---

## In-Memory Handler (for testing)

```python
from agent_log import AgentLogger, InMemoryHandler

handler = InMemoryHandler(level="DEBUG")
logger = AgentLogger("agent", level="DEBUG")
logger.add_handler(handler)

logger.info("step 1", phase="planning")
logger.error("step 2 failed", phase="execution", code=500)

# Filter by level
errors = handler.filter(level="ERROR")
assert errors[0].fields["code"] == 500

# Filter by correlation ID
from agent_log import AgentLogger, InMemoryHandler
h = InMemoryHandler()
a = AgentLogger("svc"); a.add_handler(h)
b = a.with_correlation("run-99")
b.info("started"); b.info("done")
run_records = h.filter(correlation_id="run-99")
assert len(run_records) == 2
```

---

## API Reference

### `AgentLogger(name, level="INFO", correlation_id=None)`

| Method | Description |
|--------|-------------|
| `debug/info/warning/error/critical(msg, **fields)` | Log at given level with optional context fields |
| `bind(**fields) -> AgentLogger` | New logger with fields always attached |
| `with_correlation(id) -> AgentLogger` | New logger with fixed correlation_id |
| `add_handler(handler)` | Attach a `LogHandler`; if none attached, logs to stdout |

### `LogRecord`

| Attribute | Type | Description |
|-----------|------|-------------|
| `timestamp` | `float` | `time.time()` at creation |
| `level` | `str` | Uppercase level string |
| `message` | `str` | Log message |
| `logger_name` | `str` | Logger name |
| `fields` | `dict` | Extra context fields |
| `correlation_id` | `str \| None` | Correlation/trace ID |
| `to_dict()` | `dict` | Flat dict (JSON-serialisable) |
| `to_json()` | `str` | JSON string |

### `InMemoryHandler(level="DEBUG", max_size=1000)`

| Method | Description |
|--------|-------------|
| `records` | All stored `LogRecord`s |
| `filter(level=None, correlation_id=None)` | Filtered subset |
| `clear()` | Wipe all records |

---

## License

MIT
