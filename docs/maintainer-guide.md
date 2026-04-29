# Maintainer Guide

## Adding a Device Model

1. Identify the model signature from a gateway `readall` summary and `deviceid` detail payload.
2. Add model constants or classification rules in `salus_it600/device_models.py`.
3. Add or update parser tests with a real-ish detail payload.
4. Update the parser implementation in the matching `salus_it600/parsers/` module.
5. Confirm the Home Assistant entity mapping still works for the new model.

## Adding a Climate Variant

1. Add client parser coverage first.
2. Add Home Assistant state-mapping tests for the exposed climate behavior.
3. Add public client write methods if the variant needs new write fields.
4. Keep raw gateway details out of Home Assistant entity classes when possible.

## Parser Expectations

Parsers should prefer partial device snapshots over dropping a device entirely when the missing field is optional. Required identity fields, such as `UniID`, can still reject malformed payloads. Optional telemetry, such as current temperature, should become `None` when the gateway does not provide it.

When a payload needs a defensive fallback, add a focused test that captures the exact malformed or partial payload shape. Avoid broad behavior changes without a fixture that explains why the parser needs the fallback.

## Device Model Shape

The public device models remain `NamedTuple` classes for now. They are immutable enough for callers, support the existing `_replace()` test and update pattern, and avoid a migration churn that does not currently remove parser complexity.

Reconsider frozen dataclasses when the model layer needs computed fields, validation, or many optional protocol attributes that make positional tuple behavior actively harmful.

## Home Assistant Boundary

The Home Assistant integration should use public `IT600Gateway` methods. If the integration needs a protocol behavior that is not exposed by the client, add a narrow public client method and test the request payload there.

Climate read-side interpretation belongs in `custom_components/salus/_climate_state.py`; entity classes should remain thin adapters between Home Assistant and the client model.
