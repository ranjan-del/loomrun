# Roadmap

Full plan with learning goals, exercises and exit criteria: [docs/plan.md](docs/plan.md).
Target hardware: Apple M1, 16 GB, Ollama on Metal (ADR 0004). All numbers are single-machine numbers.

| Release | Phases | Headline |
|---|---|---|
| v0.1.0 | 0, 1, 2 | Drop-in proxy with ledger, queue and Grafana |
| v0.2.0 | 3, 4 | Reliable and fair |
| v0.3.0 | 5 | Swap-aware |
| v0.4.0 | 6 | Governor, console, MCP |
| v1.0.0 | 7 plus hardening | Multi-worker |

Legend: `[x]` shipped on main, `[~]` in progress, `[ ]` not started.

Phases 0 to 6 run on a single machine. Phase 7 needs a second machine or container.
Each phase ends with a measured before-and-after result recorded under `docs/benchmarks/`.

## Phase 0: Landscape and baseline
- [~] `docs/landscape.md`: drafted from documentation on 2026-09-14; tested facts still to add
- [x] `docs/problem.md`: one page problem statement and non-goals
- [~] Install Ollama (done, 0.34.0), pull tiny, small and medium models (in progress)
- [ ] Load test script against bare Ollama (`bench/`), written by the engineer as the Phase 0 exercise
- [ ] Baseline numbers on the target hardware: time to first token, tokens per second, p50 and p95 latency at 1, 4 and 16 concurrent clients

## Phase 1: Pass-through proxy with a ledger
- [ ] Async proxy exposing the engine's own API and forwarding unchanged, streaming included
- [ ] Ledger in PostgreSQL: caller, model, tokens in and out, duration, outcome
- [ ] Ollama native and OpenAI-compatible surfaces both proxied, API keys per caller
- [ ] Structured JSON logs with request id
- [ ] `loomrun serve`, `loomrun ledger`, Compose `lite` profile
- [ ] Measured: overhead added by the proxy

## Phase 2: Queue and admission control
- [ ] Redis queue, fixed pool of workers
- [ ] Bounded queue, reject or delay when full
- [ ] Worker heartbeats
- [ ] Prometheus `/metrics`, Grafana provisioning, Compose `observe` profile, `loomrun status`
- [ ] Measured: throughput and p95 under overload with and without admission control

## Phase 3: Timeouts, cancellation, retries
- [ ] Per-request deadlines
- [ ] Client disconnect cancels the worker's engine call
- [ ] Retry only on retryable errors, exponential backoff with jitter, idempotency keys
- [ ] OpenTelemetry spans per request
- [ ] Measured: tokens wasted on cancelled requests before and after

## Phase 4: Priority and fair share
- [ ] Callers and priorities in configuration
- [ ] Interactive requests ahead of batch, no caller above its share
- [ ] `loomrun callers`, Python admin SDK
- [ ] Measured: interactive p95 while a batch job runs

## Phase 5: Swap-aware placement
- [ ] Track loaded models, load times, memory per model
- [ ] Group same-model requests, avoid thrash
- [ ] `loomrun models`, `docs/concepts/kv-cache.md`
- [ ] Measured: model swaps per minute and throughput with and without placement

## Phase 6: Governor, console, MCP
- [ ] Per-caller token and time budgets
- [ ] Degradation ladder: smaller model, shorter context, stop with partial result and reason
- [ ] `loomrun budgets`
- [ ] Angular and Tailwind console over ledger and status
- [ ] MCP server exposing status, ledger, budgets, models, bench
- [ ] Measured: hard failures turned into completed degraded requests

## Phase 7: Second worker
- [ ] Two engines on two machines or containers
- [ ] Task ownership with leases, dead worker detection, placement across both
- [ ] vLLM adapter (CUDA machine) or second Ollama container, `loomrun workers`
- [ ] Measured: aggregate throughput and behaviour when one worker dies

## v1.0.0 hardening
- [ ] End-to-end tests, rate limits, input validation, release automation, docs site

## Later, optional
- Kubernetes deployment, TypeScript SDK generated from OpenAPI, more engines.
