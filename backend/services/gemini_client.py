import base64
import io
import logging
from typing import Iterable, List

import httpx
from fastapi import Depends

from ..config import Settings, get_settings
from ..schemas import ChatMessage

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1"


class GeminiClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def create_chat_completion(self, messages: Iterable[ChatMessage], language: str) -> str:
        serialized_messages = self._serialize_messages(messages)
        instruction = self._chat_instruction(language)
        contents = serialized_messages
        if instruction:
            contents = [
                {"role": "user", "parts": [{"text": instruction}]},
                *serialized_messages,
            ]

        endpoint = f"{GEMINI_BASE_URL}/models/{self.settings.gemini_chat_model}:generateContent"

        data = await self._post(
            endpoint,
            {"contents": contents},
            timeout=60,
        )
        return self._extract_text(data)

    async def transcribe_audio(self, file_bytes: io.BytesIO, mime_type: str, language: str) -> str:
        file_bytes.seek(0)
        normalized_mime = mime_type.split(";")[0].strip()
        audio_payload = {
            "inlineData": {
                "mimeType": normalized_mime,
                "data": base64.b64encode(file_bytes.read()).decode("utf-8"),
            }
        }

        endpoint = f"{GEMINI_BASE_URL}/models/{self.settings.gemini_stt_model}:generateContent"
        prompt = {
            "role": "user",
            "parts": [
                audio_payload,
                {
                    "text": self._transcription_instruction(language),
                },
            ],
        }

        data = await self._post(
            endpoint,
            {"contents": [prompt]},
            timeout=90,
        )
        
        logger.debug(f"Gemini transcription response received: {data}")
        result = self._extract_text(data)
        
        if not result or not result.strip():
            logger.warning("Gemini transcription returned empty result")
            raise ValueError("Transcription returned empty result. Please try speaking again.")
        
        return result

    async def _post(self, endpoint: str, payload: dict, timeout: int) -> dict:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    endpoint,
                    params={"key": self.settings.gemini_api_key},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = self._extract_error_message(exc.response)
            raise RuntimeError(message) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Network error contacting Gemini: {exc}") from exc

        return response.json()

    def _serialize_messages(self, messages: Iterable[ChatMessage]) -> List[dict]:
        serialized: List[dict] = []
        for message in messages:
            role = "user" if message.role == "user" else "model"
            serialized.append(
                {
                    "role": role,
                    "parts": [{"text": message.content}],
                }
            )
        return serialized

    def _extract_text(self, payload: dict) -> str:
        try:
            candidates = payload.get("candidates", [])
            if not candidates:
                logger.error(f"No candidates in Gemini response: {payload}")
                raise ValueError("Gemini API returned no candidates in response.")
            
            for candidate in candidates:
                if "content" not in candidate:
                    continue
                    
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                
                if not parts:
                    continue
                
                texts = []
                for part in parts:
                    if isinstance(part, dict) and "text" in part:
                        text = part.get("text")
                        if text and isinstance(text, str):
                            texts.append(text)
                
                if texts:
                    result = "\n".join(texts).strip()
                    if result:
                        return result
            
            logger.error(f"Unable to extract text from Gemini response: {payload}")
            raise ValueError("Gemini API response did not contain valid text output.")
        except ValueError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error extracting text from Gemini response: {e}")
            raise ValueError(f"Failed to parse Gemini API response: {str(e)}") from e

    def _extract_error_message(self, response: httpx.Response) -> str:
        fallback = f"Gemini API error ({response.status_code})"
        try:
            data = response.json()
        except ValueError:
            return fallback

        error = data.get("error")
        if not error:
            return fallback

        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()

        return fallback

    def _chat_instruction(self, language: str) -> str:
        if language == "hi":
            return (
                "आप एक सहायक AI सहायक हैं। उपयोगकर्ता के प्रश्नों का उत्तर केवल हिंदी में दें "
                "और देवनागरी लिपि का प्रयोग करें।"
            )
        return "You are a helpful AI assistant. Reply concisely using natural English."

    def _transcription_instruction(self, language: str) -> str:
        if language == "hi":
            return (
                "ऑडियो इनपुट को हिंदी में ट्रांसक्राइब करें। केवल पहचाने गए शब्द लौटाएँ और कोई अतिरिक्त टिप्पणी न जोड़ें।"
            )
        return (
            "Transcribe the audio input in English. Return only the words you hear without any additional commentary."
        )


def get_gemini_client(settings: Settings = Depends(get_settings)) -> GeminiClient:
    return GeminiClient(settings)

