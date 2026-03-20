#!/usr/bin/env python3
"""
Download PISCES subset from ShenLab/MentalChat16K.
"""

import json
import hashlib
from pathlib import Path
from datasets import load_dataset

RAW_DIR = Path("data/pisces/raw")
OUT_ENRICHED = Path("data/pisces/pisces_enriched.json")

def main():
    print(f"Downloading ShenLab/MentalChat16K...")
    # Streaming to inspect first
    ds = load_dataset("ShenLab/MentalChat16K", split="train")
    print(f"Total rows: {len(ds)}")
    
    # Inspect columns
    sample = ds[0]
    print(f"Columns: {list(sample.keys())}")
    
    # Check for source column
    if "source" in sample:
        source_col = "source"
    elif "dataset" in sample:
        source_col = "dataset"
    else:
        print("Warning: No 'source' or 'dataset' column found. Checking first 5 rows for clues:")
        for i in range(5):
            print(ds[i])
        return

    # Filter for PISCES
    print(f"Filtering for PISCES in column '{source_col}'...")
    pisces_rows = [row for row in ds if "pisces" in str(row.get(source_col, "")).lower()]
    print(f"Found {len(pisces_rows)} PISCES rows.")

    if not pisces_rows:
        print("No PISCES rows found. Exiting.")
        return

    # Group by Conversation ID (if available) or assume each row is a full conversation?
    # MentalChat16K description says "multi-turn", but sometimes rows are turns.
    # Let's inspect a sample PISCES row structure.
    print("Sample PISCES row:")
    print(pisces_rows[0])

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    enriched = []

    for i, row in enumerate(pisces_rows):
        # Infer conversation structure
        # If 'history' or 'messages' column exists, it's already multi-turn.
        # If not, we might need to reconstruct.
        
        conv_id = f"pisces_{i:04d}"
        messages = []
        
        if "history" in row:
             # Assuming list of [user, assistant] or similar
             hist = row["history"]
             if isinstance(hist, list):
                 for turn in hist:
                     if isinstance(turn, dict) and "role" in turn and "content" in turn:
                         messages.append(turn)
                     elif isinstance(turn, list) and len(turn) == 2:
                         messages.append({"role": "user", "content": turn[0]})
                         messages.append({"role": "assistant", "content": turn[1]})
        elif "conversation" in row:
             # ShareGPT format?
             messages = row["conversation"]
        elif "instruction" in row and "output" in row:
             # Single turn or instructions
             messages.append({"role": "user", "content": row["instruction"]})
             messages.append({"role": "assistant", "content": row["output"]})
             # Check if input exists
             if row.get("input"):
                 messages[0]["content"] += "\nInput: " + row["input"]
        
        if not messages:
            print(f"Skipping row {i}: Could not parse messages.")
            continue

        raw = {
            "id": conv_id,
            "messages": messages
        }
        
        raw_path = RAW_DIR / f"{conv_id}.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)

        enriched.append({
            "id": conv_id,
            "source": "PISCES",
            "domain": "mental_health",
            "total_turns": len(messages),
            "file_path": str(raw_path.resolve()),
            "taxonomy": {
                 "architecture": "Generation", # Default, update if we find better
                 "constraint_hardness": "Soft"
            }
        })

    with open(OUT_ENRICHED, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Processed {len(enriched)} conversations.")
    print(f"Raw data: {RAW_DIR}")
    print(f"Enriched Metadata: {OUT_ENRICHED}")

if __name__ == "__main__":
    main()
