# ADR 0004: Target hardware is the engineer's Apple M1 with 16 GB; Python pinned to 3.12

Date: 2026-09-14. Status: accepted.

## Context
Measured on 2026-09-14: MacBook Pro, Apple M1, 8 cores, 16 GB unified memory, Metal GPU. Docker,
uv, PostgreSQL 16 and Node 26 installed. System Python is 3.14. Ollama and Redis not installed.

## Decision
- All Phase 0 to 6 measurements run on this machine with Ollama on Metal. Reports name it.
- Model set: a tiny, a small and a medium model so that swap pressure exists within 16 GB.
- Python pinned to 3.12 via uv for library compatibility.
- Redis, Prometheus and Grafana run in Docker Compose; PostgreSQL also in Compose for
  reproducibility even though a local install exists.
- vLLM is deferred to Phase 7 because it needs a CUDA GPU this machine does not have.

## Consequences
- The project is fully buildable and measurable without cloud spend through v0.4.0.
- Numbers are single-machine, Apple Silicon numbers. The README and every report say so.
