# Contributing

Loomrun is at the planning stage. Discussion and issues are welcome; code contributions become
useful from v0.1.0.

## Ground rules
- Every capability enters through a roadmap phase whose measurement asked for it. Propose the
  measurement first.
- No number in any document unless it came from a real run, with the hardware named.
- No feature described as shipped unless `ROADMAP.md` marks it shipped.
- Decisions get an ADR in `docs/decisions/`.

## Development
```
make setup      # python 3.12 via uv, all dependencies
make check      # ruff, mypy, pytest
make stack      # Postgres and Redis in Docker (from Phase 1)
```
Ollama runs on the host, not in Docker, so it can use the GPU.

## Style
Plain language in docs. Small modules with one purpose. Type hints everywhere; `mypy --strict`
passes. Commits describe why, not just what.
