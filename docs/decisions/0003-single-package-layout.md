# ADR 0003: One Python package with clear modules, not a multi-package monorepo

Date: 2026-09-14. Status: accepted.

## Context
RagFabric uses `packages/{core,server,cli,sdk-python,sdk-typescript}`. Loomrun is smaller and has
one consumer surface: the proxy process. A multi-package layout adds build and import complexity
before there is anything to separate.

## Decision
A single `loomrun` package under `src/` with modules per concern (proxy, queue, scheduler,
governor, ledger, engine, telemetry, cli, mcp). The admin SDK lives in `sdk/python/` and the
console in `console/` because they are separate deployables.

## Consequences
- Simpler to learn and hold in one head, which is the point of the project.
- If a real external consumer needs the scheduler or ledger as a library, that triggers a new ADR
  to split.
