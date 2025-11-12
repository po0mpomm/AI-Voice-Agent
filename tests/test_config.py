@
from pathlib import Path

import pytest

from riverwood_voice_agent.config import SettingsError, load_settings


def test_load_settings_requires_api_key(tmp_path: Path) -> None:
    with pytest.raises(SettingsError):
        load_settings(tmp_path / "missing.yaml")


def test_load_settings_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "riverwood.config.yaml"
    config_path.write_text("groq_api_key: test-key\nwhisper_model: base\n", encoding="utf8")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    settings = load_settings(config_path)

    assert settings.groq_api_key == "test-key"
    assert settings.whisper_model == "base"

