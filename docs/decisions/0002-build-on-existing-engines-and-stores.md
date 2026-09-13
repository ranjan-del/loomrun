# ADR 0002: Build on existing engines and stores, never replace them

Date: 2026-09-14. Status: accepted.

## Context
The tempting failure mode in this space is to rebuild an inference engine, a queue, or a
workflow engine badly. Ollama and vLLM already serve models well. Redis and PostgreSQL already
provide a queue and durable state.

## Decision
- Inference: Ollama first (runs on Apple Silicon and consumer GPUs), vLLM later. Treated as black
  boxes with measured load times and memory. Never patched.
- Queue: Redis. Chosen for the MVP because it is one process, well understood, and sufficient for
  a single-machine queue with worker heartbeats. RabbitMQ and Kafka are not needed at this scale.
- State and ledger: PostgreSQL. Durable, queryable, and already used in the sibling project.
- Loomrun owns only admission, scheduling, governance and record keeping.

## Consequences
- Loomrun stays small enough to understand end to end.
- Applications keep using the engine's API; they only change the address they call.
- If a measurement ever shows Redis or PostgreSQL is the bottleneck, that becomes a new ADR.
