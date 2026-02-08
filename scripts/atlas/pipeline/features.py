#!/usr/bin/env python3
"""
STEP 1: Feature Extraction (Deterministic)

Extracts computable interactional features from conversations.
No labels, no archetypes — just features.

Literature basis:
- Repair: Schegloff et al. (1977)
- Politeness: Brown & Levinson (1987)
- Frustration: Buechel & Hahn (2017)
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path


# ============= LINGUISTIC MARKERS =============

# Repair markers (Schegloff et al., 1977)
REPAIR_MARKERS = [
    r"no,?\s*(i\s+)?meant",
    r"that'?s not what i",
    r"let me clarify",
    r"i said",
    r"as i mentioned",
    r"i already told you",
    r"again,",
    r"for the \w+ time",
    r"no[,.]?\s+(i\s+)?(want|need|said)",
    r"not\s+\w+[,.]?\s+(but|instead)",
    r"\?\?+",
    r"did you (even )?(read|understand|see)",
]

# Constraint markers (deontic expressions)
CONSTRAINT_HARD = [
    r"\b(must|have to|need to|require|only|never|always)\b",
    r"\b(no more than|at least|maximum|minimum|exactly)\b",
    r"\b(cannot|can't|won't|will not)\b",
]

CONSTRAINT_SOFT = [
    r"\b(prefer|ideally|if possible|would like|hope)\b",
    r"\b(rather|better if|nice to have)\b",
]

CONSTRAINT_GOAL = [
    r"\b(goal|objective|aim|target|trying to|want to|looking for)\b",
]

# Politeness markers (Brown & Levinson, 1987)
POLITENESS_POSITIVE = [
    r"\bplease\b",
    r"\bcould you\b",
    r"\bwould you\b",
    r"\bwould you mind\b",
    r"\bthank you\b",
    r"\bthanks\b",
    r"\bi appreciate\b",
    r"\bkindly\b",
]

POLITENESS_NEGATIVE = [
    r"\bjust\s+(give|tell|do)\b",
    r"^(give|tell|do|make|show)\s+me\b",
    r"\bwhatever\b",
    r"\bfine\b$",
    r"\bforget it\b",
]

# Frustration markers
FRUSTRATION_MARKERS = [
    r"!{2,}",
    r"\?{2,}",
    r"\b[A-Z]{4,}\b",
    r"\bugh\b",
    r"\bsigh\b",
    r"\bfrustrat",
    r"\bannoying\b",
    r"\bridiculous\b",
    r"\bwaste of time\b",
]

# Passive acceptance
PASSIVE_PATTERNS = [
    r"^(ok|okay|sure|alright|fine|got it|i see|thanks)\.?$",
    r"^(sounds good|that works|perfect)\.?$",
    r"^(yes|yeah|yep|yup)\.?$",
]


# ============= FEATURE DATACLASS =============

@dataclass
class ConversationFeatures:
    """All computable features for a single conversation."""
    
    # Metadata
    conversation_id: str
    source: str
    total_turns: int
    user_turns: int
    
    # Repair
    repair_count: int
    repair_success_rate: float
    
    # Constraints
    constraint_count: int
    constraint_hard: int
    constraint_soft: int
    constraint_goal: int
    
    # Politeness
    politeness_initial: float
    politeness_final: float
    politeness_delta: float
    
    # Frustration
    frustration_score: float
    frustration_initial: float
    frustration_final: float
    frustration_trend: str  # "increasing", "stable", "decreasing"
    
    # Passivity
    passive_turns: int
    passive_rate: float
    
    # Specificity
    specificity_initial: float
    specificity_final: float
    specificity_delta: float
    
    # Repetition
    verbatim_repeats: int
    
    # Length
    mean_user_length: float


# ============= EXTRACTION FUNCTIONS =============

def count_pattern_matches(text: str, patterns: List[str]) -> int:
    """Count how many patterns match in text."""
    text_lower = text.lower()
    count = 0
    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            count += 1
    return count


def calculate_politeness_score(text: str) -> float:
    """Calculate politeness score (-1 to +1)."""
    text_lower = text.lower()
    
    positive = count_pattern_matches(text_lower, POLITENESS_POSITIVE)
    negative = count_pattern_matches(text_lower, POLITENESS_NEGATIVE)
    
    if positive + negative == 0:
        return 0.0
    
    return (positive - negative) / (positive + negative)


def calculate_specificity(text: str) -> int:
    """Calculate specificity on 1-5 scale."""
    text = text.strip()
    
    if len(text) < 10:
        return 1
    
    score = 2  # Baseline
    
    # Quantifiers add specificity
    if re.search(r'\$[\d,]+|\d+\s*(hours|days|weeks|dollars|percent|%)', text, re.I):
        score += 1
    
    # Requirements add specificity
    if re.search(r'\b(must|need|require|only|max|min|at least|no more)\b', text, re.I):
        score += 1
    
    # Length/detail adds specificity
    if len(text) > 200:
        score += 1
    
    return min(score, 5)


def is_passive_acceptance(text: str) -> bool:
    """Check if text is passive acceptance."""
    text = text.strip().lower()
    if len(text) > 50:
        return False
    return any(re.match(p, text) for p in PASSIVE_PATTERNS)


def find_verbatim_repeats(texts: List[str], min_length: int = 30) -> int:
    """Count substantial text segments repeated verbatim."""
    normalized = [t.strip().lower() for t in texts if len(t) >= min_length]
    
    seen = set()
    repeats = 0
    for text in normalized:
        if text in seen:
            repeats += 1
        seen.add(text)
    
    return repeats


def detect_repair_success(messages: List[dict], repair_indices: List[int]) -> float:
    """
    Estimate repair success rate.
    A repair is successful if the next user message is NOT another repair.
    """
    if not repair_indices:
        return 0.0
    
    successes = 0
    for idx in repair_indices:
        # Find next user message
        next_user_idx = None
        for i in range(idx + 1, len(messages)):
            if messages[i].get('role') == 'user':
                next_user_idx = i
                break
        
        if next_user_idx is None:
            continue
        
        # Check if next user message is also a repair
        next_text = messages[next_user_idx].get('content', '')
        is_another_repair = count_pattern_matches(next_text, REPAIR_MARKERS) > 0
        
        if not is_another_repair:
            successes += 1
    
    return successes / len(repair_indices)


# ============= MAIN EXTRACTION =============

def extract_features(conversation_id: str, messages: List[dict], source: str = "unknown") -> ConversationFeatures:
    """Extract all features from a conversation."""
    
    # Separate user and assistant messages
    user_messages = [m for m in messages if m.get('role') == 'user']
    user_texts = [m.get('content', '') for m in user_messages]
    
    if not user_messages:
        raise ValueError("No user messages found")
    
    # ===== REPAIR =====
    repair_indices = []
    for i, msg in enumerate(messages):
        if msg.get('role') == 'user':
            text = msg.get('content', '')
            if count_pattern_matches(text, REPAIR_MARKERS) > 0:
                repair_indices.append(i)
    
    repair_count = len(repair_indices)
    repair_success_rate = detect_repair_success(messages, repair_indices)
    
    # ===== CONSTRAINTS =====
    constraint_hard = sum(count_pattern_matches(t, CONSTRAINT_HARD) for t in user_texts)
    constraint_soft = sum(count_pattern_matches(t, CONSTRAINT_SOFT) for t in user_texts)
    constraint_goal = sum(count_pattern_matches(t, CONSTRAINT_GOAL) for t in user_texts)
    constraint_count = constraint_hard + constraint_soft + constraint_goal
    
    # ===== POLITENESS =====
    politeness_scores = [calculate_politeness_score(t) for t in user_texts]
    
    n_initial = min(3, len(politeness_scores))
    n_final = min(3, len(politeness_scores))
    
    politeness_initial = sum(politeness_scores[:n_initial]) / n_initial if n_initial > 0 else 0
    politeness_final = sum(politeness_scores[-n_final:]) / n_final if n_final > 0 else 0
    politeness_delta = politeness_final - politeness_initial
    
    # ===== FRUSTRATION =====
    frustration_per_turn = [count_pattern_matches(t, FRUSTRATION_MARKERS) for t in user_texts]
    frustration_score = sum(frustration_per_turn) / len(user_texts) if user_texts else 0
    
    frustration_initial = sum(frustration_per_turn[:n_initial]) / n_initial if n_initial > 0 else 0
    frustration_final = sum(frustration_per_turn[-n_final:]) / n_final if n_final > 0 else 0
    
    if frustration_final > frustration_initial + 0.3:
        frustration_trend = "increasing"
    elif frustration_final < frustration_initial - 0.3:
        frustration_trend = "decreasing"
    else:
        frustration_trend = "stable"
    
    # ===== PASSIVITY =====
    passive_turns = sum(1 for t in user_texts if is_passive_acceptance(t))
    passive_rate = passive_turns / len(user_texts) if user_texts else 0
    
    # ===== SPECIFICITY =====
    specificity_scores = [calculate_specificity(t) for t in user_texts]
    
    specificity_initial = sum(specificity_scores[:n_initial]) / n_initial if n_initial > 0 else 0
    specificity_final = sum(specificity_scores[-n_final:]) / n_final if n_final > 0 else 0
    specificity_delta = specificity_final - specificity_initial
    
    # ===== REPETITION =====
    verbatim_repeats = find_verbatim_repeats(user_texts)
    
    # ===== LENGTH =====
    mean_user_length = sum(len(t) for t in user_texts) / len(user_texts) if user_texts else 0
    
    return ConversationFeatures(
        conversation_id=conversation_id,
        source=source,
        total_turns=len(messages),
        user_turns=len(user_messages),
        repair_count=repair_count,
        repair_success_rate=round(repair_success_rate, 3),
        constraint_count=constraint_count,
        constraint_hard=constraint_hard,
        constraint_soft=constraint_soft,
        constraint_goal=constraint_goal,
        politeness_initial=round(politeness_initial, 3),
        politeness_final=round(politeness_final, 3),
        politeness_delta=round(politeness_delta, 3),
        frustration_score=round(frustration_score, 3),
        frustration_initial=round(frustration_initial, 3),
        frustration_final=round(frustration_final, 3),
        frustration_trend=frustration_trend,
        passive_turns=passive_turns,
        passive_rate=round(passive_rate, 3),
        specificity_initial=round(specificity_initial, 3),
        specificity_final=round(specificity_final, 3),
        specificity_delta=round(specificity_delta, 3),
        verbatim_repeats=verbatim_repeats,
        mean_user_length=round(mean_user_length, 1),
    )


def detect_source(filepath: Path) -> str:
    """Detect source from filename."""
    name = filepath.stem.lower()
    if "arena" in name or "chatbot" in name:
        return "ChatbotArena"
    elif "oasst" in name:
        return "OASST"
    return "WildChat"


def process_file(filepath: Path) -> Optional[ConversationFeatures]:
    """Process a single conversation file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    
    messages = data.get("messages", data.get("conversation", []))
    if len(messages) < 10:
        return None
    
    try:
        return extract_features(
            conversation_id=filepath.stem,
            messages=messages,
            source=detect_source(filepath)
        )
    except ValueError:
        return None


# ============= CLI =============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract features from conversations")
    parser.add_argument("--input", "-i", required=True, help="Input directory")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file")
    parser.add_argument("--sample", "-s", type=int, default=None, help="Sample N files")
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    json_files = list(input_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON files")
    
    if args.sample:
        import random
        json_files = random.sample(json_files, min(args.sample, len(json_files)))
        print(f"Sampled {len(json_files)} files")
    
    results = []
    for i, fp in enumerate(json_files):
        if i % 100 == 0:
            print(f"Processing {i}/{len(json_files)}...")
        
        features = process_file(fp)
        if features:
            results.append(asdict(features))
    
    print(f"\n✅ Extracted features from {len(results)} conversations")
    
    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Saved to {output_path}")
    
    # Quick stats
    print("\n📊 Feature Summary:")
    print(f"  Mean repair_count: {sum(r['repair_count'] for r in results) / len(results):.2f}")
    print(f"  Mean passive_rate: {sum(r['passive_rate'] for r in results) / len(results):.2f}")
    print(f"  Mean specificity_delta: {sum(r['specificity_delta'] for r in results) / len(results):.2f}")
    print(f"  Mean politeness_delta: {sum(r['politeness_delta'] for r in results) / len(results):.2f}")
