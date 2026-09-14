"""Loomrun: scheduler and governor for one shared inference machine.

Loomrun sits between applications and an inference engine (Ollama or vLLM).
It owns admission, queueing, scheduling, governance and record keeping, and
nothing else. See docs/plan.md for the phases and docs/decisions/ for why.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("loomrun")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0+source"

__all__ = ["__version__"]
