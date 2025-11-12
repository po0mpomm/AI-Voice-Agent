"""Speech-to-text transcription services."""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from .exceptions import TranscriptionError

LOGGER = logging.getLogger(__name__)


class WhisperTranscriber:
    """Wrapper around the Faster Whisper model with lazy loading."""

    def __init__(
        self,
        model_name: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
        beam_size: int = 5,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self._model: Optional[WhisperModel] = None

    def _ensure_model(self) -> WhisperModel:
        if self._model is None:
            LOGGER.info(
                "Loading Whisper model '%s' (device=%s, precision=%s)",
                self.model_name,
                self.device,
                self.compute_type,
            )
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe_numpy(
        self,
        sample_rate: int,
        audio_data: np.ndarray,
        language_hint: str = "en",
        translate: bool = False,
    ) -> str:
        LOGGER.debug("Beginning transcription (sr=%s, samples=%s)", sample_rate, len(audio_data))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_path = Path(tmp_file.name)
            sf.write(tmp_file, audio_data, sample_rate)

        try:
            return self._transcribe_file(temp_path, language_hint, translate)
        finally:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass

    def _transcribe_file(self, path: Path, language_hint: str, translate: bool) -> str:
        model = self._ensure_model()
        try:
            segments, _info = model.transcribe(
                str(path),
                beam_size=self.beam_size,
                task="translate" if translate else "transcribe",
                language=language_hint,
            )
        except Exception as exc:  # pragma: no cover - model errors are external
            raise TranscriptionError(f"Whisper transcription failed: {exc}") from exc

        text = " ".join(segment.text.strip() for segment in segments if segment.text)
        text = text.strip()
        if not text:
            raise TranscriptionError("Could not understand the provided audio")

        LOGGER.info("Transcription complete: %s", text)
        return text
