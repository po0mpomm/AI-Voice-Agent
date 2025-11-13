from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    conversation_id: Optional[str] = None
    language: str = "en"


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None


class TranscriptionResponse(BaseModel):
    text: str

