"""Scheduling and placement policies (Phases 4 and 5).

Decides which waiting request runs next: priority, weighted fair share between
callers, and swap-aware placement that avoids evicting a model with waiting
work. Pure policy functions over queue state; no I/O of its own.
"""
