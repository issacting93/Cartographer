#!/usr/bin/env python3
from typing import List, Optional, Tuple, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
from atlas.core.enums import (
    NodeType, 
    MoveType, 
    ConstraintState, 
    InteractionMode, 
    StabilityClass
)

class AtlasBaseModel(BaseModel):
    class Config:
        use_enum_values = True

class Move(AtlasBaseModel):
    move_type: MoveType
    text_span: str
    confidence: float = Field(ge=0.0, le=1.0)
    method: str
    actor: str

class Turn(AtlasBaseModel):
    turn_index: int
    role: str
    content_length: int
    content_preview: str
    move_count: int = 0
    moves: List[Move] = Field(default_factory=list)

class Constraint(AtlasBaseModel):
    constraint_id: str
    text: str
    hardness: str
    current_state: ConstraintState = ConstraintState.STATED
    state_history: List[Tuple[int, ConstraintState]] = Field(default_factory=list)
    introduced_at: int
    last_violation_at: Optional[int] = None
    times_violated: int = 0
    times_repaired: int = 0
    lifespan: int = 0
    final_state: Optional[ConstraintState] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.state_history:
            self.state_history = [(self.introduced_at, ConstraintState.STATED)]

    def transition(self, turn_index: int, new_state: Union[str, ConstraintState]):
        """Advance the state machine."""
        if isinstance(new_state, str):
            new_state = ConstraintState(new_state)
            
        # Guard: a constraint cannot transition before it was introduced
        effective_turn = max(turn_index, self.introduced_at)

        self.current_state = new_state
        self.state_history.append((effective_turn, new_state))
        self.lifespan = max(0, effective_turn - self.introduced_at)

        if new_state == ConstraintState.VIOLATED:
            self.times_violated += 1
            self.last_violation_at = turn_index
        elif new_state == ConstraintState.REPAIRED:
            self.times_repaired += 1
            # Transition back to ACTIVE after repair
            self.current_state = ConstraintState.ACTIVE
            self.state_history.append((turn_index, ConstraintState.ACTIVE))

class ViolationEvent(AtlasBaseModel):
    violation_idx: int
    turn_index: int
    constraint_id: Union[str, Literal["mode"]]
    violation_type: str
    was_repaired: bool = False
    violation_ord: int = 1

class InteractionModeAnnotation(AtlasBaseModel):
    turn_index: int
    user_requested: InteractionMode
    ai_enacted: InteractionMode
    is_violation: bool
    violation_type: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    method: str = "regex"

class Conversation(AtlasBaseModel):
    conv_id: str
    source: str
    domain: str = "general"
    total_turns: int
    stability_class: Optional[StabilityClass] = None
    task_architecture: Optional[str] = None
    constraint_hardness: Optional[str] = None
    task_goal: Optional[str] = None

class Connection(AtlasBaseModel):
    source: str
    target: str
    edge_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
class ConversationMetrics(AtlasBaseModel):
    """Graph-derived metrics for one conversation."""
    conversation_id: str
    drift_velocity: float = 0.0
    agency_tax: float = 0.0
    constraint_half_life: Optional[float] = None
    constraint_survival_rate: float = 0.0
    mode_violation_rate: float = 0.0
    repair_success_rate: float = 0.0
    mean_constraint_lifespan: float = 0.0
    mode_entropy: float = 0.0
    total_violations: int = 0
    total_repairs: int = 0
    total_constraints: int = 0
    total_turns: int = 0
    move_coverage: float = 0.0
    stability_class: str = ""
    task_architecture: str = ""
    constraint_hardness: str = ""
