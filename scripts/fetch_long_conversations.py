#!/usr/bin/env python3
"""
fetch_long_conversations.py - Fetch long, constraint-rich conversations

Targets conversations with:
- 10+ user turns (20+ total messages)
- Task-oriented content with explicit constraints
"""

import json
import re
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm

OUTPUT_DIR = Path("/Users/zac/Downloads/Cartography/public/output")

# How many to fetch
TARGET_WILDCHAT = 300
TARGET_LMSYS = 300

# Constraint patterns (more lenient to get more data)
CONSTRAINT_KEYWORDS = [
    'must', 'need', 'require', 'should', 'only', 'no more', 'at least',
    'maximum', 'minimum', 'budget', 'deadline', 'constraint', 'limit',
    'goal', 'objective', 'want to', 'trying to', 'looking for',
    'prefer', 'ideally', "don't want", 'avoid', 'exclude',
]


def has_task_content(conversation: list) -> bool:
    """Check if conversation has task-oriented content."""
    user_text = ' '.join(
        m.get('content', '') for m in conversation
        if m.get('role') == 'user'
    ).lower()

    # Count keyword matches
    matches = sum(1 for kw in CONSTRAINT_KEYWORDS if kw in user_text)
    return matches >= 2


def format_conversation(conv_id: str, messages: list, source: str) -> dict:
    """Convert to our format."""
    return {
        "id": conv_id,
        "source": source,
        "messages": [
            {"role": m.get("role"), "content": m.get("content", "")}
            for m in messages
            if m.get("role") in ["user", "assistant"]
        ]
    }


def fetch_wildchat():
    """Fetch long conversations from WildChat."""
    print("\n" + "=" * 60)
    print("Fetching from WildChat-1M (streaming)...")
    print("=" * 60)

    dataset = load_dataset("allenai/WildChat-1M", split="train", streaming=True)

    results = []
    scanned = 0
    max_scan = 50000  # Don't scan forever

    pbar = tqdm(total=TARGET_WILDCHAT, desc="Found")

    for item in dataset:
        scanned += 1

        conversation = item.get("conversation", [])

        # Skip short conversations
        if len(conversation) < 16:  # 8 turns minimum
            continue

        # Skip if no task content
        if not has_task_content(conversation):
            continue

        # Create entry
        conv_hash = item.get("conversation_hash", str(scanned))[:16]
        conv_id = f"wildchat_new_{conv_hash}"

        # Skip if already exists
        if (OUTPUT_DIR / f"{conv_id}.json").exists():
            continue

        entry = format_conversation(conv_id, conversation, "WildChat")
        results.append(entry)
        pbar.update(1)

        if len(results) >= TARGET_WILDCHAT:
            break

        if scanned >= max_scan:
            print(f"\nReached scan limit ({max_scan})")
            break

    pbar.close()
    print(f"Scanned {scanned:,} conversations, found {len(results)} qualifying")
    return results


def fetch_lmsys():
    """Fetch long conversations from LMSYS-Chat-1M."""
    print("\n" + "=" * 60)
    print("Fetching from LMSYS-Chat-1M (streaming)...")
    print("=" * 60)

    dataset = load_dataset("lmsys/lmsys-chat-1m", split="train", streaming=True)

    results = []
    scanned = 0
    max_scan = 50000

    pbar = tqdm(total=TARGET_LMSYS, desc="Found")

    for item in dataset:
        scanned += 1

        conversation = item.get("conversation", [])

        # Skip short conversations
        if len(conversation) < 16:
            continue

        # Skip if no task content
        if not has_task_content(conversation):
            continue

        # Create entry
        conv_id = f"lmsys_new_{item.get('conversation_id', scanned)}"

        # Skip if already exists
        if (OUTPUT_DIR / f"{conv_id}.json").exists():
            continue

        entry = format_conversation(conv_id, conversation, "ChatbotArena")
        results.append(entry)
        pbar.update(1)

        if len(results) >= TARGET_LMSYS:
            break

        if scanned >= max_scan:
            print(f"\nReached scan limit ({max_scan})")
            break

    pbar.close()
    print(f"Scanned {scanned:,} conversations, found {len(results)} qualifying")
    return results


def save_results(conversations: list):
    """Save conversations to individual files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for conv in conversations:
        filepath = OUTPUT_DIR / f"{conv['id']}.json"
        with open(filepath, 'w') as f:
            json.dump(conv, f, indent=2)

    print(f"\nSaved {len(conversations)} new conversations to {OUTPUT_DIR}")


def main():
    print("=" * 60)
    print("Fetching long conversations for CUI 2026 study")
    print("Target: 500+ new conversations with 16+ messages")
    print("=" * 60)

    # Fetch from both sources
    wildchat_results = fetch_wildchat()
    lmsys_results = fetch_lmsys()

    # Combine and save
    all_results = wildchat_results + lmsys_results
    save_results(all_results)

    print("\n" + "=" * 60)
    print(f"COMPLETE: {len(all_results)} new conversations fetched")
    print("=" * 60)


if __name__ == "__main__":
    main()
