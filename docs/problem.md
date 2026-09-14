# Problem statement

Written 2026-09-14. One page. If this page and the code ever disagree, this page is wrong and
must be fixed, not the other way round.

## Who has the problem

A small team, a school, an NGO, or a single developer who runs open models on one machine with
Ollama (or, later, vLLM) and has more than one thing using it: a chat application, a background
ingestion job, a classifier, a few agents under development.

## What goes wrong

| Symptom | Cause |
|---|---|
| The person at the chat screen waits behind a batch job | The engine serves in arrival order. Nothing knows that one caller is a human waiting and another is a script that can wait. |
| The machine spends its time loading and unloading models | Two callers want two models that do not both fit in memory. The engine evicts on idleness, not on what is waiting. |
| One buggy script starves everyone | No per-caller limit on concurrency, tokens or time. |
| Nobody can say what any caller used | No record per caller of tokens, wait time, run time, outcome. |
| Work continues after the caller has gone | A cancelled or timed-out request keeps generating tokens on the engine. |
| Overload produces slow failures instead of fast answers | The engine queues deep and then fails late, so callers cannot back off early. |

## What Ollama already does, so we do not rebuild it

From the Ollama FAQ, read 2026-09-14: it processes up to `OLLAMA_NUM_PARALLEL` requests per model
at once (default 1), keeps up to `OLLAMA_MAX_LOADED_MODELS` models loaded if they fit (default 3
per GPU), queues up to `OLLAMA_MAX_QUEUE` requests (default 512) and returns 503 beyond that,
and unloads idle models to make room. It has no notion of callers, priority, fairness, budgets,
deadlines or a per-request record. The queue is one FIFO for everyone.

## What Loomrun does

Loomrun is a proxy in front of the engine. Applications keep the engine's API and change only
the address. Loomrun adds, one measured phase at a time:

1. A record of every request per caller.
2. A bounded queue with fast rejection under overload.
3. Deadlines that cancel engine work when the caller leaves, and retries that do not storm.
4. Priority and fair share between callers.
5. Placement that keeps the model with waiting work loaded.
6. Budgets that degrade gracefully instead of failing hard.
7. A second machine, when one is not enough.

## What success looks like

On the target machine (Apple M1, 16 GB), with a batch caller flooding the box and a chat caller
sending one request at a time, the chat caller's p95 latency through Loomrun stays close to its
unloaded baseline, the batch job still finishes, model swaps per minute drop against the bare
engine, and the ledger accounts for every token both callers used. Every one of those is a number
in `docs/benchmarks/` from a real run.

## Non-goals

Not an inference engine. Not a RAG or chat app. Not a workflow engine. Not a cloud API gateway.
Not a Kubernetes replacement. Not a cloud service.
