# Migration Summary: Gradio to FastAPI + Gemini API

## Overview
This document summarizes the changes made to migrate the AI Voice Agent project from Gradio/Groq/Whisper to FastAPI + Gemini API with HTML/CSS/JS frontend.

## Key Changes

### 1. Backend Architecture
- **Removed**: Gradio-based UI
- **Added**: FastAPI REST API backend
- **Location**: `backend/` directory

### 2. API Integration
- **Removed**: 
  - Groq API (for chat completions)
  - Whisper (faster-whisper) (for speech-to-text)
  - pyttsx3 (for text-to-speech)
- **Added**: 
  - Gemini API (for both chat completions and speech-to-text)
  - Browser Web Speech API (for text-to-speech)

### 3. Frontend
- **Removed**: Gradio UI
- **Added**: Modern HTML/CSS/JavaScript frontend
- **Location**: `frontend/` directory
- **Features**:
  - Voice recording with MediaRecorder API
  - Real-time chat interface
  - Browser-based speech synthesis
  - Multi-language support (English/Hindi)
  - Responsive design

### 4. Configuration
- **Changed**: Environment variables
  - Old: `GROQ_API_KEY`, `WHISPER_MODEL`, etc.
  - New: `GEMINI_API_KEY`, `GEMINI_CHAT_MODEL`, `GEMINI_STT_MODEL`
- **File**: `example.env` updated

### 5. Dependencies
- **Removed**:
  - `gradio==4.44.0`
  - `faster-whisper==1.0.1`
  - `groq==0.11.0`
  - `pyttsx3==2.91`
  - `soundfile==0.12.1`
  - `numpy>=1.24`
- **Added**:
  - `fastapi==0.110.0`
  - `uvicorn[standard]==0.30.0`
  - `httpx==0.27.0`
  - `python-multipart==0.0.9`
  - `pydantic-settings==2.3.4`

### 6. CLI Changes
- **Removed**: `gradio` command
- **Added**: `server` command to run FastAPI server
- **Usage**: `python -m anvaya_voice_agent.cli server`

### 7. New Files Created
```
backend/
├── __init__.py
├── app.py                    # FastAPI application
├── config.py                 # Settings with Gemini API
├── schemas.py                # Pydantic models
└── services/
    ├── __init__.py
    └── gemini_client.py      # Gemini API client

frontend/
├── index.html                # Main HTML page
├── app.js                    # Frontend JavaScript
└── styles.css                # Styling

run_server.py                 # Simple server launcher
```

### 8. Files Modified
- `src/anvaya_voice_agent/cli.py` - Updated to run FastAPI server
- `anvaya-voice-agent/requirements.txt` - Updated dependencies
- `example.env` - Updated environment variables
- `README.md` - Updated documentation

### 9. Files No Longer Used (but kept for reference)
- `src/anvaya_voice_agent/gradio_app.py` - Gradio UI (deprecated)
- `src/anvaya_voice_agent/pipeline.py` - Old pipeline (deprecated)
- `src/anvaya_voice_agent/audio.py` - Whisper transcriber (deprecated)
- `src/anvaya_voice_agent/chat.py` - Groq client (deprecated)
- `src/anvaya_voice_agent/tts.py` - pyttsx3 synthesizer (deprecated)

## How to Run

### Quick Start
```bash
# 1. Install dependencies
pip install -r anvaya-voice-agent/requirements.txt

# 2. Set up environment
cp example.env .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run server
python run_server.py
# or
python -m anvaya_voice_agent.cli server

# 4. Open browser
# Navigate to http://127.0.0.1:8000
```

## API Endpoints

### GET /
Serves the frontend HTML page

### GET /health
Health check endpoint
Response: `{"status": "ok"}`

### POST /api/chat
Chat completion endpoint
Request:
```json
{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "conversation_id": "optional-uuid",
  "language": "en"
}
```
Response:
```json
{
  "response": "Hello! How can I help you?",
  "conversation_id": "optional-uuid"
}
```

### POST /api/transcribe
Audio transcription endpoint
Request: `multipart/form-data`
- `file`: Audio file (webm, wav, mp3, etc.)
- `language`: Language code (en, hi)

Response:
```json
{
  "text": "Transcribed text"
}
```

## Benefits of Migration

1. **Better Performance**: Gemini API is faster than local Whisper models
2. **Modern UI**: HTML/CSS/JS frontend is more customizable and responsive
3. **Simplified Architecture**: Single API (Gemini) for both chat and transcription
4. **Browser TTS**: No need for local TTS engine, uses browser's native capabilities
5. **Better Scalability**: FastAPI is production-ready and can handle more concurrent requests
6. **Easier Deployment**: Can be deployed as a standard web application

## Notes

- The old pipeline code (`pipeline.py`, `audio.py`, `chat.py`, `tts.py`) is still in the codebase but not used by the new FastAPI backend
- The Gradio app (`gradio_app.py`) is also kept for reference but not used
- All new functionality is in the `backend/` and `frontend/` directories
- The CLI has been simplified to just run the server

