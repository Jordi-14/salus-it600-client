# Changelog

## 0.4.4 - 2026-04-29

Device metadata:

- Mark RS600/SR600 cover devices as Home Assistant `shutter` covers.

## 0.4.3 - 2026-04-29

P3 command reliability:

- Retry a transient gateway server disconnect once for encrypted write requests.
  Read requests are not retried, and writes still fail after the single retry.

## 0.4.2 - 2026-04-29

P2 maintainability:

- Add higher-level SQ610 client write methods for setpoint, HVAC mode, and
  preset/hold state so Home Assistant does not need to pass raw gateway
  property names.
- Remove the public raw SQ610 property write helper; SQ610 writes now go through
  semantic client methods only.
- Split gateway detail payload parsing into device-family modules under
  `salus_it600.parsers`.
- Add realistic JSON payload fixtures and parser regression tests for SQ610,
  FC600, TRV3RF, WLS600, TS600, SPE600, and RS600 devices.
- Document the model-shape decision to keep public device models as
  `NamedTuple` classes for now.

## 0.4.1 - 2026-04-29

P1 near-term hardening:

- Normalize ongoing gateway request failures before decrypting responses:
  non-200 HTTP responses now raise `IT600ConnectionError`, fixed-length gateway
  protocol frames now raise `IT600UnsupportedFirmwareError`, and decrypt
  failures now raise `IT600CommandError`.
- Add unit coverage for ongoing request HTTP errors, protocol frames, and
  decrypt failures.
- Add a GitHub issue form for client protocol, parsing, and command support
  reports.

P0 release hardening for the current `salus-it600-client 0.4.0` client line.

- Require the full Ruff check in CI instead of only syntax-critical rules.
- Require strict mypy in CI and the PyPI publish workflow.
- Tighten protocol connect typing by validating decrypted protocol responses
  are JSON objects before returning them.
