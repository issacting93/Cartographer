#!/usr/bin/env python3
"""
fetch_wildchat_only.py - Fetch long conversations from WildChat only
"""

import json
from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm

OUTPUT_DIR = Path("/Users/zac/Downloads/Cartography/public/output")
TARGET = 150  # Fetch 150 more to exceed 562 target

CONSTRAINT_KEYWORDS = [
    'must', 'need', 'require', 'should', 'only', 'no more', 'at least',
    'maximum', 'minimum', 'budget', 'deadline', 'constraint', 'limit',
    'goal', 'objective', 'want to', 'trying to', 'looking for',
    'prefer', 'ideally', "don't want", 'avoid', 'exclude',
]


def has_task_content(conversation: list) -> bool:
    user_text = ' '.join(
        m.get('content', '') for m in conversation
        if m.get('role') == 'user'
    ).lower()
    matches = sum(1 for kw in CONSTRAINT_KEYWORDS if kw in user_text)
    return matches >= 2


def main():
    print(f"Fetching {TARGET} long conversations from WildChat...")
    print(f"Output: {OUTPUT_DIR}")

    dataset = load_dataset("allenai/WildChat-1M", split="train", streaming=True)

    results = []
    scanned = 0
    saved = 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for item in tqdm(dataset, desc="Scanning"):
        scanned += 1

        conversation = item.get("conversation", [])

        if len(conversation) < 16:
            continue

        if not has_task_content(conversation):
            continue

        conv_hash = item.get("conversation_hash", str(scanned))[:16]
        conv_id = f"wildchat_new_{conv_hash}"
        filepath = OUTPUT_DIR / f"{conv_id}.json"

        if filepath.exists():
            continue

        entry = {
            "id": conv_id,
            "source": "WildChat",
            "messages": [
                {"role": m.get("role"), "content": m.get("content", "")}
                for m in conversation
                if m.get("role") in ["user", "assistant"]
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(entry, f, indent=2)

        saved += 1
        results.append(conv_id)

        if saved >= TARGET:
            break

        if scanned >= 100000:
            break

    print(f"\nScanned: {scanned:,}")
    print(f"Saved: {saved} new files")


if __name__ == "__main__":
    main()
