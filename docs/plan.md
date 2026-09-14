# Loomrun plan

Status: planning, 2026-09-14. This document is the full plan. `ROADMAP.md` is the short status
view. Nothing described here exists yet unless the roadmap marks it shipped.

## 1. Purpose

Learn the execution layer that sits under AI applications by building a small, measured,
documented tool that a small team can use: a scheduler and governor for one shared inference
machine running Ollama or vLLM.

## 2. Target hardware, measured on 2026-09-14

| Item | Value | Consequence |
|---|---|---|
| Machine | MacBook Pro, Apple M1, 8 cores (4 performance, 4 efficiency) | Ollama runs on the Metal GPU. Numbers are single-machine numbers and are reported as such. |
| Memory | 16 GB unified, shared between CPU and GPU | One 7B or 8B model at 4-bit fits (roughly 5 GB). Two such models do not fit comfortably alongside the OS. Swap pressure is real, which is exactly what Phase 5 needs to observe. |
| Installed | Docker 29, uv 0.11, PostgreSQL 16, Node 26 | Redis and Grafana run in Docker Compose. PostgreSQL can too, for reproducibility. |
| Missing | Ollama, Redis | Phase 0 installs Ollama. Redis arrives with Compose in Phase 2. |
| Python | 3.14 on the system | Pin 3.12 with `uv python install 3.12`. Several libraries lag the newest release. |

Model set for experiments (sizes approximate, confirm with `ollama list` after pulling):

| Role | Model | Why |
|---|---|---|
| Tiny | `qwen2.5:1.5b` | Fast, always fits. The degradation target in Phase 6. |
| Small | `llama3.2:3b` | Default interactive model. |
| Medium | `llama3.1:8b` or `qwen2.5:7b` | The one that forces swaps when combined with another. |

## 3. What gets built

Each component exists because a phase measures the problem it fixes.

| Component | Problem it fixes | Phase | What it teaches |
|---|---|---|---|
| Proxy | Apps need one address that speaks the engine's API and streams | 1 | Async HTTP, streaming, reverse proxies |
| Ledger | Nobody knows what each app used | 1 | Schema design for run records, PostgreSQL |
| Queue and workers | Engine accepts unlimited work and falls over | 2 | Producers and consumers, bounded concurrency, backpressure |
| Admission control | Callers need a fast "wait" or "no" instead of a slow failure | 2 | Load shedding, queue limits |
| Deadlines and cancellation | Work continues after the caller left | 3 | Cancel scopes, propagation, wasted work |
| Retry policy | Transient failures kill requests, synchronised retries cause a second wave | 3 | Error classification, backoff, jitter, idempotency |
| Scheduler policies | The batch job starves the chat | 4 | Priority queues, weighted fair share, starvation |
| Model placement | Two models thrash in memory | 5 | Model loading, memory, KV cache, batching |
| Governor | Runaway callers, no budgets, hard failures | 6 | Policy engines, pricing config, degradation, partial results |
| Multi-worker | One machine is not enough | 7 | Task ownership, heartbeats, dead worker detection |

## 4. Cross-cutting tracks

These are the parts that make it a real tool rather than a script. Each is placed where it first
becomes useful and cheap, and skipped where it would be decoration.

### 4.1 Observability

| Stage | What | Phase | Why here |
|---|---|---|---|
| Ledger | Every request as a row: caller, model, tokens, timings, outcome, retries, swaps | 1 | Needed before anything can be measured |
| Structured logs | JSON logs with request id and caller on every line | 1 | Cheap, and debugging Phase 2 without it is painful |
| Metrics | Prometheus endpoint: queue depth, in flight, wait time, latency histograms, swaps, rejections | 2 | The queue is the first thing you cannot see without metrics. Grafana via Compose gives dashboards for free. |
| Traces | OpenTelemetry spans: admission, wait, engine call, retries | 3 | Retries and cancellation are the first things that need a per-request timeline |
| Bench reports | `docs/benchmarks/<phase>-<topic>.md` with hardware, method, numbers, plotted from real runs | Every phase | The project's honesty contract |

### 4.2 CLI

`loomrun` command built with Typer, grows one verb per phase:

| Verb | Phase | Does |
|---|---|---|
| `loomrun bench` | 0 | Runs the load test and writes a report |
| `loomrun serve` | 1 | Starts the proxy |
| `loomrun ledger` | 1 | Queries the ledger: by caller, model, time window |
| `loomrun status` | 2 | Queue depth, workers, loaded models, in flight |
| `loomrun callers` | 4 | Manage callers, priorities, shares |
| `loomrun models` | 5 | Loaded models, load times, memory, placement decisions |
| `loomrun budgets` | 6 | Set and inspect budgets |
| `loomrun workers` | 7 | Worker list and health |

### 4.3 API compatibility

Applications do not use a Loomrun SDK to talk to models. They use the engine API they already
use, pointed at Loomrun. Two surfaces are proxied from Phase 1:

| Surface | Why |
|---|---|
| Ollama native (`/api/generate`, `/api/chat`, `/api/tags`) | Existing Ollama apps work unchanged |
| OpenAI-compatible (`/v1/chat/completions`, `/v1/models`) | Any OpenAI SDK app works unchanged, and vLLM exposes the same surface, so swapping the engine in Phase 7 is a config change |

Callers identify themselves with an API key issued by Loomrun. Priority and deadline travel as
headers with sensible defaults per caller.

### 4.4 Python SDK

A thin admin and inspection client, not a model client. Arrives in Phase 4 when there is something
to administer. Wraps the ledger, status, callers and budgets endpoints. A TypeScript SDK generated
from the OpenAPI spec is optional, after v1.0, only if the dashboard or a user needs it.

### 4.5 MCP server

An MCP server that exposes Loomrun's read and admin operations as tools: status, ledger queries,
budgets, placement decisions, bench trigger. Purpose: Claude Code, Codex or any MCP client can
inspect and operate the box in conversation. Arrives in Phase 6, once status, ledger, callers and
budgets all exist, so the tool set is complete on day one. Read tools are free; write tools
(budgets, callers) require a confirmation flag. Built with the official Python MCP SDK. Loomrun
does not itself proxy MCP traffic; that is a different problem.

### 4.6 Dashboard

| Stage | What | Phase |
|---|---|---|
| Grafana | Provisioned dashboards in Compose over the Prometheus metrics: queue, latency, swaps, per caller | 2 |
| Loomrun console | Angular and Tailwind app over the ledger and status API: live queue, callers and budgets, model placement timeline, bench history | 6 |

Grafana comes first because it costs one YAML file. The Angular console comes when there is
state that Grafana cannot show well: budgets, degradation decisions, placement reasoning.

### 4.7 Documentation

| Document | Written in |
|---|---|
| `docs/landscape.md` | Phase 0 |
| `docs/problem.md` | Phase 0 |
| `docs/concepts/<topic>.md` one per learning topic: backpressure, cancellation, jitter, fair share, KV cache, degradation | The phase that introduces it |
| `docs/architecture.md` | Phase 2, updated each phase |
| `docs/decisions/` ADRs | Whenever a decision is made |
| `docs/benchmarks/` | Every phase |
| `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md` | v0.1 release |

## 5. Repository layout

One Python package with clear modules. Splitting into several packages, as RagFabric did, is a
later ADR if a real consumer needs a separate package.

```
loomrun/
  src/loomrun/
    proxy/        HTTP surface, Ollama and OpenAI-compatible routes, streaming
    queue/        Redis queue, workers, heartbeats, admission
    scheduler/    priority, fair share, placement policies
    governor/     budgets, degradation ladder, pricing config
    ledger/       PostgreSQL models, migrations, queries
    engine/       Ollama and vLLM adapters, model inventory
    telemetry/    logging, metrics, tracing
    cli/          Typer commands
    mcp/          MCP server (Phase 6)
  sdk/python/     admin client (Phase 4)
  console/        Angular dashboard (Phase 6)
  bench/          load scripts and report generator
  deploy/         docker-compose.yml, Grafana provisioning, Dockerfiles
  docs/
  tests/
```

## 6. Technology and reasons

| Choice | Reason |
|---|---|
| Python 3.12, uv, ruff, mypy, pytest | Same toolchain as RagFabric. 3.12 for library compatibility. |
| Starlette or FastAPI with httpx | Async streaming proxy with minimal overhead. FastAPI for the admin API where validation matters. |
| Pydantic and YAML config | Configuration-driven callers, policies, budgets, pricing. Nothing hardcoded. |
| PostgreSQL | Durable ledger and state. Already installed and known. |
| Redis | Queue, worker heartbeats, loaded-model registry. One process, sufficient for one machine. See ADR 0002. |
| Typer | CLI |
| Prometheus client, Grafana, OpenTelemetry | Standard, self-hosted, no vendor |
| Docker Compose profiles | `lite`: Postgres, Redis, Loomrun. `observe`: adds Prometheus and Grafana. |
| Angular and Tailwind | Console, matching skills already built in RagFabric |
| Official Python MCP SDK | MCP server |
| Ollama first, vLLM in Phase 7 | Ollama runs on the M1. vLLM needs a CUDA GPU and arrives with the second worker. |

## 7. Phases

Every phase follows the same loop: learn, exercise, implement, review, integrate, test, measure,
document. Exit criteria must be met before the next phase starts.

### Phase 0: Landscape and baseline (no Loomrun code)

| | |
|---|---|
| Goal | Know what exists and how the bare engine behaves on this machine |
| Learn | How Ollama serves: `OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_LOADED_MODELS`, `OLLAMA_KEEP_ALIVE`, what the engine already does for concurrency and swapping. Time to first token vs tokens per second. Percentiles and why averages lie. |
| Exercise | Write a 40 to 60 line asyncio script: fire N concurrent chat requests at Ollama, record time to first token and total time per request, print p50 and p95 and tokens per second. Then alternate two models request by request and time the swaps. |
| Build | Install Ollama, pull the three models. `bench/` with the script and a markdown report generator. |
| Measure | Baseline at 1, 4, 16 concurrent clients for the small model. Swap cost between small and medium. |
| Document | `docs/landscape.md` with tested facts per tool. `docs/problem.md`. `docs/benchmarks/0-baseline.md`. |
| Exit | Baseline numbers exist with hardware named. Landscape shows exactly which gaps Ollama alone leaves. |

### Phase 1: Pass-through proxy and ledger

| | |
|---|---|
| Learn | Async HTTP servers and clients, chunked and SSE streaming, why a proxy must not buffer, request ids, structured logging, ledger schema design |
| Exercise | A minimal Starlette app that forwards one streaming endpoint to Ollama with httpx and prints per-request timing |
| Build | Proxy for both API surfaces. API keys per caller. Ledger table and migration. `loomrun serve`, `loomrun ledger`. Compose `lite`. |
| Measure | Proxy overhead per request vs baseline. Must be small and stated. |
| Exit | An OpenAI SDK app and an Ollama app both work through Loomrun unchanged. Every request is in the ledger. |

### Phase 2: Queue, workers, admission control

| | |
|---|---|
| Learn | Producers and consumers, bounded queues, why unbounded queues kill servers, backpressure, load shedding, heartbeats, Prometheus histograms |
| Exercise | In-memory asyncio queue with 3 workers and 50 producers, observe latency with and without a queue bound |
| Build | Redis queue, worker pool sized to the engine's parallelism, bounded queue with 429 or wait, heartbeats, `/metrics`, Grafana provisioning, `loomrun status` |
| Measure | Throughput and p95 at 16 and 50 clients with and without admission control |
| Exit | Overload produces fast rejections, not slow failures. Queue depth is visible in Grafana. |

### Phase 3: Deadlines, cancellation, retries

| | |
|---|---|
| Learn | Cancel scopes, cancellation propagation across the proxy to the engine, error classification, exponential backoff with jitter, idempotency keys, OpenTelemetry spans |
| Exercise | A coroutine chain where the client disconnects mid-stream. Prove the engine call stops. Simulate synchronised retries with and without jitter. |
| Build | Per-request deadline header with caller default, disconnect cancels the engine call, retry policy in config, idempotency key, OTel tracing |
| Measure | Tokens generated after the client left, before and after. Retry storm size with and without jitter. |
| Exit | No wasted generation on cancelled requests. Traces show admission, wait, call and retries per request. |

### Phase 4: Priority and fair share

| | |
|---|---|
| Learn | Priority queues, starvation, weighted fair queuing, deficit round robin, priority inversion |
| Exercise | Simulate two callers, one flooding and one interactive, under three policies: FIFO, strict priority, weighted fair. Plot interactive p95 for each. |
| Build | Callers with priority and share in config, scheduler policy module, `loomrun callers`, Python admin SDK |
| Measure | Interactive p95 while a batch flood runs, per policy |
| Exit | Chat stays fast under batch load and batch still progresses. |

### Phase 5: Swap-aware placement

| | |
|---|---|
| Learn | Model loading cost, unified memory, KV cache size and its dependence on context length, continuous batching, quantization trade-offs, how Ollama decides to evict |
| Exercise | Measure load time and memory for each of the three models. Compute how many concurrent requests at a given context length fit for each. |
| Build | Model inventory in Redis (loaded, load time, memory), placement policy that groups same-model work and avoids evicting a model with waiting requests, `loomrun models`, `docs/concepts/kv-cache.md` |
| Measure | Swaps per minute and total throughput with mixed small and medium traffic, with and without placement |
| Exit | Measurable drop in swaps with no loss of fairness from Phase 4. |

### Phase 6: Governor, console, MCP

| | |
|---|---|
| Learn | Policy engines, versioned pricing config, budget windows, degradation as a design principle, partial results with reasons, MCP tool design |
| Exercise | A budget policy as a pure function: given caller state and request, return allow, degrade with a step, or stop with a reason. Table-driven tests. |
| Build | Per-caller token and time budgets, degradation ladder (smaller model, shorter context, stop with partial and reason), `loomrun budgets`, Angular console, MCP server |
| Measure | Requests that would have failed hard vs completed degraded. Console and MCP show the same numbers as the ledger. |
| Exit | A runaway caller is contained without affecting others. Claude Code can inspect the box through MCP. |

### Phase 7: Second worker

| | |
|---|---|
| Learn | Task ownership and leases, at-least-once vs exactly-once, dead worker detection, placement across heterogeneous workers |
| Exercise | Two worker processes on one machine sharing a Redis queue. Kill one mid-request. Prove the request is re-owned exactly once. |
| Build | Worker registration, leases, dead worker recovery, engine adapter for vLLM on a CUDA machine or a second Ollama in a container, `loomrun workers` |
| Measure | Aggregate throughput with two workers. Behaviour and recovery time when one dies. |
| Exit | Two engines behind one Loomrun. Killing one loses no request. |

## 8. Releases

| Release | Phases | Headline |
|---|---|---|
| v0.1.0 | 0, 1, 2 | Drop-in proxy with ledger, queue and Grafana |
| v0.2.0 | 3, 4 | Reliable and fair |
| v0.3.0 | 5 | Swap-aware |
| v0.4.0 | 6 | Governor, console, MCP |
| v1.0.0 | 7 plus hardening: e2e tests, rate limits, input validation, release automation, docs site | Multi-worker, production ready for a small team |

## 9. How to start

1. Install Ollama and pull the three models.
2. Read how Ollama handles parallelism and loaded models. Write the findings into `docs/landscape.md`.
3. Do the Phase 0 exercise: the asyncio load script. You write it. Review follows.
4. Run the baseline and write `docs/benchmarks/0-baseline.md`.
5. Write `docs/problem.md` in your own words from the README.
6. Open the Phase 0 issue on GitHub with these five items and close it when they are done.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Ollama already solves more than assumed | Phase 0 landscape tests it. If the gap is smaller, the problem statement narrows honestly. |
| 16 GB limits which models can be tested together | Use tiny, small and medium so swap pressure exists without OS thrash. State the limit in every report. |
| Scope creep toward a general runtime | Every feature needs a phase measurement that asked for it. ADR 0001. |
| Phase 7 needs hardware not owned | A second Ollama in a Docker container on the same machine proves the distributed logic. A real GPU is optional. |
| Single-machine numbers overinterpreted | Every report names the hardware. The README says the logic transfers and the numbers do not. |

## 11. Definition of done for a phase

- Learning notes exist in `docs/concepts/` for every new concept.
- The exercise was implemented by the engineer and reviewed.
- Code is tested, linted and typed.
- A benchmark report exists with hardware, method, and before-and-after numbers.
- ADRs exist for any decision made.
- `ROADMAP.md` is updated and only then may a feature be described as shipped.
