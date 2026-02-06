"""
Chat Models for LLM-backed prototype
"""

from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class ConstraintNode(BaseModel):
    """Constraint from the Context Inventory"""
    id: str
    type: Literal["Goal", "Constraint", "Preference", "Session"]
    label: str
    description: Optional[str] = None


class ChatMessage(BaseModel):
    """Single message in conversation history"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request to the chat endpoint"""
    message: str
    constraints: list[ConstraintNode] = []
    history: list[ChatMessage] = []
    condition: Literal["baseline", "treatment"] = "treatment"


class ChatResponse(BaseModel):
    """Response from the chat endpoint"""
    content: str
    constraint_violations: list[str] = []  # IDs of violated constraints
    model_used: str = "gpt-4o-mini"
