"""Command-line interface for the Anvaya voice agent."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import typer
import uvicorn

from .config import load_settings
from .exceptions import ConfigurationError
from .logging_config import configure_logging

app = typer.Typer(help="Run the Anvaya AI Voice Agent")
LOGGER = logging.getLogger(__name__)


@app.command("server")
def run_server(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    log_level: Optional[str] = typer.Option(None, help="Override log level (DEBUG, INFO, etc.)"),
) -> None:
    """Launch the FastAPI web server."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from backend.app import app as fastapi_app
    
    if log_level:
        logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
    
    typer.echo(f"Starting Anvaya Voice Chat Assistant on http://{host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, reload=reload)






if __name__ == "__main__":
    app()
