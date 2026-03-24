"""22+ pytest tests for the agent-log library."""

import json
import time
import pytest

from agent_log import AgentLogger, LogRecord, LogHandler, InMemoryHandler


# ---------------------------------------------------------------------------
# LogRecord tests
# ---------------------------------------------------------------------------


def test_record_basic_fields():
    r = LogRecord("INFO", "hello", "mylogger")
    assert r.level == "INFO"
    assert r.message == "hello"
    assert r.logger_name == "mylogger"
    assert r.fields == {}
    assert r.correlation_id is None


def test_record_timestamp_is_float():
    before = time.time()
    r = LogRecord("DEBUG", "ts", "l")
    after = time.time()
    assert before <= r.timestamp <= after


def test_record_level_uppercased():
    r = LogRecord("warning", "msg", "l")
    assert r.level == "WARNING"


def test_record_fields_stored():
    r = LogRecord("ERROR", "boom", "svc", fields={"code": 500, "path": "/api"})
    assert r.fields["code"] == 500
    assert r.fields["path"] == "/api"


def test_record_fields_not_mutated():
    original = {"x": 1}
    r = LogRecord("INFO", "m", "l", fields=original)
    r.fields["x"] = 99
    assert original["x"] == 1  # original dict unchanged


def test_record_to_dict_structure():
    r = LogRecord("INFO", "hi", "app", fields={"agent": "gpt4"}, correlation_id="abc")
    d = r.to_dict()
    assert d["level"] == "INFO"
    assert d["message"] == "hi"
    assert d["logger"] == "app"
    assert d["correlation_id"] == "abc"
    assert d["agent"] == "gpt4"
    assert "timestamp" in d


def test_record_to_json_valid():
    r = LogRecord("DEBUG", "test", "x")
    raw = r.to_json()
    parsed = json.loads(raw)
    assert parsed["level"] == "DEBUG"


def test_record_to_json_contains_fields():
    r = LogRecord("INFO", "msg", "l", fields={"k": "v"}, correlation_id="cid-1")
    parsed = json.loads(r.to_json())
    assert parsed["k"] == "v"
    assert parsed["correlation_id"] == "cid-1"


# ---------------------------------------------------------------------------
# InMemoryHandler tests
# ---------------------------------------------------------------------------


def test_inmemory_stores_record():
    h = InMemoryHandler()
    r = LogRecord("INFO", "stored", "l")
    h.handle(r)
    assert len(h.records) == 1


def test_inmemory_level_filtering():
    h = InMemoryHandler(level="WARNING")
    h.handle(LogRecord("DEBUG", "ignored", "l"))
    h.handle(LogRecord("WARNING", "kept", "l"))
    assert len(h.records) == 1
    assert h.records[0].message == "kept"


def test_inmemory_max_size_evicts_oldest():
    h = InMemoryHandler(max_size=3)
    for i in range(5):
        h.handle(LogRecord("INFO", f"msg{i}", "l"))
    assert len(h.records) == 3
    assert h.records[0].message == "msg2"


def test_inmemory_clear():
    h = InMemoryHandler()
    h.handle(LogRecord("INFO", "x", "l"))
    h.clear()
    assert h.records == []


def test_inmemory_filter_by_level():
    h = InMemoryHandler()
    h.handle(LogRecord("INFO", "a", "l"))
    h.handle(LogRecord("ERROR", "b", "l"))
    errors = h.filter(level="ERROR")
    assert len(errors) == 1
    assert errors[0].message == "b"


def test_inmemory_filter_by_correlation_id():
    h = InMemoryHandler()
    h.handle(LogRecord("INFO", "x", "l", correlation_id="req-1"))
    h.handle(LogRecord("INFO", "y", "l", correlation_id="req-2"))
    result = h.filter(correlation_id="req-1")
    assert len(result) == 1
    assert result[0].message == "x"


def test_inmemory_filter_combined():
    h = InMemoryHandler()
    h.handle(LogRecord("ERROR", "e1", "l", correlation_id="req-1"))
    h.handle(LogRecord("INFO", "i1", "l", correlation_id="req-1"))
    h.handle(LogRecord("ERROR", "e2", "l", correlation_id="req-2"))
    result = h.filter(level="ERROR", correlation_id="req-1")
    assert len(result) == 1
    assert result[0].message == "e1"


def test_inmemory_records_returns_copy():
    h = InMemoryHandler()
    h.handle(LogRecord("INFO", "x", "l"))
    snapshot = h.records
    snapshot.clear()
    assert len(h.records) == 1  # original unaffected


# ---------------------------------------------------------------------------
# AgentLogger tests
# ---------------------------------------------------------------------------


def test_logger_basic_info(capsys):
    logger = AgentLogger("test")
    logger.info("hello world")
    out = capsys.readouterr().out
    parsed = json.loads(out.strip())
    assert parsed["message"] == "hello world"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test"


def test_logger_level_suppresses_debug(capsys):
    logger = AgentLogger("test", level="INFO")
    logger.debug("should not appear")
    out = capsys.readouterr().out
    assert out.strip() == ""


def test_logger_bind_attaches_fields():
    h = InMemoryHandler()
    logger = AgentLogger("svc")
    logger.add_handler(h)
    bound = logger.bind(agent="gpt4", env="prod")
    bound.info("decision made")
    rec = h.records[0]
    assert rec.fields["agent"] == "gpt4"
    assert rec.fields["env"] == "prod"


def test_logger_bind_does_not_modify_original():
    h = InMemoryHandler()
    logger = AgentLogger("svc")
    logger.add_handler(h)
    bound = logger.bind(extra="yes")
    logger.info("original")
    assert "extra" not in h.records[0].fields


def test_logger_with_correlation():
    h = InMemoryHandler()
    logger = AgentLogger("svc")
    logger.add_handler(h)
    corr = logger.with_correlation("trace-xyz")
    corr.info("traced")
    assert h.records[0].correlation_id == "trace-xyz"


def test_logger_all_levels():
    h = InMemoryHandler(level="DEBUG")
    logger = AgentLogger("svc", level="DEBUG")
    logger.add_handler(h)
    logger.debug("d")
    logger.info("i")
    logger.warning("w")
    logger.error("e")
    logger.critical("c")
    levels = [r.level for r in h.records]
    assert levels == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_logger_extra_fields_in_record():
    h = InMemoryHandler()
    logger = AgentLogger("svc")
    logger.add_handler(h)
    logger.info("action taken", step=3, tool="search")
    rec = h.records[0]
    assert rec.fields["step"] == 3
    assert rec.fields["tool"] == "search"


def test_logger_correlation_id_in_output(capsys):
    logger = AgentLogger("svc", correlation_id="c-99")
    logger.info("msg")
    out = capsys.readouterr().out
    parsed = json.loads(out.strip())
    assert parsed["correlation_id"] == "c-99"


def test_loghandler_abstract_emit():
    """LogHandler.emit must be abstract — cannot instantiate directly."""
    with pytest.raises(TypeError):
        LogHandler()  # type: ignore


def test_inmemory_handler_default_max_size():
    h = InMemoryHandler()
    assert h._max_size == 1000
