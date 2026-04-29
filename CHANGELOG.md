# Changelog

## Unreleased

P0 release hardening for the current `salus-it600-client 0.4.0` client line.

- Require the full Ruff check in CI instead of only syntax-critical rules.
- Require strict mypy in CI and the PyPI publish workflow.
- Tighten protocol connect typing by validating decrypted protocol responses
  are JSON objects before returning them.

Before publishing the next client release, bump both `pyproject.toml` and
`salus_it600/__version__.py`, then update `homeassistant_salus` to pin that
published client version.
