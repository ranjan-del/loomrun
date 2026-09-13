# Roadmap

Legend: `[x]` shipped on main, `[~]` in progress, `[ ]` not started.

Phases 0 to 6 run on a single machine. Phase 7 needs a second machine or container.
Each phase ends with a measured before-and-after result recorded under `docs/benchmarks/`.

## Phase 0: Landscape and baseline
- [ ] `docs/landscape.md`: what Ollama, llama-swap, vLLM, Ray Serve and LiteLLM do and do not do, with tested facts
- [ ] `docs/problem.md`: one page problem statement and non-goals
- [ ] Load test script against bare Ollama
- [ ] Baseline numbers on the target hardware: time to first token, tokens per second, p50 and p95 latency at 1, 4 and 16 concurrent clients

## Phase 1: Pass-through proxy with a ledger
- [ ] Async proxy exposing the engine's own API and forwarding unchanged, streaming included
- [ ] Ledger in PostgreSQL: caller, model, tokens in and out, duration, outcome
- [ ] Measured: overhead added by the proxy

## Phase 2: Queue and admission control
- [ ] Redis queue, fixed pool of workers
- [ ] Bounded queue, reject or delay when full
- [ ] Worker heartbeats
- [ ] Measured: throughput and p95 under overload with and without admission control

## Phase 3: Timeouts, cancellation, retries
- [ ] Per-request deadlines
- [ ] Client disconnect cancels the worker's engine call
- [ ] Retry only on retryable errors, exponential backoff with jitter
- [ ] Measured: tokens wasted on cancelled requests before and after

## Phase 4: Priority and fair share
- [ ] Callers and priorities in configuration
- [ ] Interactive requests ahead of batch, no caller above its share
- [ ] Measured: interactive p95 while a batch job runs

## Phase 5: Swap-aware placement
- [ ] Track loaded models, load times, memory per model
- [ ] Group same-model requests, avoid thrash
- [ ] Measured: model swaps per minute and throughput with and without placement

## Phase 6: Budgets and degradation
- [ ] Per-caller token and time budgets
- [ ] Degradation ladder: smaller model, shorter context, stop with partial result and reason
- [ ] Measured: hard failures turned into completed degraded requests

## Phase 7: Second worker
- [ ] Two engines on two machines or containers
- [ ] Task ownership, dead worker detection, placement across both
- [ ] Measured: aggregate throughput and behaviour when one worker dies

## Later, optional
- vLLM on a cloud GPU, Kubernetes deployment, dashboard UI.
