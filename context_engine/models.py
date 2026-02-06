"""
Context Engine: Task Models

Defines the core data structures for the Task-First Interaction Model.
These models support the CUI 2026 paper's "Tasks, Not Turns" framework.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# --- Task Lifecycle Status ---

TaskStatus = Literal["active", "suspended", "completed", "archived"]
NodeType = Literal["Goal", "Constraint", "Preference", "Artifact", "Context"]
NodeSource = Literal["user_pin", "inferred", "imported", "system"]
ConsentLevel = Literal["private", "scoped", "shared"]


# --- Constraint Node (within a Task) ---

class ConstraintNode(BaseModel):
    """
    A typed element within a Task Object.
    Represents goals, constraints, preferences, artifacts, or context.
    """
    id: str = Field(default_factory=lambda: f"node:{uuid.uuid4().hex[:8]}")
    type: NodeType
    label: str
    description: Optional[str] = None
    source: NodeSource = "user_pin"
    active: bool = True      # Is this node currently in scope?
    pinned: bool = False     # Explicitly pinned by user?
    created_at: datetime = Field(default_factory=datetime.utcnow)
    consent: ConsentLevel = "private"
    metadata: Dict[str, Any] = {}


class TaskEdge(BaseModel):
    """
    Relationship between nodes within a Task.
    """
    id: str = Field(default_factory=lambda: f"edge:{uuid.uuid4().hex[:8]}")
    source: str  # Node ID
    target: str  # Node ID
    type: Literal["REQUIRES", "CONFLICTS", "INFORMS", "PART_OF"]
    weight: float = 1.0


# --- Task Object ---

class TaskMetadata(BaseModel):
    """
    Metrics tracked for the CUI 2026 evaluation.
    """
    conversation_turns: int = 0
    restatement_count: int = 0
    constraint_violations: int = 0
    last_resumed_at: Optional[datetime] = None
    interruption_count: int = 0


class TaskObject(BaseModel):
    """
    The core unit of persistence in the Task-First Interaction Model.
    A Task Object contains the goal, constraints, and state for a user's work.
    """
    id: str = Field(default_factory=lambda: f"task:{uuid.uuid4().hex[:12]}")
    user_id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus = "active"
    
    # Content
    nodes: List[ConstraintNode] = []
    edges: List[TaskEdge] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Evaluation metrics
    metrics: TaskMetadata = Field(default_factory=TaskMetadata)
    
    def get_active_nodes(self) -> List[ConstraintNode]:
        """Return only nodes currently in scope."""
        return [n for n in self.nodes if n.active]
    
    def get_pinned_nodes(self) -> List[ConstraintNode]:
        """Return only explicitly pinned nodes."""
        return [n for n in self.nodes if n.pinned]


# --- API Request/Response Models ---

class CreateTaskRequest(BaseModel):
    user_id: str
    name: str
    description: Optional[str] = None
    initial_nodes: List[ConstraintNode] = []


class CreateTaskResponse(BaseModel):
    task_id: str
    ok: bool = True


class TaskListResponse(BaseModel):
    tasks: List[TaskObject]
    active_task_id: Optional[str] = None


class SwitchTaskRequest(BaseModel):
    user_id: str
    task_id: str


class SwitchTaskResponse(BaseModel):
    ok: bool
    task: Optional[TaskObject] = None


class PinEventRequest(BaseModel):
    """
    Pattern 1: Pin to Task
    Reifies text (e.g., from chat) into a Constraint Node.
    """
    user_id: str
    task_id: str
    text: str
    type: NodeType = "Constraint"
    source: NodeSource = "user_pin"


class PinEventResponse(BaseModel):
    node_id: str
    ok: bool = True


class ContextQueryRequest(BaseModel):
    """
    Pattern 3: Context Lens
    Query with explicit scope selection.
    """
    user_id: str
    task_id: str
    scope: List[str] = []  # Node IDs to include (empty = all active)
    prompt: str


class ContextQueryResponse(BaseModel):
    augmented_prompt: str
    active_nodes: List[ConstraintNode]
    scripts: List[str] = []


# --- Logging Models (for Evaluation) ---

class RestatementEvent(BaseModel):
    """
    Logged when a user re-states a constraint.
    Used to measure Restatement Burden in the CUI evaluation.
    """
    task_id: str
    node_id: str
    turn_number: int
    event_type: Literal["explicit_restatement", "implicit_reminder", "system_prompt"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConstraintViolationEvent(BaseModel):
    """
    Logged when the LLM output contradicts an active constraint.
    """
    task_id: str
    node_id: str
    turn_number: int
    violation_description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
