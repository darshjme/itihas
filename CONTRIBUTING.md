# Contributing to agent-log

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/your-org/agent-log
cd agent-log
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v --cov=agent_log
```

## Guidelines

- Keep runtime dependencies at zero — stdlib only.
- All new features need tests.
- Follow PEP 8.  Type-annotate all public APIs.
- Open an issue before large changes.

## Pull Requests

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Commit with clear messages.
4. Open a PR against `main`.
