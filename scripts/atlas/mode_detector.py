#!/usr/bin/env python3
"""
Interaction Mode Detector

Detects user-requested mode (LISTENER/ADVISOR/EXECUTOR) and AI-enacted mode
per turn pair. Identifies mode violations: when AI operates in a mode the
user did not request.

Mode Violations:
  UNSOLICITED_ADVICE:   User in LISTENER mode, AI gives advice
  PREMATURE_EXECUTION:  User in ADVISOR mode, AI generates full deliverable
  EXECUTION_AVOIDANCE:  User in EXECUTOR mode, AI asks more questions
"""

import re
import math
from typing import List, Optional, Tuple

from atlas.core.enums import InteractionMode as IM, ModeViolationType as MVT
from atlas.utils import ModeAnnotation, llm_call_with_retry


# ============= User Mode Detection (Regex) =============

LISTENER_SIGNALS = [
    r"^(here'?s?|this is|let me (tell|explain|describe|share))\b",
    r"^(the situation is|background:|context:|for context)\b",
    r"^(i have|we have|there are|there'?s)\b.{20,}(?<!\?)$",
    r"^(so basically|so the thing is|the problem is)\b",
    r"^(i'?m? (working on|dealing with|facing))\b.{20,}(?<!\?)$",
    r"^(fyi|just so you know|for your (information|reference))\b",
]

ADVISOR_SIGNALS = [
    r"\b(what do you (think|suggest|recommend))\b",
    r"\b(should i|would you (recommend|suggest|advise))\b",
    r"\b(which (is|would be|do you think is) (better|best|preferred))\b",
    r"\b(any (suggestions?|advice|recommendations?|thoughts|ideas))\b",
    r"\b(pros and cons|compare|evaluate|assess)\b",
    r"\b(is (it|this|that) (a good|the right|the best))\b",
    r"\b(what('?s| is| are) (the best|a good|your) (way|approach|strategy))\b",
    r"\b(help me (decide|choose|pick|figure out))\b",
]

EXECUTOR_SIGNALS = [
    r"^(write|generate|create|make|build|produce|draft|compose)\b",
    r"^(give me|show me|provide|list|prepare)\b.*\b(a|an|the|some)\b",
    r"\b(translate|convert|rewrite|summarize|format|transform)\b",
    r"\b(code|script|function|program|implementation)\b.*\b(for|that|which|to)\b",
    r"^(can you|could you|please)\b.*\b(write|make|create|build|generate)\b",
    r"\b(i need|i want) (a|an|the|you to (write|make|create|build))\b",
    r"^(fix|update|modify|change|edit|refactor)\b",
    r"\b(output|deliverable|result|product)\b",
]


def detect_user_mode(text: str) -> Tuple[str, float]:
    """
    Detect user-requested interaction mode from message text.
    Returns (mode, confidence).
    """
    text_lower = text.lower().strip()

    # Short passive responses don't signal a mode
    if len(text_lower) < 15:
        return IM.AMBIGUOUS, 0.3

    scores = {IM.LISTENER: 0, IM.ADVISOR: 0, IM.EXECUTOR: 0}

    for pattern in LISTENER_SIGNALS:
        if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
            scores[IM.LISTENER] += 1

    for pattern in ADVISOR_SIGNALS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            scores[IM.ADVISOR] += 1

    for pattern in EXECUTOR_SIGNALS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            scores[IM.EXECUTOR] += 1

    total = sum(scores.values())
    if total == 0:
        return IM.AMBIGUOUS, 0.3

    best_mode = max(scores, key=scores.get)
    confidence = scores[best_mode] / max(total, 1)

    # Require at least 0.4 margin to avoid ambiguity
    if confidence < 0.4:
        return IM.AMBIGUOUS, confidence

    return best_mode, min(confidence, 0.95)


# ============= AI Mode Detection (Structural) =============

AI_ADVICE_PATTERNS = [
    r"\b(i (would |)recommend|i (would |)suggest|you (should|could|might))\b",
    r"\b(consider|you may want to|it would be (best|better|wise))\b",
    r"\b(in my (opinion|view|assessment))\b",
    r"\b(the (best|better|preferred) (option|choice|approach))\b",
    r"\b(alternatively|on the other hand|however)\b",
    r"\b(pros|cons|advantages|disadvantages|trade-?offs)\b",
]

AI_CLARIFICATION_PATTERNS = [
    r"\b(could you (clarify|specify|elaborate))\b",
    r"\b(can you (tell|provide|give) me more)\b",
    r"\b(what (exactly|specifically))\b.*\?",
    r"\b(before (i|we) (proceed|start|begin|continue))\b",
    r"\b(i (need|want) to (understand|know|clarify))\b",
]


def detect_ai_mode(text: str) -> Tuple[str, float]:
    """
    Detect what mode the AI is actually operating in based on output structure.
    Returns (mode, confidence).
    """
    text_lower = text.lower().strip()
    text_len = len(text_lower)

    # Count structural signals
    has_code_block = "```" in text
    has_numbered_list = bool(re.search(r'^\d+[\.\)]\s', text, re.MULTILINE))
    question_count = text.count("?")

    advice_signals = sum(
        1 for p in AI_ADVICE_PATTERNS
        if re.search(p, text_lower, re.IGNORECASE)
    )

    clarification_signals = sum(
        1 for p in AI_CLARIFICATION_PATTERNS
        if re.search(p, text_lower, re.IGNORECASE)
    )

    # LISTENER mode: short, acknowledging, questions
    if text_len < 200 and clarification_signals >= 1:
        return IM.LISTENER, 0.8

    if text_len < 100 and question_count >= 2:
        return IM.LISTENER, 0.75

    # ADVISOR mode: evaluative language, comparisons, moderate length
    if advice_signals >= 2 and not has_code_block:
        return IM.ADVISOR, 0.8

    # EXECUTOR mode: substantial output, code blocks, structured deliverables
    if has_code_block or text_len > 800:
        return IM.EXECUTOR, 0.85

    if text_len > 400 and has_numbered_list:
        return IM.EXECUTOR, 0.7

    # Default: EXECUTOR for long outputs, ADVISOR for medium
    if text_len > 300:
        return IM.EXECUTOR, 0.6

    if advice_signals >= 1:
        return IM.ADVISOR, 0.6

    return IM.EXECUTOR, 0.5


# ============= Mode Violation Detection =============

def classify_violation(
    user_mode: str,
    ai_mode: str,
) -> Optional[str]:
    """Determine if there's a mode violation and what type."""
    if user_mode == "AMBIGUOUS":
        return None

    if user_mode == ai_mode:
        return None

    violations = {
        (IM.LISTENER, IM.ADVISOR): MVT.UNSOLICITED_ADVICE,
        (IM.LISTENER, IM.EXECUTOR): MVT.UNSOLICITED_ADVICE,
        (IM.ADVISOR, IM.EXECUTOR): MVT.PREMATURE_EXECUTION,
        (IM.EXECUTOR, IM.LISTENER): MVT.EXECUTION_AVOIDANCE,
        (IM.EXECUTOR, IM.ADVISOR): MVT.EXECUTION_AVOIDANCE,
    }

    return violations.get((user_mode, ai_mode))


# ============= LLM Fallback for Ambiguous =============

AMBIGUOUS_MODE_PROMPT = """Given this user message in a conversation, what is the user asking the AI to do?

USER MESSAGE:
"{text}"

CONTEXT (previous 2 messages):
{context}

Answer with exactly one word: LISTENER, ADVISOR, or EXECUTOR

Where:
- LISTENER = user is providing information, not asking for output
- ADVISOR = user wants evaluation, recommendations, or comparison
- EXECUTOR = user wants the AI to produce a deliverable (text, code, plan, etc.)"""


async def resolve_ambiguous_mode(
    text: str,
    context: str,
    client,
    model: str,
) -> Tuple[str, float]:
    """LLM fallback for ambiguous user mode."""
    prompt = AMBIGUOUS_MODE_PROMPT.format(
        text=text[:500],
        context=context[:500],
    )

    result = await llm_call_with_retry(
        client, model,
        system_prompt="Classify interaction mode. Respond with one word only.",
        user_prompt=prompt,
        max_tokens=10,
    )

    if not result:
        return IM.EXECUTOR, 0.4  # Default assumption

    mode = result.strip().upper()
    if mode in (IM.LISTENER, IM.ADVISOR, IM.EXECUTOR):
        return IM(mode), 0.7

    return IM.EXECUTOR, 0.4


# ============= Main Detection =============

async def detect_mode_violations(
    messages: List[dict],
    client=None,
    model: str = "gpt-4o-mini",
) -> List[ModeAnnotation]:
    """
    Process all turn pairs and detect mode mismatches.

    Args:
        messages: Raw conversation messages [{role, content}, ...]
        client: AsyncOpenAI client (None = skip LLM fallback)
        model: LLM model name

    Returns:
        List of ModeAnnotation, one per user-assistant turn pair.
    """
    annotations = []

    # Iterate over user-assistant pairs
    for i in range(len(messages) - 1):
        user_msg = messages[i]
        ai_msg = messages[i + 1]

        if user_msg.get("role") != "user" or ai_msg.get("role") != "assistant":
            continue

        user_text = user_msg.get("content", "")
        ai_text = ai_msg.get("content", "")

        # Detect user mode
        user_mode, user_conf = detect_user_mode(user_text)

        # LLM fallback for ambiguous
        method = "regex"
        if user_mode == IM.AMBIGUOUS and client:
            # Build context from previous messages
            context_parts = []
            for j in range(max(0, i - 2), i):
                role = messages[j].get("role", "?").upper()
                ctx = messages[j].get("content", "")[:200]
                context_parts.append(f"{role}: {ctx}")
            context = "\n".join(context_parts) if context_parts else "[start of conversation]"

            user_mode, user_conf = await resolve_ambiguous_mode(
                user_text, context, client, model
            )
            method = "llm"

        # Detect AI mode
        ai_mode, ai_conf = detect_ai_mode(ai_text)

        # Check for violation
        mode_match = (user_mode == ai_mode) or (user_mode == IM.AMBIGUOUS)
        violation_type = classify_violation(user_mode, ai_mode)

        annotations.append(ModeAnnotation(
            turn_index=i,
            user_requested=user_mode,
            ai_enacted=ai_mode,
            is_violation=not mode_match,
            violation_type=violation_type,
            confidence=min(user_conf, ai_conf),
            method=method,
        ))

    return annotations


def detect_mode_violations_deterministic(
    messages: List[dict],
) -> List[ModeAnnotation]:
    """Synchronous, deterministic-only version (no LLM fallback)."""
    import asyncio
    return asyncio.run(detect_mode_violations(messages, client=None))
