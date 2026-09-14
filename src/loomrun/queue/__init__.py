"""Queue, workers, admission control (Phase 2).

A bounded Redis queue and a fixed pool of workers sized to the engine's
parallelism. When the queue is full, callers get a fast answer (wait or 429)
instead of a slow failure. Workers publish heartbeats.
"""
