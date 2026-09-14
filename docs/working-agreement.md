# Working agreement

Loomrun is a learn-and-build project. The point is to understand the execution layer under AI
applications by building a small, measured, documented tool that a small team can actually use.

## Rules
- **Learn, then build.** For every component: explain the problem, why it exists, the underlying
  computer science and the architecture; give a small exercise; the engineer implements a simplified
  version first; review it; then integrate, test, measure, document.
- **Integrate, do not replace.** Ollama or vLLM do inference. PostgreSQL holds state. Redis holds the
  queue. Never patch the engine. Never rebuild a workflow engine, gateway or orchestrator.
- **Measure first, never fabricate.** No number appears in any document unless it came from a real
  run, with the hardware named. No feature is claimed unless ROADMAP.md marks it shipped.
- **One problem.** Loomrun schedules and governs one shared inference machine. A capability enters
  only when a phase's measurement shows the problem it fixes.
- **Simple working system over impressive architecture.**
- **Decisions are recorded** as ADRs in `docs/decisions/NNNN-title.md`.
- **Challenge decisions.** If an idea is unnecessary, already solved by mature software, or
  over-engineered, say so before building it.

## Local memory
`MEMORY.md` at the repo root is the running project memory: context, decisions, open questions,
what happened in each session. It is gitignored and stays on the engineer's machine. Any assistant
or collaborator working on the project reads it at the start of a session and appends to it at the end.

## Git
The maintainer commits, pushes and merges to `main` directly; feature branches are used when work
spans more than one sitting. Everyone else contributes through pull requests. `main` is protected:
CI must pass, force pushes and deletion are blocked, and review conversations must be resolved
before merge. Commit messages carry no tool attribution trailers.
