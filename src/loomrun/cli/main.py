"""Loomrun command line entry point.

Phase 0 ships only `version`. Every later phase adds exactly one verb; see
docs/plan.md section 4.2.
"""

from __future__ import annotations

import typer

from loomrun import __version__

app = typer.Typer(
    name="loomrun",
    help="Scheduler and governor for one shared inference machine.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Scheduler and governor for one shared inference machine."""


@app.command()
def version() -> None:
    """Print the installed Loomrun version."""
    typer.echo(__version__)


if __name__ == "__main__":  # pragma: no cover
    app()
