"""Engine adapters and model inventory (Phases 1, 5, 7).

Ollama first, vLLM later. Engines are black boxes: the adapter knows how to
forward a request, list models, and observe which models are loaded and how
long loads took. It never patches or reimplements the engine.
"""
