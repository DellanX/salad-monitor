# `salad-logparse` Library Crate Specification

`salad-logparse` is a pure, zero-side-effect parsing library for Salad Bowl logs.

## Modules:
- `tailer`: Incremental file reader with file rotation and shrink detection.
- `parser`: Compiled regex pattern matchers for the 12 Salad log event signatures.
- `state_machine`: Workload state machine tracking pull progress, layer digests, ETA estimates, and wallet balances.
