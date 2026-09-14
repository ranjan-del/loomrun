"""Ledger (Phase 1).

One PostgreSQL row per request: caller, model, tokens in and out, timings
(queued, started, first token, finished), outcome, retries, swaps observed.
Everything the CLI, console and MCP server report comes from here.
"""
