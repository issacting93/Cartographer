#!/usr/bin/env python3
"""
STEP 2: Turn-Level Move Taxonomy Classifier

Decomposes each conversation turn into communicative Moves.
Hybrid approach: deterministic regex for most Moves, LLM for violations and task shifts.

Move Taxonomy (13 types in 4 categories):
  Constraint Lifecycle: PROPOSE_CONSTRAINT, ACCEPT_CONSTRAINT, VIOLATE_CONSTRAINT, RATIFY_CONSTRAINT
  Repair:              REPAIR_INITIATE, REPAIR_EXECUTE, ABANDON_CONSTRAINT
  Task Structure:      STATE_GOAL, TASK_SHIFT, GENERATE_OUTPUT
  Interactional:       REQUEST_CLARIFICATION, PROVIDE_INFORMATION, PASSIVE_ACCEPT
"""

import re
import json
import sys
from typing import List, Optional, Tuple
from pathlib import Path

# Import regex patterns from existing features.py
sys.path.insert(0, str(Path(__file__).parent.parent))
from features import (
    REPAIR_MARKERS,
    CONSTRAINT_HARD,
    CONSTRAINT_SOFT,
    CONSTRAINT_GOAL,
    PASSIVE_PATTERNS,
    count_pattern_matches,
)

from atlas.core.enums import MoveType as MT
from atlas.utils import Move, llm_call_with_retry


# ============= Additional Regex Patterns =============

# AI constraint acceptance patterns
ACCEPT_PATTERNS = [
    r"\b(i'll make sure|i will make sure|i'll ensure|i will ensure)\b",
    r"\b(noted|understood|i understand)\b.*\b(you want|your|the constraint|the requirement)\b",
    r"\b(keeping in mind|with that in mind|taking into account)\b",
    r"\b(i'll focus on|i will focus on|focusing on)\b",
    r"\b(as you (requested|specified|mentioned|asked))\b",
    r"\b(per your (request|instruction|requirement))\b",
    r"\b(i'll stick to|i will stick to|sticking to)\b",
    r"\b(absolutely|of course)[,.]?\s*(i'll|i will|let me)\b",
]

# AI repair execution patterns
REPAIR_EXECUTE_PATTERNS = [
    r"\b(i apologize|my apologies|sorry about that|you'?re right)\b",
    r"\b(let me (correct|fix|adjust|revise|redo|try again))\b",
    r"\b(i (misunderstood|missed that|overlooked))\b",
    r"\b(here'?s the (corrected|revised|updated|fixed) version)\b",
    r"\b(i see what you mean|good catch|thanks for clarifying)\b",
]

# AI clarification request patterns
CLARIFICATION_PATTERNS = [
    r"\b(could you (clarify|specify|elaborate|explain))\b",
    r"\b(do you mean|did you mean|are you (referring|looking))\b",
    r"\b(can you (tell me more|provide more|give me more))\b",
    r"\b(what (exactly|specifically) (do you|would you|are you))\b",
    r"\b(just to (clarify|confirm|make sure))\b",
    r"\b(before i (proceed|continue|start|begin))\b.*\?",
    r"\b(a few questions|some questions|i have a question)\b",
]


# ============= Deterministic Move Detectors =============

def detect_propose_constraint(text: str) -> List[Move]:
    """Detect user proposing new constraints. Uses features.py patterns."""
    moves = []
    text_lower = text.lower()

    for patterns, hardness in [
        (CONSTRAINT_HARD, "hard"),
        (CONSTRAINT_SOFT, "soft"),
        (CONSTRAINT_GOAL, "goal"),
    ]:
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Extract surrounding context for the span
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 40)
                span = text[start:end].strip()
                moves.append(Move(
                    move_type=MT.PROPOSE_CONSTRAINT,
                    text_span=span[:120],
                    confidence=0.85,
                    method="regex",
                    actor="user",
                ))
                break  # One detection per pattern group

    return moves


def detect_state_goal(text: str, turn_index: int) -> List[Move]:
    """Detect user stating a task goal."""
    moves = []
    for pattern in CONSTRAINT_GOAL:
        match = re.search(pattern, text.lower(), re.IGNORECASE)
        if match:
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 60)
            span = text[start:end].strip()
            # Higher confidence for early turns
            confidence = 0.9 if turn_index < 4 else 0.7
            moves.append(Move(
                move_type=MT.STATE_GOAL,
                text_span=span[:120],
                confidence=confidence,
                method="regex",
                actor="user",
            ))
            return moves  # One goal per turn
    return moves


def detect_repair_initiate(text: str) -> List[Move]:
    """Detect user initiating repair. Uses features.py REPAIR_MARKERS."""
    if count_pattern_matches(text, REPAIR_MARKERS) > 0:
        # Find the matching span
        text_lower = text.lower()
        for pattern in REPAIR_MARKERS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                start = max(0, match.start() - 10)
                end = min(len(text), match.end() + 40)
                span = text[start:end].strip()
                return [Move(
                    move_type=MT.REPAIR_INITIATE,
                    text_span=span[:120],
                    confidence=0.9,
                    method="regex",
                    actor="user",
                )]
    return []


def detect_passive_accept(text: str) -> List[Move]:
    """Detect user passively accepting. Uses features.py PASSIVE_PATTERNS."""
    text_stripped = text.strip().lower()
    if len(text_stripped) > 50:
        return []
    for pattern in PASSIVE_PATTERNS:
        if re.match(pattern, text_stripped):
            return [Move(
                move_type=MT.PASSIVE_ACCEPT,
                text_span=text_stripped[:60],
                confidence=0.95,
                method="regex",
                actor="user",
            )]
    return []


def detect_accept_constraint(text: str) -> List[Move]:
    """Detect AI accepting/acknowledging a user constraint."""
    text_lower = text.lower()
    for pattern in ACCEPT_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 40)
            span = text[start:end].strip()
            return [Move(
                move_type=MT.ACCEPT_CONSTRAINT,
                text_span=span[:120],
                confidence=0.8,
                method="regex",
                actor="assistant",
            )]
    return []


def detect_repair_execute(text: str) -> List[Move]:
    """Detect AI executing a repair (acknowledging error)."""
    text_lower = text.lower()
    for pattern in REPAIR_EXECUTE_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 40)
            span = text[start:end].strip()
            return [Move(
                move_type=MT.REPAIR_EXECUTE,
                text_span=span[:120],
                confidence=0.85,
                method="regex",
                actor="assistant",
            )]
    return []


def detect_request_clarification(text: str) -> List[Move]:
    """Detect AI asking for clarification."""
    text_lower = text.lower()
    for pattern in CLARIFICATION_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 40)
            span = text[start:end].strip()
            return [Move(
                move_type=MT.REQUEST_CLARIFICATION,
                text_span=span[:120],
                confidence=0.85,
                method="regex",
                actor="assistant",
            )]
    return []


# ============= Inferred Move Detectors =============

def infer_ratification(
    prev_moves: List[Move],
    current_moves: List[Move],
    current_role: str,
) -> Optional[Move]:
    """
    Lazy ratification: if AI accepted a constraint in the previous turn,
    and the user's current turn does not contain a repair, infer RATIFY.
    """
    if current_role != "user":
        return None

    prev_had_accept = any(m.move_type == "ACCEPT_CONSTRAINT" for m in prev_moves)
    current_has_repair = any(m.move_type == "REPAIR_INITIATE" for m in current_moves)

    if prev_had_accept and not current_has_repair:
        return Move(
            move_type=MT.RATIFY_CONSTRAINT,
            text_span="[implicit: no objection after acceptance]",
            confidence=0.7,
            method="inferred",
            actor="user",
        )
    return None


def infer_abandon(
    current_moves: List[Move],
    prev_had_violation: bool,
) -> Optional[Move]:
    """
    If user passively accepts after a constraint violation,
    infer ABANDON_CONSTRAINT.
    """
    if not prev_had_violation:
        return None

    has_passive = any(m.move_type == "PASSIVE_ACCEPT" for m in current_moves)
    if has_passive:
        return Move(
            move_type=MT.ABANDON_CONSTRAINT,
            text_span="[passive acceptance after violation]",
            confidence=0.75,
            method="inferred",
            actor="user",
        )
    return None


def infer_provide_information(
    current_moves: List[Move],
    prev_had_clarification: bool,
    current_role: str,
) -> Optional[Move]:
    """
    If user responds to a clarification request and it's not a repair,
    infer PROVIDE_INFORMATION.
    """
    if current_role != "user" or not prev_had_clarification:
        return None

    has_repair = any(m.move_type == "REPAIR_INITIATE" for m in current_moves)
    has_passive = any(m.move_type == "PASSIVE_ACCEPT" for m in current_moves)
    if not has_repair and not has_passive:
        return Move(
            move_type=MT.PROVIDE_INFORMATION,
            text_span="[response to clarification request]",
            confidence=0.7,
            method="inferred",
            actor="user",
        )
    return None


def assign_default_assistant_move(
    current_moves: List[Move],
    text: str,
) -> Optional[Move]:
    """
    If assistant turn has no specific moves and content is substantial,
    assign GENERATE_OUTPUT as default.
    """
    if current_moves:
        return None
    if len(text.strip()) > 80:
        return Move(
            move_type=MT.GENERATE_OUTPUT,
            text_span=text[:80].strip() + "...",
            confidence=0.6,
            method="inferred",
            actor="assistant",
        )
    return None


# ============= Aspirational Constraint Filter =============

ASPIRATIONAL_PATTERNS = [
    r"^(be |provide |ensure |maintain )(accurate|correct|proper|good|clear|helpful|high.quality|appropriate)",
    r"^(code|output|response|answer|result).{0,20}(must |should )?(be |remain )?(correct|accurate|functional|proper|good|valid)",
    r"^(deliver|produce|create|generate) (high.quality|accurate|correct|proper)",
    r"^(accurate|correct|helpful|clear|proper|appropriate) (response|output|answer|information|code)",
]


def is_aspirational_constraint(text: str) -> bool:
    """
    Check if a constraint is aspirational (quality standard) vs verifiable (binary pass/fail).

    Aspirational: "Provide accurate information", "Code must be correct"
    Verifiable: "Use Python", "No more than 500 words", "Output in JSON format"
    """
    text_lower = text.lower().strip()
    for pattern in ASPIRATIONAL_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    # Very short constraints with only quality words
    quality_words = {
        "accurate", "correct", "proper", "good", "clear", "helpful",
        "appropriate", "valid", "functional", "quality", "consistent",
    }
    tokens = set(text_lower.split())
    content_tokens = tokens - {"be", "must", "should", "the", "a", "an", "and", "or", "is", "are", "provide", "ensure", "maintain"}
    if len(content_tokens) <= 3 and content_tokens & quality_words:
        return True
    return False


# ============= LLM-Based Detectors =============

VIOLATION_PROMPT = """Given these active constraints and the AI's response, identify which constraints (if any) are CLEARLY violated.

RULES — only flag a violation when:
- The response DIRECTLY contradicts or ignores a specific, verifiable constraint
- The response does something the constraint explicitly forbids
- The response completely omits something the constraint requires AND the response addresses that topic

Do NOT flag:
- Partial completions (the AI addressed the constraint but didn't finish)
- Stylistic differences (formatting, tone, length variations)
- Aspirational quality standards (these have already been filtered out)

ACTIVE CONSTRAINTS:
{constraints}

AI RESPONSE (excerpt):
{response}

For each violated constraint, respond with a JSON array. Each item has "constraint_index" (0-based), "reason" (short explanation), and "confidence" (0.0-1.0).
If no violations, respond with [].

Respond with JSON only."""

TASK_SHIFT_PROMPT = """The user's original goal was:
"{original_goal}"

The user now says:
"{user_text}"

Has the user COMPLETELY ABANDONED their original goal and started a FUNDAMENTALLY DIFFERENT task?

Only flag as a shift if the user has moved to an entirely different subject with no connection to the original goal.
Do NOT flag as a shift:
- Refining, narrowing, or expanding the original goal
- Adding new constraints or requirements to the same task
- Asking follow-up questions about the same topic
- Iterating on a previous attempt at the same goal
- Requesting a different approach to the same problem

Respond with JSON: {{"is_shift": true/false, "confidence": 0.0-1.0, "new_goal": "..." or null}}"""


async def detect_violations_llm(
    assistant_text: str,
    active_constraints: List[str],
    client,
    model: str,
) -> List[Move]:
    """Use LLM to detect constraint violations in assistant output."""
    if not active_constraints:
        return []

    # Only check substantial assistant outputs
    if len(assistant_text.strip()) < 50:
        return []

    # Filter to verifiable constraints only (skip aspirational meta-goals)
    verifiable = [
        (orig_idx, c)
        for orig_idx, c in enumerate(active_constraints)
        if not is_aspirational_constraint(c)
    ]
    if not verifiable:
        return []

    constraints_text = "\n".join(
        f"  [{seq}] {c}" for seq, (_, c) in enumerate(verifiable)
    )
    response_excerpt = assistant_text[:1500]

    prompt = VIOLATION_PROMPT.format(
        constraints=constraints_text,
        response=response_excerpt,
    )

    result = await llm_call_with_retry(
        client, model,
        system_prompt="You detect constraint violations. Be strict — only flag clear, unambiguous violations. Output JSON only.",
        user_prompt=prompt,
        max_tokens=200,
    )

    if not result:
        return []

    try:
        violations = json.loads(result)
        if not isinstance(violations, list):
            return []
    except json.JSONDecodeError:
        return []

    moves = []
    for v in violations:
        idx = v.get("constraint_index", 0)
        confidence = v.get("confidence", 0.5)
        # Only accept high-confidence violations
        if confidence < 0.7:
            continue
        # Map back to original constraint via verifiable index
        if idx < len(verifiable):
            _, constraint_text = verifiable[idx]
        else:
            continue
        reason = v.get("reason", "")
        moves.append(Move(
            move_type=MT.VIOLATE_CONSTRAINT,
            text_span=f"[violates: {constraint_text[:60]}] {reason[:40]}",
            confidence=confidence,
            method="llm",
            actor="assistant",
        ))

    return moves


async def detect_task_shift_llm(
    user_text: str,
    original_goal: str,
    client,
    model: str,
) -> Optional[Move]:
    """Use LLM to detect if user has shifted the task goal."""
    if not original_goal or len(user_text.strip()) < 20:
        return None

    # Only check turns with goal-like language
    has_goal_language = count_pattern_matches(user_text, CONSTRAINT_GOAL) > 0
    if not has_goal_language:
        return None

    prompt = TASK_SHIFT_PROMPT.format(
        original_goal=original_goal[:200],
        user_text=user_text[:500],
    )

    result = await llm_call_with_retry(
        client, model,
        system_prompt="You detect goal changes. Output JSON only.",
        user_prompt=prompt,
        max_tokens=100,
    )

    if not result:
        return None

    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        return None

    if data.get("is_shift"):
        new_goal = data.get("new_goal", "")
        confidence = data.get("confidence", 0.7)
        if confidence < 0.7:
            return None
        return Move(
            move_type=MT.TASK_SHIFT,
            text_span=f"[shift to: {new_goal[:80]}]",
            confidence=confidence,
            method="llm",
            actor="user",
        )
    return None


# ============= Main Classification =============

async def classify_moves(
    messages: List[dict],
    primary_constraints: List[str],
    evidence: dict,
    task_goal: str = "",
    client=None,
    model: str = "gpt-4o-mini",
) -> List[dict]:
    """
    Classify all turns into Moves. Returns messages with 'moves' field added.

    Args:
        messages: Raw conversation messages [{role, content}, ...]
        primary_constraints: From classify_task_first.py output
        evidence: {constraint_turns, violation_turns, repair_turns}
        task_goal: From classify_task_first.py output
        client: AsyncOpenAI client (None = skip LLM calls)
        model: LLM model name
    """
    annotated = []
    prev_moves: List[Move] = []
    prev_had_violation = False
    prev_had_clarification = False
    repair_initiated = False  # Gates REPAIR_EXECUTE: only fire after user REPAIR_INITIATE

    for i, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role not in ("user", "assistant"):
            annotated.append({**msg, "turn_index": i, "moves": []})
            prev_moves = []
            continue

        turn_moves: List[Move] = []

        if role == "user":
            # Deterministic detectors
            turn_moves.extend(detect_propose_constraint(content))
            turn_moves.extend(detect_state_goal(content, i))
            turn_moves.extend(detect_repair_initiate(content))
            turn_moves.extend(detect_passive_accept(content))

            # Inferred moves
            ratify = infer_ratification(prev_moves, turn_moves, role)
            if ratify:
                turn_moves.append(ratify)

            abandon = infer_abandon(turn_moves, prev_had_violation)
            if abandon:
                turn_moves.append(abandon)

            info = infer_provide_information(turn_moves, prev_had_clarification, role)
            if info:
                turn_moves.append(info)

            # Track repair initiation for gating REPAIR_EXECUTE on assistant turns
            if any(m.move_type == "REPAIR_INITIATE" for m in turn_moves):
                repair_initiated = True

            # LLM: task shift detection
            if client and task_goal:
                shift = await detect_task_shift_llm(content, task_goal, client, model)
                if shift:
                    turn_moves.append(shift)

        elif role == "assistant":
            # Deterministic detectors
            turn_moves.extend(detect_accept_constraint(content))
            # Only detect REPAIR_EXECUTE if user previously initiated repair
            if repair_initiated:
                turn_moves.extend(detect_repair_execute(content))
                # Reset flag once repair execute is emitted
                if any(m.move_type == "REPAIR_EXECUTE" for m in turn_moves):
                    repair_initiated = False
            turn_moves.extend(detect_request_clarification(content))

            # LLM: violation detection
            if client and primary_constraints:
                violations = await detect_violations_llm(
                    content, primary_constraints, client, model
                )
                turn_moves.extend(violations)

            # Default: GENERATE_OUTPUT if no other moves
            default = assign_default_assistant_move(turn_moves, content)
            if default:
                turn_moves.append(default)

        # Singular move types (only one per turn)
        SINGULAR_MOVES = {
            MT.STATE_GOAL, MT.TASK_SHIFT, MT.ACCEPT_CONSTRAINT, 
            MT.REPAIR_EXECUTE, MT.REQUEST_CLARIFICATION, 
            MT.RATIFY_CONSTRAINT, MT.GENERATE_OUTPUT, MT.PASSIVE_ACCEPT,
            MT.ABANDON_CONSTRAINT
        }

        # Deduplicate: singular types by type, others by (type, text_span)
        seen_singular = {}
        seen_plural = {}
        
        for m in turn_moves:
            if m.move_type in SINGULAR_MOVES:
                if m.move_type not in seen_singular or m.confidence > seen_singular[m.move_type].confidence:
                    seen_singular[m.move_type] = m
            else:
                key = (m.move_type, m.text_span)
                if key not in seen_plural or m.confidence > seen_plural[key].confidence:
                    seen_plural[key] = m
                    
        turn_moves = list(seen_singular.values()) + list(seen_plural.values())

        # Track state for next iteration
        prev_had_violation = any(m.move_type == MT.VIOLATE_CONSTRAINT for m in turn_moves)
        prev_had_clarification = any(m.move_type == MT.REQUEST_CLARIFICATION for m in turn_moves)
        prev_moves = turn_moves

        annotated.append({
            **msg,
            "turn_index": i,
            "moves": [
                {
                    "move_type": m.move_type,
                    "text_span": m.text_span,
                    "confidence": m.confidence,
                    "method": m.method,
                    "actor": m.actor,
                }
                for m in turn_moves
            ],
        })

    return annotated


def classify_moves_deterministic(
    messages: List[dict],
    primary_constraints: List[str],
    evidence: dict,
    task_goal: str = "",
) -> List[dict]:
    """
    Synchronous, deterministic-only version (no LLM calls).
    Useful for testing and when LLM is unavailable.
    """
    import asyncio
    return asyncio.run(
        classify_moves(messages, primary_constraints, evidence, task_goal, client=None)
    )
