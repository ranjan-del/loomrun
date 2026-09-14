# Landscape

What the neighbouring tools do and do not do, so Loomrun's gap is stated from evidence rather
than memory. Each row says where the fact came from and when. Rows marked **to verify** are
working assumptions until a Phase 0 test or a documentation read confirms them.

Last updated 2026-09-14.

## Summary table

| Capability | Ollama | llama-swap | vLLM | LiteLLM proxy | Loomrun |
|---|---|---|---|---|---|
| Serves local models | Yes | Via llama-server and others | Yes, high throughput | No, routes to APIs (local engines count as APIs) | No, proxies to the engine |
| Several models on one box | Yes, up to a limit if they fit | Yes, swap on demand, groups via swap matrix | One model per server process (to verify) | Not applicable | Uses the engine's ability, adds placement policy |
| Request queue | Yes, one FIFO, 512 deep, then 503 | Not documented | Not documented on the serving page (to verify: `max_num_seqs`) | Max parallel requests per key | Bounded, per-caller aware, fast rejection |
| Caller identity | No | No | No | Yes: keys, users, teams | Yes: API keys per caller |
| Priority between callers | No | No | No | No | Yes, Phase 4 |
| Fair share between callers | No | No | No | No | Yes, Phase 4 |
| Deadlines and cancellation propagation | Client disconnect handling only | Not documented | Not documented | Not documented | Yes, Phase 3 |
| Retry policy with jitter | No | No | No | Yes, retries and fallbacks | Yes, Phase 3 |
| Budgets | No | No | No | Yes, rich: key, user, team, model, duration | Yes, with a degradation ladder instead of an error, Phase 6 |
| Aware of local memory and which model is loaded | Internally, for its own eviction | Yes, for swapping | Internally, for one model | No | Yes, for placement decisions, Phase 5 |
| Placement based on what is waiting | No, evicts on idleness | No, swaps on the request in hand | Not applicable | No | Yes, Phase 5 |
| Per-request ledger | No | Web UI with token metrics | Metrics endpoint | Yes, spend logs | Yes, PostgreSQL rows per request, Phase 1 |
| Multi-machine | No | No | Multi-GPU within a node; multi-node for one model | Load balancing across deployments | Phase 7 |

## Ollama

Source: Ollama FAQ at docs.ollama.com, read 2026-09-14. Installed version on the target
machine: 0.34.0.

- `OLLAMA_NUM_PARALLEL`: "The maximum number of parallel requests each model will process at
  the same time." Default 1. "Required RAM will scale by `OLLAMA_NUM_PARALLEL` *
  `OLLAMA_CONTEXT_LENGTH`."
- `OLLAMA_MAX_LOADED_MODELS`: "The maximum number of models that can be loaded concurrently
  provided they fit in available memory." Default "3 * the number of GPUs or 3 for CPU inference".
- `OLLAMA_MAX_QUEUE`: default 512. "Ollama will queue when busy before rejecting additional
  requests." Beyond that the server responds 503.
- Eviction: when a new model does not fit, "all new requests will be queued until the new model
  can be loaded. As prior models become idle, one or more will be unloaded to make room." Default
  unload after 5 minutes idle.
- "When using GPU inference new models must be able to completely fit in VRAM to allow
  concurrent model loads."

What this means for Loomrun: Ollama already has a queue, a parallelism knob and an eviction
rule. It has no idea who is calling, so it cannot prioritise, share fairly, budget, or keep a
model loaded because work for it is waiting. Those are the gaps. Loomrun must not duplicate the
queue depth or parallelism logic; it sizes its worker pool to `OLLAMA_NUM_PARALLEL` and keeps
the engine's own queue nearly empty so that Loomrun's scheduler, not Ollama's FIFO, decides order.

Phase 0 tests to run: confirm the 503 at queue overflow, measure swap time between the small
and medium model, measure how `OLLAMA_NUM_PARALLEL` 1 vs 4 changes throughput and per-request
latency on the M1.

## llama-swap

Source: project README on GitHub, read 2026-09-14.

- "On-demand model switching for many local AI servers." When a request names a model, it
  starts the matching server and stops the previous one.
- "Run concurrent models with a custom DSL swap matrix." Groups of models may stay up together.
- Automatic unloading via TTL. "One binary, one configuration file. no external dependencies."
- Proxies OpenAI-compatible endpoints and Anthropic API endpoints.
- Web UI with real-time monitoring and token metrics.
- Not present in the documentation: request queueing, priorities, per-client fairness, budgets,
  per-request accounting. Explicitly not: distributed inference or multi-node.

What this means for Loomrun: llama-swap solves "which server is running" reactively, per
request. Loomrun's placement is the opposite direction: look at the whole queue and decide what
to keep loaded. The two could even stack, with llama-swap as Loomrun's engine, but Ollama is the
first target.

## vLLM

Source: online serving page at docs.vllm.ai, read 2026-09-14. That page lists the endpoints
(`/v1/completions`, `/v1/chat/completions`, `/v1/chat/completions/batch`, `/v1/responses`,
`/v1/embeddings`) and says nothing about tenants, priorities, budgets or overload behaviour.

To verify in Phase 7, when a CUDA machine is available: one model per `vllm serve` process
(from CLI usage), `max_num_seqs` as the concurrency bound, continuous batching and the scheduler's
behaviour under overload. vLLM does not run on the M1 target, so nothing about it is measured
before Phase 7.

What this means for Loomrun: vLLM is the throughput engine. Loomrun's OpenAI-compatible surface
from Phase 1 means switching the engine from Ollama to vLLM is a configuration change.

## LiteLLM proxy

Source: budgets and users documentation at docs.litellm.ai, read 2026-09-14.

- Budgets at global, team, team member, internal user, virtual key, per-model, per-agent and
  per-customer scope, with `budget_duration` resets.
- "Budget is reset at the end of specified duration. If not set, budget is never reset."
- When exceeded: requests fail with an error such as `ExceededTokenBudget`, or fall back to
  zero-cost models if configured.
- TPM and RPM limits per key, user, team, agent; max parallel requests.
- Not mentioned: local GPU memory awareness, which local model is loaded, queueing with
  priorities, fair share between callers.

What this means for Loomrun: LiteLLM is the reference for how rich budget configuration can be.
Loomrun should not try to match that breadth. Its difference is the degradation ladder (smaller
model, shorter context, partial result with reason) and that its decisions know about the one
machine's memory and queue. If a team already runs LiteLLM for cloud APIs, Loomrun sits behind
it as the local engine.

## Ray Serve, Kubernetes

To verify by documentation read before Phase 7. Working assumption: both solve placement and
scaling across many machines and are heavier than a one-box team needs. Loomrun's Phase 7 uses
Redis leases for two workers and does not attempt to compete here.

## The gap, in one sentence

Existing tools either serve models (Ollama, vLLM), swap them (llama-swap), or budget cloud API
calls (LiteLLM). None of them knows who is calling one shared local machine and decides order,
share, placement and budget from that. Loomrun does only that.
