<h1 align="center">Loomrun</h1>

<p align="center">
  <b>A scheduler and governor for one shared inference machine.</b><br/>
  Put it in front of Ollama or vLLM. Several apps share the box fairly, runaway jobs get stopped,
  the right model stays loaded, and every request is written down with its cost.
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <img alt="Status: pre-alpha" src="https://img.shields.io/badge/status-pre--alpha-orange">
</p>

> **Status: planning.** Nothing is implemented yet. This README describes the problem and the
> intended shape of the project. [ROADMAP.md](ROADMAP.md) tracks what exists and what is next.
> No section below claims a feature that is not marked shipped in the roadmap, and no number in
> this repository will ever be written down unless it came from a real run.

---

## The problem

A small team runs one inference machine. On it, Ollama or vLLM loads open models and answers
requests. Several things hit that machine at once:

| Caller | Sends | Needs |
|---|---|---|
| A chat application | One question at a time from a person at a screen | An answer in seconds |
| A nightly ingestion job | Thousands of documents to summarise | Done by morning, nobody waiting |
| A classification service | Hundreds of short requests an hour | Quick, not urgent |

The inference engine takes whatever arrives, in whatever order. Nothing is in charge, so:

- The person at the screen waits behind the batch job.
- Two apps use two models, the memory holds one, and the machine spends its time swapping.
- A script with a bug sends requests forever and nothing stops it.
- Nobody can say what any app used in tokens, time or memory.
- A crash halfway through the batch means starting again from zero.

Large platforms solve this inside their own infrastructure. Small teams run their applications
straight onto the engine and hit every one of these problems.

## What Loomrun is

Loomrun is a thin runtime that sits between applications and the inference engine. Every request
passes through it. It decides who goes first, how many run at once, when to make callers wait,
when to stop a runaway job, which model to keep loaded, and it records what happened.

```
Applications        chat app, ingestion job, classifier, agents
      |
   Loomrun          admission, queue, priority, fair share, budgets, placement, ledger
      |
Inference engine    Ollama or vLLM: loads the model, produces tokens
      |
Hardware            GPU or Apple Silicon unified memory
```

Applications keep speaking the engine's own API. They point at Loomrun instead of the engine and
change nothing else.

## What Loomrun is not

- Not an inference engine. Ollama and vLLM do that well and Loomrun builds on them.
- Not a chat or RAG application. See [RagFabric](https://github.com/ranjan-del/ragfabric) for that layer.
- Not a general workflow engine, a multi-cloud LLM gateway, or a Kubernetes replacement.
- Not a cloud service. It runs on your own machine.

## How it differs from existing tools

| Tool | What it does | What it does not do, which Loomrun does |
|---|---|---|
| Ollama alone | Loads models, serves requests, keeps a model warm for a while | No priorities, fairness, budgets, per-app ledger, or placement based on what is waiting |
| llama-swap | Swaps models in front of a local engine | Swaps on demand only. No queue, priority, or thrash avoidance |
| vLLM | Fast serving of one model with continuous batching | One model per process. No notion of tenants or budgets |
| LLM gateways (LiteLLM and similar) | One API over many cloud providers, per-key spend limits | Built for cloud APIs. Unaware of one machine's memory or loaded models |
| Ray Serve, Kubernetes | Serve across many machines | Heavy. Built for clusters, not one box shared by a few apps |

These comparisons are the working hypothesis. Phase 0 of the roadmap verifies each row and
records the evidence in `docs/landscape.md` before any code is written.

## Planned shape

Every capability enters only when a phase's measurement shows the problem it fixes. In rough order:

1. Pass-through proxy with a ledger of every request
2. Queue, bounded workers, admission control
3. Timeouts, cancellation propagation, retries with backoff
4. Priorities and fair share between apps
5. Swap-aware model placement
6. Per-app budgets with a degradation ladder instead of hard failure
7. A second worker machine

See [ROADMAP.md](ROADMAP.md) for detail and status.

## Principles

- **Integrate, do not replace.** The engine does inference, PostgreSQL holds state, Redis holds the
  queue. Loomrun holds only the scheduling and governance logic.
- **Measure first.** Every phase starts with a baseline and ends with a before-and-after number from
  a real run on real hardware. Numbers state the hardware they came from.
- **Simple working system over impressive architecture.** A feature that no measurement asked for
  does not get built.
- **Teach as you go.** Each component documents what it does, why it exists, what the alternatives
  were and which trade-off was taken. Decisions live in [docs/decisions](docs/decisions/).

## Contributing

The project is at the planning stage. Issues and discussion are welcome. Contribution guidelines
will be added when there is code to contribute to.

## License

[MIT](LICENSE).
