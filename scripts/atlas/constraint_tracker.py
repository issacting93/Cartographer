#!/usr/bin/env python3
"""
Constraint Lifecycle State Machine

Tracks each constraint through its lifecycle:
  STATED -> ACTIVE -> VIOLATED -> REPAIRED -> ACTIVE (cycle)
                        |
                        +-> ABANDONED (terminal)

  ACTIVE -> SURVIVED (conversation ends with constraint intact)

Seeds from classify_task_first.py evidence data, then advances
based on Move annotations from move_classifier.py.
"""

import re
from typing import List, Optional, Tuple, Set
from atlas.core.enums import ConstraintState as CS, MoveType as MT
from atlas.utils import (
    ConstraintState,  # This is the Pydantic model 'Constraint'
    ConversationConstraintTrack,
    jaccard_similarity,
)


# ============= Constraint Initialization =============

def classify_constraint_hardness(text: str) -> str:
    """Classify a constraint as hard, soft, or goal based on text."""
    text_lower = text.lower()

    hard_indicators = [
        r"\b(must|need to|require|only|never|always)\b",
        r"\b(no more than|at least|maximum|minimum|exactly)\b",
        r"\b(cannot|can't|won't|will not)\b",
        r"\$[\d,]+|\d+\s*(hours|days|dollars|percent|%)",
    ]

    soft_indicators = [
        r"\b(prefer|ideally|if possible|would like|hope)\b",
        r"\b(rather|better if|nice to have)\b",
    ]

    goal_indicators = [
        r"\b(goal|objective|aim|target|trying to|want to|looking for)\b",
    ]

    hard_score = sum(1 for p in hard_indicators if re.search(p, text_lower))
    soft_score = sum(1 for p in soft_indicators if re.search(p, text_lower))
    goal_score = sum(1 for p in goal_indicators if re.search(p, text_lower))

    if hard_score >= soft_score and hard_score >= goal_score:
        return "hard"
    if goal_score >= soft_score:
        return "goal"
    return "soft"


def initialize_constraints(
    primary_constraints: List[str],
    evidence: dict,
) -> List[ConstraintState]:
    """
    Seed constraint state machines from classify_task_first.py output.

    Args:
        primary_constraints: List of constraint text strings
        evidence: {constraint_turns: [...], violation_turns: [...], repair_turns: [...]}
    """
    constraint_turns = evidence.get("constraint_turns", [])
    constraints = []

    for i, text in enumerate(primary_constraints):
        introduced_at = constraint_turns[i] if i < len(constraint_turns) else 0
        hardness = classify_constraint_hardness(text)

        constraints.append(ConstraintState(
            constraint_id=f"c_{i}",
            text=text,
            hardness=hardness,
            current_state=CS.STATED,
            introduced_at=introduced_at,
        ))

    return constraints


# ============= Move-to-Constraint Matching =============

def match_move_to_constraint(
    move_text: str,
    constraints: List[ConstraintState],
    threshold: float = 0.15,
) -> Optional[str]:
    """
    Determine which constraint a Move is about using token similarity.

    Returns constraint_id of best match, or None if below threshold.
    """
    if not constraints:
        return None

    best_match = None
    best_score = 0.0

    for c in constraints:
        score = jaccard_similarity(move_text, c.text)
        if score > best_score:
            best_score = score
            best_match = c.constraint_id

    if best_score >= threshold:
        return best_match
    return None


def match_violation_to_constraint(
    violation_span: str,
    constraints: List[ConstraintState],
) -> Optional[str]:
    """
    Match a VIOLATE_CONSTRAINT move to a specific constraint.
    Violation spans from LLM often contain the constraint text directly.
    """
    # Try direct matching first (LLM violations often name the constraint)
    for c in constraints:
        c_tokens = set(c.text.lower().split())
        span_lower = violation_span.lower()
        if len(c_tokens) >= 2:
            overlap = sum(1 for t in c_tokens if t in span_lower)
            if overlap >= len(c_tokens) * 0.4:
                return c.constraint_id

    # Fall back to Jaccard
    return match_move_to_constraint(violation_span, constraints, threshold=0.1)


# ============= State Machine Advancement =============

def advance_constraints(
    constraints: List[ConstraintState],
    turn_index: int,
    moves: List[dict],
    repair_pending: Optional[set] = None,
    unmatched_violations: Optional[list] = None,
) -> Tuple[List[ConstraintState], set, list]:
    """
    Process all Moves in a turn and advance constraint state machines.

    Args:
        constraints: Current list of ConstraintState objects
        turn_index: Index of the current turn
        moves: List of move dicts from move_classifier output
        repair_pending: Set of constraint_ids with pending user repair initiation
        unmatched_violations: Accumulator for violations that couldn't be matched to any constraint

    Returns:
        (constraints, repair_pending, unmatched_violations) — updated state, pending set, and unmatched list.
    """
    if repair_pending is None:
        repair_pending = set()
    if unmatched_violations is None:
        unmatched_violations = []

    constraints_by_id = {c.constraint_id: c for c in constraints}

    for move in moves:
        move_type = move.get("move_type", "")
        text_span = move.get("text_span", "")

        if move_type == MT.ACCEPT_CONSTRAINT:
            # AI accepts -> transition STATED constraints to ACTIVE
            for c in constraints:
                if c.current_state == CS.STATED:
                    c.transition(turn_index, CS.ACTIVE)

        elif move_type == MT.RATIFY_CONSTRAINT:
            # User ratifies -> transition STATED constraints to ACTIVE
            for c in constraints:
                if c.current_state == CS.STATED:
                    c.transition(turn_index, CS.ACTIVE)

        elif move_type == MT.VIOLATE_CONSTRAINT:
            # Only consider constraints that have been introduced by this turn
            eligible = [c for c in constraints if c.introduced_at <= turn_index]
            target_id = match_violation_to_constraint(text_span, eligible)
            if target_id and target_id in constraints_by_id:
                target = constraints_by_id[target_id]
                if target.current_state in (CS.ACTIVE, CS.STATED):
                    target.transition(turn_index, CS.VIOLATED)
            else:
                # Log unmatched violation — do NOT assign to any constraint
                unmatched_violations.append({
                    "turn_index": turn_index,
                    "text_span": text_span[:200],
                })

        elif move_type == MT.REPAIR_INITIATE:
            # User initiates repair -> mark specific violated constraint(s) as pending
            target_id = match_move_to_constraint(text_span, [
                c for c in constraints if c.current_state == CS.VIOLATED
            ])
            if target_id:
                repair_pending.add(target_id)
            else:
                # If can't match, mark all violated constraints as pending
                for c in constraints:
                    if c.current_state == CS.VIOLATED:
                        repair_pending.add(c.constraint_id)

        elif move_type == MT.REPAIR_EXECUTE:
            # AI executes repair -> only transition constraints with pending repair
            repaired_any = False
            for c in constraints:
                if c.constraint_id in repair_pending and c.current_state == CS.VIOLATED:
                    c.transition(turn_index, CS.REPAIRED)
                    repaired_any = True
            if repaired_any:
                repair_pending.clear()

        elif move_type == MT.ABANDON_CONSTRAINT:
            # User abandons -> transition VIOLATED constraints to ABANDONED
            for c in constraints:
                if c.current_state == CS.VIOLATED:
                    c.transition(turn_index, CS.ABANDONED)
            # Clear any pending repairs for abandoned constraints
            repair_pending -= {c.constraint_id for c in constraints if c.current_state == CS.ABANDONED}

    return constraints, repair_pending, unmatched_violations


# ============= Main Entry Point =============

def build_constraint_tracker(
    messages_with_moves: List[dict],
    primary_constraints: List[str],
    evidence: dict,
) -> ConversationConstraintTrack:
    """
    Build constraint lifecycle tracking from Move-annotated messages.

    Args:
        messages_with_moves: Output of move_classifier.classify_moves()
        primary_constraints: From classify_task_first.py output
        evidence: {constraint_turns, violation_turns, repair_turns}

    Returns:
        ConversationConstraintTrack with per-constraint lifecycle data.
    """
    conversation_id = ""
    if messages_with_moves:
        conversation_id = messages_with_moves[0].get("conversation_id", "unknown")

    # Initialize constraints from existing classification
    constraints = initialize_constraints(primary_constraints, evidence)

    if not constraints:
        return ConversationConstraintTrack(
            conversation_id=conversation_id,
            constraints=[],
        )

    # Activate constraints that have no explicit acceptance
    # (if evidence says they were introduced early, assume active)
    violation_turns = set(evidence.get("violation_turns", []))
    for c in constraints:
        if c.current_state == CS.STATED and c.introduced_at <= 2:
            c.transition(c.introduced_at, CS.ACTIVE)

    # Process each turn's moves
    total_turns = len(messages_with_moves)
    repair_pending: Set[str] = set()
    all_unmatched_violations: list = []
    for msg in messages_with_moves:
        turn_index = msg.get("turn_index", 0)
        moves = msg.get("moves", [])

        if moves:
            constraints, repair_pending, all_unmatched_violations = advance_constraints(
                constraints, turn_index, moves, repair_pending, all_unmatched_violations
            )

    # Finalize: mark surviving constraints
    for c in constraints:
        if c.current_state in (CS.ACTIVE, CS.STATED):
            c.current_state = CS.SURVIVED
            c.state_history.append((total_turns, CS.SURVIVED))
            c.lifespan = total_turns - c.introduced_at

    return ConversationConstraintTrack(
        conversation_id=conversation_id,
        constraints=constraints,
        unmatched_violations=len(all_unmatched_violations),
    )
