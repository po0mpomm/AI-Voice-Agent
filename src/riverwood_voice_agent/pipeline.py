"""Core voice agent pipeline orchestration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Mapping, Sequence

import numpy as np

from .audio import WhisperTranscriber
from .chat import GroqChatClient
from .config import Settings
from .exceptions import VoiceAgentError
from .tts import SpeechSynthesizer

LOGGER = logging.getLogger(__name__)

ChatMessage = Mapping[str, str]


@dataclass
class VoiceAgent:
    """Coordinate transcription, chat completion, and speech output."""

    settings: Settings
    history: List[ChatMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.transcriber = WhisperTranscriber(
            model_name=self.settings.whisper_model,
            device=self.settings.whisper_device,
            compute_type=self.settings.whisper_compute_type,
        )
        self.chat_client = GroqChatClient(
            api_key=self.settings.groq_api_key,
            model=self.settings.groq_model,
            system_prompt=self.settings.system_prompt,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
        )
        self.synthesizer = SpeechSynthesizer(
            rate=self.settings.speech_rate,
            volume=self.settings.speech_volume,
            voice_keywords=self.settings.voice_preference_keywords,
        )

    def reset_history(self) -> None:
        LOGGER.debug("Resetting conversation history")
        self.history.clear()

    def get_recent_history(self) -> Sequence[ChatMessage]:
        if self.settings.max_history_messages <= 0:
            return []
        return self.history[-self.settings.max_history_messages :]

    def transcribe(self, sample_rate: int, audio_data: np.ndarray) -> str:
        return self.transcriber.transcribe_numpy(
            sample_rate=sample_rate,
            audio_data=audio_data,
            language_hint=self.settings.prompt_language_hint,
            translate=self.settings.translate_task,
        )

    def chat(self, user_text: str) -> str:
        reply = self.chat_client.complete(self.get_recent_history(), user_text)
        return reply

    def speak(self, text: str) -> None:
        self.synthesizer.speak(text)

    def process_audio(self, sample_rate: int, audio_data: np.ndarray) -> str:
        LOGGER.debug("Processing audio input")
        text = self.transcribe(sample_rate, audio_data)
        reply = self.chat(text)
        self.speak(reply)
        self._update_history(user_text=text, reply=reply)
        return reply

    def process_text(self, user_text: str) -> str:
        LOGGER.debug("Processing text input")
        reply = self.chat(user_text)
        self.speak(reply)
        self._update_history(user_text=user_text, reply=reply)
        return reply

    def _update_history(self, user_text: str, reply: str) -> None:
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})

    def ensure_ready(self) -> None:
        """Eagerly load heavy dependencies to surface issues early."""
        try:
            self.transcriber._ensure_model()  # pylint: disable=protected-access
        except Exception as exc:  # pragma: no cover - whisper errors are external
            raise VoiceAgentError(f"Failed to load Whisper model: {exc}") from exc

