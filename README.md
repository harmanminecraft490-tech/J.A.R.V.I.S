# J.A.R.V.I.S — Autonomous AI PC Agent

A modular Windows desktop agent built around the loop:

**LISTEN → UNDERSTAND → PLAN → OBSERVE → ACT → VERIFY → RECOVER → CONTINUE → COMPLETE**

## Architecture

- `core/` — agent orchestration, planning, task state, memory
- `vision/` — screen capture and observation abstractions
- `computer/` — mouse, keyboard, windows, processes
- `tools/` — filesystem, terminal, browser, system capabilities
- `voice/` — replaceable voice provider adapters
- `ui/` — dashboard
- `config/` — environment and runtime configuration
- `tests/` — automated validation
- `docs/` — architecture and engineering notes

## Safety

Computer control is mediated by a risk/permission layer. Emergency stop must halt queued non-critical computer-control actions. Credentials and secrets are never committed.

## Development

The first implementation milestone focuses on a dependable Windows control/observation core, structured actions, task state, logging, configuration, and tests before adding higher-level autonomy.
