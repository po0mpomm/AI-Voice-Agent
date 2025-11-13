"""Gradio front-end for the Anvaya voice agent."""
from __future__ import annotations

import logging
from typing import Any, Tuple

import gradio as gr
import numpy as np

from .exceptions import VoiceAgentError
from .pipeline import VoiceAgent

LOGGER = logging.getLogger(__name__)


def create_gradio_interface(agent: VoiceAgent) -> gr.Blocks:
    """Build and return the Gradio UI for the agent."""

    with gr.Blocks(title=agent.settings.gradio_title) as demo:
        gr.Markdown("## 🎙️ Anvaya AI Voice Agent\nSpeak and get a friendly reply (Hinglish supported).")

        chatbot = gr.Chatbot(label="Conversation", type="messages", height=350)
        audio_in = gr.Audio(sources=["microphone"], type="numpy", label="🎤 Record your voice")
        text_input = gr.Textbox(label="Or type your message", placeholder="Type here and press Enter...")

        status = gr.Markdown(visible=False)

        def handle_audio(audio: Tuple[int, np.ndarray] | None) -> tuple[Any, str, Any]:
            if audio is None:
                return agent.history, "", gr.update(value="⚠️ No audio received", visible=True)
            sr, data = audio
            try:
                reply = agent.process_audio(sr, data)
                LOGGER.debug("Reply generated from audio: %s", reply)
                return agent.history, "", gr.update(visible=False)
            except VoiceAgentError as exc:
                LOGGER.exception("Audio pipeline failed")
                return agent.history, "", gr.update(value=f"Error: {exc}", visible=True)

        def handle_text(user_text: str) -> tuple[Any, str, Any]:
            if not user_text.strip():
                return agent.history, "", gr.update(value="⚠️ Please enter a message.", visible=True)
            try:
                reply = agent.process_text(user_text)
                LOGGER.debug("Reply generated from text: %s", reply)
                return agent.history, "", gr.update(visible=False)
            except VoiceAgentError as exc:
                LOGGER.exception("Text pipeline failed")
                return agent.history, user_text, gr.update(value=f"Error: {exc}", visible=True)

        audio_in.change(handle_audio, inputs=audio_in, outputs=[chatbot, text_input, status])
        text_input.submit(handle_text, inputs=text_input, outputs=[chatbot, text_input, status])

        def reset_conversation() -> list[dict[str, str]]:
            agent.reset_history()
            return []

        gr.Button("Reset Conversation").click(reset_conversation, outputs=chatbot)

    return demo
