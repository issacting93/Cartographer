#!/usr/bin/env python3
"""
fetch_conversations.py - Download and filter conversations for N=562 analysis

Filters for:
- 10+ turns (20+ messages)
- Contains explicit constraints (goals, requirements, preferences)
- Excludes: creative writing, one-shot Q&A, code-only
"""

import json
import re
import os
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm

OUTPUT_DIR = Path("/Users/zac/Downloads/Cartography/public/output")
TARGET_COUNT = 600  # Aim for slightly more than 562

# Constraint detection patterns
CONSTRAINT_PATTERNS = [
    # Explicit constraints
    r'\b(must|need to|have to|require|should|only|no more than|at least|maximum|minimum)\b',
    r'\b(constraint|requirement|condition|rule|limit|budget|deadline)\b',
    # Goals
    r'\b(goal|objective|want to|trying to|aim|target|looking for|searching for)\b',
    # Preferences
    r'\b(prefer|rather|ideally|if possible|would like|hope)\b',
    # Negations (constraints often expressed as "no X", "don't want Y")
    r'\b(no |don\'t|do not|cannot|can\'t|won\'t|will not|never|avoid)\b',
]

# Exclusion patterns (creative writing, roleplay, etc.)
EXCLUDE_PATTERNS = [
    r'\b(write a story|write a poem|roleplay|pretend you are|act as if)\b',
    r'\b(once upon a time|chapter \d+)\b',
]

def has_constraints(text: str) -> bool:
    """Check if text contains constraint-like language."""
    text_lower = text.lower()

    # Check exclusions first
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, text_lower):
            return False

    # Count constraint patterns
    matches = 0
    for pattern in CONSTRAINT_PATTERNS:
        if re.search(pattern, text_lower):
            matches += 1

    return matches >= 2  # Require at least 2 different constraint types


def is_task_oriented(conversation: list) -> bool:
    """Check if conversation is task-oriented (not just Q&A or creative)."""
    if len(conversation) < 2:
        return False

    # Check first few user messages for task indicators
    user_messages = [m['content'] for m in conversation if m.get('role') == 'user'][:3]
    combined = ' '.join(user_messages)

    return has_constraints(combined)


def conversation_to_format(conv_id: str, messages: list, source: str) -> dict:
    """Convert to our annotation format."""
    return {
        "id": conv_id,
        "source": source,
        "messages": [
            {
                "role": m.get("role", "user"),
                "content": m.get("content", "")
            }
            for m in messages
            if m.get("role") in ["user", "assistant"]
        ]
    }


def fetch_wildchat(limit: int = 300) -> list:
    """Fetch from WildChat-1M dataset."""
    print("Loading WildChat-1M...")
    dataset = load_dataset("allenai/WildChat-1M", split="train", streaming=True)

    results = []
    checked = 0

    for item in tqdm(dataset, desc="Scanning WildChat", total=limit * 10):
        checked += 1

        # Get conversation
        conversation = item.get("conversation", [])

        # Filter: 10+ turns (20+ messages)
        if len(conversation) < 20:
            continue

        # Filter: task-oriented with constraints
        if not is_task_oriented(conversation):
            continue

        # Create entry
        conv_id = f"wildchat_{item.get('conversation_hash', checked)[:12]}"
        entry = conversation_to_format(conv_id, conversation, "WildChat")
        results.append(entry)

        if len(results) >= limit:
            break

        if checked > limit * 50:  # Don't scan forever
            break

    print(f"Found {len(results)} qualifying WildChat conversations")
    return results


def fetch_lmsys(limit: int = 300) -> list:
    """Fetch from LMSYS-Chat-1M dataset."""
    print("Loading LMSYS-Chat-1M...")
    dataset = load_dataset("lmsys/lmsys-chat-1m", split="train", streaming=True)

    results = []
    checked = 0

    for item in tqdm(dataset, desc="Scanning LMSYS", total=limit * 10):
        checked += 1

        # Get conversation
        conversation = item.get("conversation", [])

        # Filter: 10+ turns (20+ messages)
        if len(conversation) < 20:
            continue

        # Filter: task-oriented with constraints
        if not is_task_oriented(conversation):
            continue

        # Create entry
        conv_id = f"lmsys_{item.get('conversation_id', checked)}"
        entry = conversation_to_format(conv_id, conversation, "ChatbotArena")
        results.append(entry)

        if len(results) >= limit:
            break

        if checked > limit * 50:
            break

    print(f"Found {len(results)} qualifying LMSYS conversations")
    return results


def save_conversations(conversations: list, prefix: str):
    """Save conversations to individual JSON files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, conv in enumerate(conversations):
        filename = OUTPUT_DIR / f"{prefix}_{i:04d}.json"
        with open(filename, 'w') as f:
            json.dump(conv, f, indent=2)

    print(f"Saved {len(conversations)} files with prefix {prefix}")


def main():
    print("=" * 60)
    print("Fetching conversations for CUI 2026 N=562 analysis")
    print("=" * 60)

    # Count existing files
    existing = list(OUTPUT_DIR.glob("*.json"))
    existing_long = [f for f in existing if count_messages(f) >= 20]
    print(f"Existing files: {len(existing)} total, {len(existing_long)} with 20+ messages")

    needed = max(0, TARGET_COUNT - len(existing_long))
    print(f"Need {needed} more conversations")

    if needed == 0:
        print("Already have enough data!")
        return

    # Fetch from sources
    wildchat_convs = fetch_wildchat(limit=needed // 2 + 50)
    lmsys_convs = fetch_lmsys(limit=needed // 2 + 50)

    # Save
    save_conversations(wildchat_convs, "wildchat_long")
    save_conversations(lmsys_convs, "lmsys_long")

    print("=" * 60)
    print(f"Total new conversations: {len(wildchat_convs) + len(lmsys_convs)}")
    print("=" * 60)


def count_messages(filepath: Path) -> int:
    """Count messages in a JSON file."""
    try:
        with open(filepath) as f:
            data = json.load(f)
            return len(data.get("messages", []))
    except:
        return 0


if __name__ == "__main__":
    main()
