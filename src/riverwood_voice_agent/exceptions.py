"""Custom exception types for the Riverwood voice agent."""
from __future__ import annotations


class VoiceAgentError(Exception):
    """Base exception for the voice agent domain."""


class ConfigurationError(VoiceAgentError):
    """Raised when configuration is missing or invalid."""


class TranscriptionError(VoiceAgentError):
    """Raised when speech-to-text transcription fails."""


class ChatCompletionError(VoiceAgentError):
    """Raised when the chat model call fails."""


class SpeechSynthesisError(VoiceAgentError):
    """Raised when text-to-speech synthesis fails."""
