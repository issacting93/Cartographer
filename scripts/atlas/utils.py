#!/usr/bin/env python3
"""
Shared data classes, constants, and helpers for the Atlas graph pipeline.
"""

import json
import re
import asyncio
import random
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Any, Set
from pathlib import Path
from pydantic import BaseModel, Field


from atlas.core.enums import (
    MoveType, 
    EdgeType, 
    ConstraintState, 
    InteractionMode, 
    ModeViolationType,
    StabilityClass
)
from atlas.core.models import (
    Move, 
    InteractionModeAnnotation as ModeAnnotation,
    Constraint as ConstraintState,
    ConversationMetrics
)

# Keep the aggregate class for now as it has complex properties
class ConversationConstraintTrack(BaseModel):
    """Aggregate constraint lifecycle data for one conversation."""
    conversation_id: str
    constraints: List[ConstraintState] = Field(default_factory=list)
    unmatched_violations: int = 0

    @property
    def total_constraints(self) -> int:
        return len(self.constraints)

    @property
    def survived_count(self) -> int:
        return sum(1 for c in self.constraints if c.current_state == ConstraintState.SURVIVED)

    @property
    def abandoned_count(self) -> int:
        return sum(1 for c in self.constraints if c.current_state == ConstraintState.ABANDONED)

    @property
    def mean_constraint_lifespan(self) -> float:
        if not self.constraints:
            return 0.0
        return sum(c.lifespan for c in self.constraints) / len(self.constraints)

    @property
    def constraint_survival_rate(self) -> float:
        if not self.constraints:
            return 0.0
        return self.survived_count / len(self.constraints)


# ============= Helpers =============

def load_conversation(file_path: str) -> Optional[dict]:
    """Load raw conversation JSON, handling both 'messages' and 'conversation' keys."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        messages = data.get("messages", data.get("conversation", []))
        return {
            "id": data.get("id", Path(file_path).stem),
            "messages": messages,
        }
    except (json.JSONDecodeError, IOError):
        return None


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Token-level Jaccard similarity between two strings."""
    tokens_a = set(text_a.lower().split())
    tokens_b = set(text_b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


async def llm_call_with_retry(
    client,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.0,
    max_tries: int = 4,
    base_delay: float = 1.0,
) -> Optional[str]:
    """Make an LLM call with exponential backoff retry."""
    for attempt in range(max_tries):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content.strip()
            # Strip markdown code fences
            content = re.sub(r'^```json?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
            return content
        except Exception as e:
            msg = str(e).lower()
            retriable = any(k in msg for k in [
                "429", "rate", "limit", "timeout", "503", "502", "500", "connection"
            ])
            if not retriable or attempt == max_tries - 1:
                print(f"  LLM call failed: {str(e)[:80]}")
                return None
            delay = base_delay * (2 ** attempt) + random.random() * 0.5
            await asyncio.sleep(delay)
    return None


def serialize_dataclass(obj: Any) -> Any:
    """Recursively serialize dataclass instances to dicts."""
    if hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)
    if isinstance(obj, list):
        return [serialize_dataclass(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize_dataclass(v) for k, v in obj.items()}
    return obj
