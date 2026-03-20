#!/usr/bin/env python3
"""
Inter-Rater Reliability (IRR) Sample Selection and Export

Selects a stratified random sample of conversations for human validation
of LLM-generated role classifications. Exports in a format suitable for
independent coding by 2+ raters.

Usage:
    python scripts/irr_sample.py [--n 100] [--seed 42]

Outputs:
    data/v2_unified/reports/irr_sample.json      - sample metadata
    data/v2_unified/reports/irr_coding_sheet.csv  - blank coding sheet for raters
"""

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONV_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "reports"

HUMAN_ROLES = [
    "information-seeker", "director", "provider",
    "collaborator", "social-expressor", "relational-peer",
]

AI_ROLES = [
    "expert-system", "co-constructor", "advisor",
    "social-facilitator", "relational-peer", "learning-facilitator",
]


def load_conversations():
    convs = {}
    for f in sorted(CONV_DIR.glob("*.json")):
        with open(f) as fh:
            convs[f.stem] = json.load(fh)
    return convs


def get_role_pair(data):
    cls = data.get("classification", {})
    hr = (cls.get("humanRole") or {}).get("distribution", {})
    ar = (cls.get("aiRole") or {}).get("distribution", {})
    if not hr or not ar:
        return None, None
    return max(hr, key=hr.get), max(ar, key=ar.get)


def stratified_sample(convs, n_total, seed):
    """Select stratified sample ensuring representation of rare roles."""
    random.seed(seed)

    by_human_role = {}
    for cid, data in convs.items():
        h, a = get_role_pair(data)
        if h is None:
            continue
        by_human_role.setdefault(h, []).append(cid)

    # Allocation: minimum 5 per role (if available), rest proportional
    min_per_role = 5
    selected = set()

    # First pass: guarantee minimum representation
    for role, cids in by_human_role.items():
        take = min(min_per_role, len(cids))
        chosen = random.sample(cids, take)
        selected.update(chosen)

    # Second pass: fill remaining quota proportionally
    remaining = n_total - len(selected)
    if remaining > 0:
        pool = [cid for cid in convs if cid not in selected and get_role_pair(convs[cid])[0] is not None]
        if len(pool) <= remaining:
            selected.update(pool)
        else:
            selected.update(random.sample(pool, remaining))

    return sorted(selected)


def export_sample(convs, sample_ids, seed):
    """Export sample metadata and blank coding sheet."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build sample metadata
    records = []
    for cid in sample_ids:
        data = convs[cid]
        h, a = get_role_pair(data)
        messages = data.get("messages", [])
        records.append({
            "conv_id": cid,
            "source": data.get("source", "unknown"),
            "n_messages": len(messages),
            "llm_human_role": h,
            "llm_ai_role": a,
            "first_human_msg": next(
                (m.get("content", "")[:200] for m in messages if m.get("role") == "human"),
                "",
            ),
        })

    # Role distribution in sample
    sample_human = Counter(r["llm_human_role"] for r in records)
    sample_ai = Counter(r["llm_ai_role"] for r in records)

    meta = {
        "n_sample": len(records),
        "seed": seed,
        "sample_human_role_distribution": dict(sample_human.most_common()),
        "sample_ai_role_distribution": dict(sample_ai.most_common()),
        "conversations": records,
    }

    meta_path = OUTPUT_DIR / "irr_sample.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Sample metadata: {meta_path}")

    # Export coding sheet CSV
    csv_path = OUTPUT_DIR / "irr_coding_sheet.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "conv_id", "source", "n_messages", "first_human_msg",
            "rater_human_role", "rater_ai_role",
            "rater_confidence_human", "rater_confidence_ai",
            "rater_notes",
        ])
        for r in records:
            writer.writerow([
                r["conv_id"],
                r["source"],
                r["n_messages"],
                r["first_human_msg"],
                "",  # rater_human_role (to fill)
                "",  # rater_ai_role (to fill)
                "",  # rater_confidence_human (1-5)
                "",  # rater_confidence_ai (1-5)
                "",  # rater_notes
            ])
    print(f"Coding sheet: {csv_path}")

    # Print summary
    print(f"\nSample: N={len(records)}")
    print(f"  Human role distribution: {dict(sample_human.most_common())}")
    print(f"  AI role distribution: {dict(sample_ai.most_common())}")
    print(f"\nValid human roles for coding: {HUMAN_ROLES}")
    print(f"Valid AI roles for coding: {AI_ROLES}")


def main():
    parser = argparse.ArgumentParser(description="Generate IRR coding sample")
    parser.add_argument("--n", type=int, default=100, help="Sample size (default: 100)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    convs = load_conversations()
    print(f"Loaded {len(convs)} conversations")

    sample_ids = stratified_sample(convs, args.n, args.seed)
    export_sample(convs, sample_ids, args.seed)


if __name__ == "__main__":
    main()
