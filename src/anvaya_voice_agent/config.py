"""Application configuration management."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from .exceptions import ConfigurationError

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency guard
    yaml = None  # type: ignore


DEFAULT_CONFIG_FILENAMES = (
    "anvaya.config.yaml",
    "anvaya.config.yml",
    "anvaya.config.json",
)


@dataclass(slots=True)
class Settings:
    """Strongly-typed container for application configuration."""

    groq_api_key: str
    whisper_model: str = "tiny"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    gradio_title: str = "Anvaya AI Voice Agent"
    persona_name: str = "Anvaya"
    persona_description: str = (
        "You are Anvaya -- a warm and friendly AI assistant. "
        "Reply in Hinglish (Roman script), 2-3 lines, warm and professional."
    )
    prompt_language_hint: str = "hi"
    translate_task: bool = True
    speech_rate: int = 160
    speech_volume: float = 1.0
    voice_preference_keywords: tuple[str, ...] = ("female", "zira", "heera")
    max_history_messages: int = 6
    groq_model: str = "llama-3.1-8b-instant"
    temperature: float = 0.9
    max_tokens: int = 200
    logging_level: str = "INFO"
    config_file: Optional[Path] = field(default=None, repr=False)

    @property
    def system_prompt(self) -> str:
        return self.persona_description


def _load_from_file(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")

    if config_path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise ConfigurationError("PyYAML is required to read YAML configuration files")
        with config_path.open("r", encoding="utf8") as fh:
            return yaml.safe_load(fh) or {}

    if config_path.suffix.lower() == ".json":
        with config_path.open("r", encoding="utf8") as fh:
            return json.load(fh) or {}

    raise ConfigurationError(f"Unsupported config file format: {config_path.suffix}")


def _merge_dict(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = base.copy()
    merged.update({k: v for k, v in overrides.items() if v is not None})
    return merged


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """Load settings from environment variables and optional config files."""

    load_dotenv()

    env_config: Dict[str, Any] = {
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "whisper_model": os.getenv("WHISPER_MODEL"),
        "whisper_device": os.getenv("WHISPER_DEVICE"),
        "whisper_compute_type": os.getenv("WHISPER_COMPUTE_TYPE"),
        "gradio_title": os.getenv("GRADIO_TITLE"),
        "persona_name": os.getenv("PERSONA_NAME"),
        "persona_description": os.getenv("PERSONA_DESCRIPTION"),
        "prompt_language_hint": os.getenv("PROMPT_LANGUAGE_HINT"),
        "translate_task": _env_bool("TRANSLATE_TASK"),
        "speech_rate": _env_int("SPEECH_RATE"),
        "speech_volume": _env_float("SPEECH_VOLUME"),
        "groq_model": os.getenv("GROQ_MODEL"),
        "temperature": _env_float("TEMPERATURE"),
        "max_tokens": _env_int("MAX_TOKENS"),
        "logging_level": os.getenv("LOGGING_LEVEL"),
        "max_history_messages": _env_int("MAX_HISTORY_MESSAGES"),
    }

    file_config: Dict[str, Any] = {}
    if config_path:
        file_config = _load_from_file(config_path)
    else:
        for candidate in DEFAULT_CONFIG_FILENAMES:
            candidate_path = Path(candidate)
            if candidate_path.exists():
                file_config = _load_from_file(candidate_path)
                config_path = candidate_path
                break

    merged = _merge_dict(file_config, env_config)

    if not merged.get("groq_api_key"):
        raise ConfigurationError("GROQ_API_KEY is required. Provide via .env or config file.")

    settings = Settings(**{k: v for k, v in merged.items() if k in Settings.__annotations__})
    settings.config_file = config_path
    return settings


def _env_bool(name: str) -> Optional[bool]:
    value = os.getenv(name)
    if value is None:
        return None
    return value.lower() in {"1", "true", "yes", "on"}


def _env_int(name: str) -> Optional[int]:
    value = os.getenv(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(f"Invalid integer for {name}: {value}") from exc


def _env_float(name: str) -> Optional[float]:
    value = os.getenv(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(f"Invalid float for {name}: {value}") from exc
