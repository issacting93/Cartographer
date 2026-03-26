#!/usr/bin/env python3
from enum import Enum

class NodeType(str, Enum):
    CONVERSATION = "Conversation"
    TURN = "Turn"
    MOVE = "Move"
    CONSTRAINT = "Constraint"
    VIOLATION_EVENT = "ViolationEvent"
    INTERACTION_MODE = "InteractionMode"

class EdgeType(str, Enum):
    CONTAINS = "CONTAINS"
    NEXT = "NEXT"
    HAS_MOVE = "HAS_MOVE"
    VIOLATES = "VIOLATES"
    TRIGGERS = "TRIGGERS"
    REPAIRS = "REPAIRS"
    RATIFIES = "RATIFIES"
    OPERATES_IN = "OPERATES_IN"

class MoveType(str, Enum):
    # Constraint Lifecycle
    PROPOSE_CONSTRAINT = "PROPOSE_CONSTRAINT"
    ACCEPT_CONSTRAINT = "ACCEPT_CONSTRAINT"           # Acknowledgment token: "sure", "noted", "here is" (Clark & Brennan 1991)
    ACKNOWLEDGE_CONSTRAINT = "ACKNOWLEDGE_CONSTRAINT" # Understanding demonstration: AI restates/paraphrases (Clark & Brennan 1991)
    VIOLATE_CONSTRAINT = "VIOLATE_CONSTRAINT"
    RATIFY_CONSTRAINT = "RATIFY_CONSTRAINT"
    SILENT_COMPLY = "SILENT_COMPLY"                   # Unmarked compliance: output complies without any linguistic marking (Clark & Brennan 1991)
    # Repair
    REPAIR_INITIATE = "REPAIR_INITIATE"
    REPAIR_EXECUTE = "REPAIR_EXECUTE"
    SELF_REPAIR = "SELF_REPAIR"                       # AI self-initiated self-repair, unprompted (Schegloff 1977 SISR)
    ABANDON_CONSTRAINT = "ABANDON_CONSTRAINT"
    ESCALATE = "ESCALATE"
    REPAIR_SUCCEED = "REPAIR_SUCCEED"
    REPAIR_FAIL = "REPAIR_FAIL"
    # Task Structure
    STATE_GOAL = "STATE_GOAL"
    TASK_SHIFT = "TASK_SHIFT"
    GENERATE_OUTPUT = "GENERATE_OUTPUT"
    # Interactional
    REQUEST_CLARIFICATION = "REQUEST_CLARIFICATION"
    PROVIDE_INFORMATION = "PROVIDE_INFORMATION"
    PASSIVE_ACCEPT = "PASSIVE_ACCEPT"

class ConstraintState(str, Enum):
    STATED = "STATED"
    ACTIVE = "ACTIVE"
    VIOLATED = "VIOLATED"
    REPAIRED = "REPAIRED"
    ABANDONED = "ABANDONED"
    SURVIVED = "SURVIVED"

class InteractionMode(str, Enum):
    LISTENER = "LISTENER"
    ADVISOR = "ADVISOR"
    EXECUTOR = "EXECUTOR"
    AMBIGUOUS = "AMBIGUOUS"

class ModeViolationType(str, Enum):
    UNSOLICITED_ADVICE = "UNSOLICITED_ADVICE"
    PREMATURE_EXECUTION = "PREMATURE_EXECUTION"
    EXECUTION_AVOIDANCE = "EXECUTION_AVOIDANCE"
    NONE = ""

class StabilityClass(str, Enum):
    TASK_MAINTAINED = "Task Maintained"
    CONSTRAINT_DRIFT = "Constraint Drift"
    AGENCY_COLLAPSE = "Agency Collapse"
    TASK_SHIFT = "Task Shift"
    NO_CONSTRAINTS = "No Constraints"
