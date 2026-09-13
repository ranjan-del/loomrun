# ADR 0001: Scope Loomrun to one shared inference machine

Date: 2026-09-14. Status: accepted.

## Context
The original brief described a general AI execution runtime: task API, planner, model router,
DAG engine, workers, queues, retries, durable execution, governance, observability, benchmarking,
adaptive routing, local inference, distributed execution and GPU awareness, across nineteen phases.

Most of that list maps directly onto mature open-source software: durable execution (Temporal,
Restate, DBOS, Inngest, Hatchet), workflows (Prefect, Dagster, Airflow, LangGraph), gateways and
routing (LiteLLM, Portkey, OpenRouter, RouteLLM), distributed workers (Ray, Celery, Kubernetes),
tracing (OpenTelemetry GenAI conventions, Langfuse, Phoenix). Composing them gives a team roughly
what the brief described. A project defined as the union of those features would be a category,
not a problem, and would likely stall before reaching anything measurable.

## Decision
Loomrun solves one problem: several applications share one inference machine running Ollama or
vLLM, and nothing is in charge of order, fairness, budgets, model placement or record keeping.
Loomrun is the thin layer that is in charge.

Everything in the original brief that matters (queue, workers, backpressure, timeouts,
cancellation, retries, fair share, budgets, placement, ledger, a second worker) enters as a phase
that fixes a measured problem on that one machine. Everything else (DAG engine, planner, cloud
routing, Kubernetes, vLLM replacement) is a non-goal.

## Consequences
- The whole project is measurable on one developer machine through Phase 6.
- Inference internals (model loading, memory, KV cache, batching) are in the spine from Phase 5,
  not deferred to a late phase.
- Novelty is a hypothesis until Phase 0 verifies the gaps in `docs/landscape.md`.
- Numbers measured on a single machine are reported as such; the scheduling logic transfers, the
  numbers do not.
