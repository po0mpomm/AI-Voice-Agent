"""Chat completion client for Groq."""
from __future__ import annotations

import logging
from typing import Iterable, List, Mapping

from groq import Groq

from .exceptions import ChatCompletionError

LOGGER = logging.getLogger(__name__)


class GroqChatClient:
    """Thin wrapper around Groq chat completions with sensible defaults."""

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        temperature: float = 0.9,
        max_tokens: int = 200,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = Groq(api_key=api_key)

    def complete(self, history: Iterable[Mapping[str, str]], user_text: str) -> str:
        messages: List[Mapping[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        LOGGER.debug("Sending request to Groq (model=%s)", self.model)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:  # pragma: no cover - depends on external API
            raise ChatCompletionError(f"Groq chat completion failed: {exc}") from exc

        content = response.choices[0].message.content.strip()
        LOGGER.info("Received response from Groq: %s", content)
        return content
