"""Command-line interface for the Riverwood voice agent."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import typer

from .config import load_settings
from .exceptions import ConfigurationError
from .gradio_app import create_gradio_interface
from .logging_config import configure_logging
from .pipeline import VoiceAgent

app = typer.Typer(help="Run the Riverwood AI Voice Agent")
LOGGER = logging.getLogger(__name__)


def _build_agent(
    config_path: Optional[Path],
    log_level: Optional[str],
    log_file: Optional[Path],
    eager: bool,
) -> VoiceAgent:
    try:
        settings = load_settings(config_path)
    except ConfigurationError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    if log_level:
        settings.logging_level = log_level

    configure_logging(settings.logging_level, log_file)
    LOGGER.debug("Settings loaded: %s", settings)

    agent = VoiceAgent(settings=settings)
    if eager:
        agent.ensure_ready()
    return agent


@app.command("gradio")
def run_gradio(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file (YAML or JSON)"),
    log_level: Optional[str] = typer.Option(None, help="Override log level (DEBUG, INFO, etc.)"),
    log_file: Optional[Path] = typer.Option(None, help="Optional path to a log file"),
    share: bool = typer.Option(False, help="Launch Gradio with public sharing"),
    no_eager: bool = typer.Option(False, help="Skip eager loading of heavy models"),
) -> None:
    """Launch the Gradio interface."""

    agent = _build_agent(config, log_level, log_file, eager=not no_eager)
    demo = create_gradio_interface(agent)
    demo.launch(share=share)


@app.command()
def chat(
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
    log_level: Optional[str] = typer.Option(None),
    log_file: Optional[Path] = typer.Option(None),
    no_eager: bool = typer.Option(False, help="Skip eager loading of heavy models"),
) -> None:
    """Start an interactive text-only chat session in the terminal."""

    agent = _build_agent(config, log_level, log_file, eager=not no_eager)
    typer.echo("Riverwood AI Voice Agent (type 'exit' to quit)")

    while True:
        user_text = typer.prompt("You")
        if user_text.strip().lower() in {"exit", "quit"}:
            break
        try:
            reply = agent.process_text(user_text)
        except Exception as exc:  # pragma: no cover - interactive session
            typer.secho(f"Error: {exc}", fg=typer.colors.RED)
            continue
        typer.secho(f"Agent: {reply}", fg=typer.colors.GREEN)


@app.command("settings")
def show_settings(
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
) -> None:
    """Print the resolved configuration as JSON."""

    try:
        settings = load_settings(config)
    except ConfigurationError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    typer.echo(json.dumps(settings.__dict__, default=str, indent=2))


if __name__ == "__main__":
    app()
