"""HTTP surface (Phase 1).

Exposes the Ollama native API and the OpenAI-compatible API, forwards requests
to the engine without buffering, and streams responses back. Identifies the
caller by API key and attaches a request id to everything downstream.
Nothing here decides order or limits; that is the queue and scheduler.
"""
