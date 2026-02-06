"""
Context Engine Module

A Task-First Interaction system for Conversational AI.
Supports the CUI 2026 paper: "Tasks, Not Turns"

Core Components:
- TaskObject: Persistent container for user goals and constraints
- TaskManager: CRUD and lifecycle operations
- API Router: REST endpoints for the three interaction patterns

Patterns Implemented:
1. Pin to Task: /event/pin (Keyword → Constraint Node)
2. Task Shelf: /task/* (Persistent task management)
3. Context Lens: /query/context (Scoped context composition)
"""

from .api import router
from .task_manager import task_manager
from .models import (
    TaskObject,
    ConstraintNode,
    TaskEdge,
    TaskMetadata,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskListResponse,
    PinEventRequest,
    PinEventResponse,
    ContextQueryRequest,
    ContextQueryResponse
)

__all__ = [
    "router",
    "task_manager",
    "TaskObject",
    "ConstraintNode",
    "TaskEdge",
    "TaskMetadata",
    "CreateTaskRequest",
    "CreateTaskResponse",
    "TaskListResponse",
    "PinEventRequest",
    "PinEventResponse",
    "ContextQueryRequest",
    "ContextQueryResponse"
]
