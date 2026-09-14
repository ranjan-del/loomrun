# Contributing

Loomrun is at the planning stage. Discussion and issues are welcome; code contributions become
useful from v0.1.0.

## Ground rules
Read [docs/working-agreement.md](docs/working-agreement.md) first.

- Every capability enters through a roadmap phase whose measurement asked for it. Propose the
  measurement first.
- No number in any document unless it came from a real run, with the hardware named.
- No feature described as shipped unless `ROADMAP.md` marks it shipped.
- Decisions get an ADR in `docs/decisions/`.

## Pull requests
Fork, branch, open a pull request against `main`. CI (ruff, mypy, pytest) must pass. Keep one
change per pull request and say which roadmap phase it belongs to.

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
