#!/usr/bin/env python3
"""
Download 100 conversations from Amod/mental_health_counseling_conversations
and convert them into the Atlas pipeline input format.

Produces:
  1. data/mental_health/raw/{id}.json  — individual conversation files
  2. data/mental_health/mental_health_enriched.json — enriched metadata for pipeline

Usage:
  pip install datasets
  python scripts/download_mental_health.py
"""

import json
import hashlib
from pathlib import Path

N = 100
RAW_DIR = Path("data/mental_health/raw")
OUT_ENRICHED = Path("data/mental_health/mental_health_enriched.json")

def main():
    from datasets import load_dataset

    print(f"Downloading Amod/mental_health_counseling_conversations...")
    ds = load_dataset("Amod/mental_health_counseling_conversations", split="train")
    print(f"Total rows in dataset: {len(ds)}")

    # Take first N rows
    subset = ds.select(range(min(N, len(ds))))

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    enriched = []

    for i, row in enumerate(subset):
        context = row["Context"].strip()
        response = row["Response"].strip()

        # Generate a stable ID from content hash
        content_hash = hashlib.md5(context.encode()).hexdigest()[:12]
        conv_id = f"mentalhealth_{i:04d}_{content_hash}"

        # --- Raw conversation file (pipeline input format) ---
        raw = {
            "id": conv_id,
            "messages": [
                {"role": "user", "content": context},
                {"role": "assistant", "content": response},
            ],
        }
        raw_path = RAW_DIR / f"{conv_id}.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)

        # --- Enriched metadata entry ---
        enriched.append({
            "id": conv_id,
            "source": "MentalHealthCounseling",
            "domain": "mental_health",
            "total_turns": 2,
            "classification": {
                "task_goal": context[:200],
                "primary_constraints": [],  # single-turn Q&A has no explicit constraints
                "stability_class": "No Constraints",
                "confidence": 0.5,
                "violation_count": 0,
                "user_response": "N/A",
                "reasoning": "Single-turn counseling Q&A — no constraint lifecycle to track.",
                "evidence": {
                    "constraint_turns": [],
                    "violation_turns": [],
                    "repair_turns": [],
                },
            },
            "file_path": str(raw_path.resolve()),
            "taxonomy": {
                "architecture": "Generation",
                "constraint_hardness": "Flexible",
            },
        })

    with open(OUT_ENRICHED, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\nDone!")
    print(f"  Raw conversations: {RAW_DIR}/ ({len(enriched)} files)")
    print(f"  Enriched metadata: {OUT_ENRICHED}")
    print(f"\nNext step — run the pipeline:")
    print(f"  python -m atlas.run_pipeline \\")
    print(f"    --enriched {OUT_ENRICHED} \\")
    print(f"    --source-dir {RAW_DIR} \\")
    print(f"    --output-dir data/mental_health/graphs \\")
    print(f"    --no-llm")


if __name__ == "__main__":
    main()
