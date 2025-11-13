"""Run the FastAPI server for Anvaya Voice Agent."""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    # Use import string for reload to work properly
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)

