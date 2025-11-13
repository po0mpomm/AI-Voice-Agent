import io
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings, Settings
from .schemas import ChatRequest, ChatResponse, TranscriptionResponse
from .services.gemini_client import GeminiClient, get_gemini_client

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Anvaya Voice Chat Assistant", version="0.1.0")

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIST.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIST), name="static")


@app.get("/")
async def serve_frontend():
    index_file = FRONTEND_DIST / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not built")
    return FileResponse(index_file)


@app.get("/health")
async def health_check(_: Settings = Depends(get_settings)):
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    client: GeminiClient = Depends(get_gemini_client),
):
    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    try:
        response_text = await client.create_chat_completion(
            payload.messages,
            payload.language,
        )
        return ChatResponse(
            response=response_text,
            conversation_id=payload.conversation_id,
        )
    except Exception as exc:
        logger.exception("Error while creating chat completion")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en"),
    client: GeminiClient = Depends(get_gemini_client),
):
    if file.content_type not in (
        "audio/webm",
        "audio/mpeg",
        "audio/wav",
        "audio/mp4",
        "audio/x-m4a",
        "audio/ogg",
        "audio/opus",
    ):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    try:
        buffer = io.BytesIO(await file.read())
        text = await client.transcribe_audio(
            buffer,
            file.content_type or "audio/webm",
            language,
        )
        return TranscriptionResponse(text=text)
    except Exception as exc:
        logger.exception("Error during transcription")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

