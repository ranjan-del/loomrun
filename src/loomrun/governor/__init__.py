"""Budgets and degradation (Phase 6).

Per-caller token and time budgets over configurable windows. When a budget is
exceeded the governor returns a decision: allow, degrade (smaller model,
shorter context) or stop with a partial result and a reason. Pricing is
configuration, versioned, never hardcoded.
"""
