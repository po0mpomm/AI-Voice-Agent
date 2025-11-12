"""Text-to-speech utilities."""
from __future__ import annotations

import logging
from typing import Iterable

import pyttsx3

from .exceptions import SpeechSynthesisError

LOGGER = logging.getLogger(__name__)


class SpeechSynthesizer:
    """Wrapper around pyttsx3 for configurable TTS output."""

    def __init__(
        self,
        rate: int = 160,
        volume: float = 1.0,
        voice_keywords: Iterable[str] = ("female",),
    ) -> None:
        self._engine = pyttsx3.init()
        self._configure_voice(voice_keywords)
        self._engine.setProperty("rate", rate)
        self._engine.setProperty("volume", volume)

    def _configure_voice(self, keywords: Iterable[str]) -> None:
        voices = self._engine.getProperty("voices")
        lowered = [keyword.lower() for keyword in keywords]
        for voice in voices:
            name = voice.name.lower()
            if any(keyword in name for keyword in lowered):
                LOGGER.info("Selected voice: %s", voice.name)
                self._engine.setProperty("voice", voice.id)
                return
        LOGGER.warning("No preferred voice found; using default voice")

    def speak(self, text: str) -> None:
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception as exc:  # pragma: no cover
            raise SpeechSynthesisError(f"Failed to speak text: {exc}") from exc
