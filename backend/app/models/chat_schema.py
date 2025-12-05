from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request with question"""
    document_id: str
    question: str
    conversation_history: Optional[list[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Chat response with answer"""
    success: bool
    question: str
    answer: str
    sources: Optional[list[str]] = None
    conversation_id: Optional[str] = None


class ConversationHistory(BaseModel):
    """Complete conversation history"""
    document_id: str
    conversation_id: str
    messages: list[ChatMessage]
    created_at: datetime
    updated_at: datetime
