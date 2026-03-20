#!/usr/bin/env python3
"""
Unified Corpus Builder (v2)
============================
Produces a clean, deduplicated, English-only corpus from raw conversation JSON files.
Unlike v1, this does NOT require pre-existing classification or PAD data.

Pipeline:
  1. Load all JSON files from data/conversations_raw/
  2. SHA-256 deduplication (normalize: lowercase, whitespace collapse, punctuation strip)
  3. Language filter (English-only via langdetect)
  4. Minimum length: >= 4 turns
  5. Copy canonical files to data/v2_unified/conversations/

Outputs:
  data/v2_unified/conversations/    - Canonical conversation files
  data/v2_unified/manifests/        - validated_manifest.json, excluded_manifest.json,
                                      dedupe_manifest.json, corpus_stats.json

Usage:
  python3 scripts/build_corpus.py [--min-turns N]
"""

import json
import os
import sys
import hashlib
import re
import shutil
import argparse
from pathlib import Path
from collections import defaultdict, Counter

try:
    from langdetect import detect, LangDetectException
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False
    print("WARNING: langdetect not installed. Language filtering disabled.")
    print("  Install with: pip install langdetect")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "conversations_raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
MANIFEST_DIR = PROJECT_ROOT / "data" / "v2_unified" / "manifests"

MIN_TURNS = 4  # default


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize text for dedup hashing."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([!?.])\1{2,}', r'\1', text)
    return text.strip()


def content_hash(messages: list) -> str:
    """SHA-256 hash of role sequence + normalized message content."""
    parts = []
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = normalize_text(msg.get('content', ''))
        parts.append(f"{role}:{content}")
    combined = '|'.join(parts)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def detect_language(messages: list) -> str:
    """Detect language from first few user messages."""
    if not HAS_LANGDETECT:
        return 'en'

    combined = ' '.join(
        msg.get('content', '')[:300]
        for msg in messages[:3]
        if msg.get('role') == 'user'
    )
    if len(combined.strip()) < 20:
        combined = ' '.join(msg.get('content', '')[:200] for msg in messages[:4])

    try:
        return detect(combined)
    except LangDetectException:
        return 'unknown'


def infer_source(filepath: str, data: dict) -> str:
    """Infer dataset source from filepath, filename, and data."""
    # Check data first
    source = data.get('source', '')
    if source:
        source_lower = source.lower()
        if 'wildchat' in source_lower:
            return 'wildchat'
        if 'oasst' in source_lower or 'openassistant' in source_lower:
            return 'oasst'
        if 'chatbot' in source_lower or 'arena' in source_lower:
            return 'chatbot_arena'

    basename = os.path.basename(filepath)
    if 'wildchat' in basename:
        return 'wildchat'
    if basename.startswith('oasst'):
        return 'oasst'
    if basename.startswith('cornell') or basename.startswith('kaggle'):
        return 'other'
    return 'chatbot_arena'


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_load(raw_dir: Path) -> tuple:
    """Load all JSON files from raw directory."""
    loaded = {}
    errors = []

    json_files = sorted(raw_dir.glob('*.json'))
    for fpath in json_files:
        fname = fpath.name
        if fname == 'all-conversations.json':
            continue  # Skip aggregate file

        base_id = fname.replace('.json', '')
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                errors.append((base_id, 'not_dict'))
                continue
            data['_source_path'] = str(fpath)
            data['_source'] = infer_source(str(fpath), data)
            loaded[base_id] = data
        except (json.JSONDecodeError, UnicodeDecodeError):
            errors.append((base_id, 'parse_error'))

    return loaded, errors


def stage_validate(loaded: dict, min_turns: int) -> tuple:
    """Validate conversations: require minimum turns and valid messages."""
    validated = {}
    excluded = {}

    for conv_id, data in loaded.items():
        messages = data.get('messages', [])
        if not messages:
            excluded[conv_id] = 'no_messages'
            continue

        # Filter to only user/assistant messages
        valid_msgs = [m for m in messages if m.get('role') in ('user', 'assistant')]
        if len(valid_msgs) < min_turns:
            excluded[conv_id] = f'too_short_{len(valid_msgs)}_turns'
            continue

        # Check messages have content
        if not all(m.get('content', '').strip() for m in valid_msgs):
            excluded[conv_id] = 'empty_messages'
            continue

        validated[conv_id] = data

    return validated, excluded


def stage_deduplicate(validated: dict) -> tuple:
    """Deduplicate by content hash."""
    hash_groups = defaultdict(list)

    for conv_id, data in validated.items():
        messages = data.get('messages', [])
        h = content_hash(messages)
        hash_groups[h].append(conv_id)

    deduped = {}
    dedupe_manifest = {}

    for h, conv_ids in hash_groups.items():
        if len(conv_ids) == 1:
            canonical = conv_ids[0]
        else:
            # Prefer files with classification, then more messages
            def score(cid):
                data = validated[cid]
                s = 0
                if data.get('classification'):
                    s += 1000
                if data.get('messages', [{}])[0].get('pad'):
                    s += 100
                s += len(data.get('messages', []))
                return s

            ranked = sorted(conv_ids, key=score, reverse=True)
            canonical = ranked[0]
            dedupe_manifest[h] = {
                'canonical': canonical,
                'duplicates': ranked[1:],
                'count': len(conv_ids),
            }

        deduped[canonical] = validated[canonical]

    return deduped, dedupe_manifest


def stage_language_filter(deduped: dict) -> tuple:
    """Filter to English-only conversations."""
    english = {}
    non_english = {}

    for conv_id, data in deduped.items():
        # If metadata says English, trust it
        metadata = data.get('metadata', {})
        meta_lang = metadata.get('language', '').lower()
        if meta_lang in ('en', 'english'):
            english[conv_id] = data
            continue

        messages = data.get('messages', [])
        lang = detect_language(messages)
        if lang == 'en':
            english[conv_id] = data
        else:
            non_english[conv_id] = lang

    return english, non_english


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def build_corpus(min_turns: int = MIN_TURNS):
    """Run the full corpus build pipeline."""
    print("=" * 60)
    print("UNIFIED CORPUS BUILDER (v2)")
    print("=" * 60)

    # Stage 1: Load
    print(f"\n[1/4] Loading raw files from {RAW_DIR}...")
    loaded, load_errors = stage_load(RAW_DIR)
    print(f"  Loaded: {len(loaded)} conversations")
    print(f"  Errors: {len(load_errors)} files")

    # Source breakdown
    source_counts_raw = Counter(data.get('_source', 'unknown') for data in loaded.values())
    print(f"  Sources: {dict(source_counts_raw.most_common())}")

    # Stage 2: Validate
    print(f"\n[2/4] Validating (min {min_turns} turns)...")
    validated, excluded = stage_validate(loaded, min_turns)
    print(f"  Validated: {len(validated)} conversations")
    print(f"  Excluded: {len(excluded)} conversations")
    reason_counts = Counter(excluded.values())
    for reason, count in reason_counts.most_common(5):
        print(f"    - {reason}: {count}")

    # Stage 3: Deduplicate
    print("\n[3/4] Deduplicating...")
    deduped, dedupe_manifest = stage_deduplicate(validated)
    n_dupes = len(validated) - len(deduped)
    print(f"  Unique: {len(deduped)} conversations")
    print(f"  Duplicates removed: {n_dupes}")

    # Stage 4: Language filter
    print("\n[4/4] Language filtering...")
    canonical, non_english = stage_language_filter(deduped)
    print(f"  English: {len(canonical)} conversations")
    print(f"  Non-English: {len(non_english)} conversations")
    if non_english:
        lang_counts = Counter(non_english.values())
        for lang, count in lang_counts.most_common(5):
            print(f"    - {lang}: {count}")

    # ---------------------------------------------------------------------------
    # Write outputs
    # ---------------------------------------------------------------------------

    print(f"\n{'=' * 60}")
    print("WRITING OUTPUTS")
    print("=" * 60)

    # Copy canonical conversations
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Clear existing
    for f in OUTPUT_DIR.iterdir():
        if f.is_file():
            f.unlink()

    for conv_id, data in canonical.items():
        # Strip internal metadata before saving
        clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
        # Ensure id is set
        if 'id' not in clean_data:
            clean_data['id'] = conv_id
        # Ensure source is set
        if 'source' not in clean_data:
            clean_data['source'] = data.get('_source', 'unknown')

        dst = OUTPUT_DIR / f"{conv_id}.json"
        with open(dst, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)

    print(f"  Canonical corpus: {len(canonical)} files in {OUTPUT_DIR}")

    # Write manifests
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    # Validated manifest
    validated_manifest = {
        conv_id: {
            'source': data.get('_source', 'unknown'),
            'n_messages': len(data.get('messages', [])),
        }
        for conv_id, data in validated.items()
    }
    with open(MANIFEST_DIR / 'validated_manifest.json', 'w') as f:
        json.dump(validated_manifest, f, indent=2)

    # Excluded manifest
    excluded_manifest = {conv_id: {'reason': reason} for conv_id, reason in excluded.items()}
    with open(MANIFEST_DIR / 'excluded_manifest.json', 'w') as f:
        json.dump(excluded_manifest, f, indent=2)

    # Dedupe manifest
    with open(MANIFEST_DIR / 'dedupe_manifest.json', 'w') as f:
        json.dump(dedupe_manifest, f, indent=2)

    # Non-English manifest
    with open(MANIFEST_DIR / 'non_english_manifest.json', 'w') as f:
        json.dump(non_english, f, indent=2)

    # Corpus stats
    source_counts = Counter(data.get('_source', 'unknown') for data in canonical.values())
    msg_counts = [len(data.get('messages', [])) for data in canonical.values()]
    avg_msgs = sum(msg_counts) / len(msg_counts) if msg_counts else 0

    # Check what has classification / PAD already
    n_classified = sum(1 for data in canonical.values() if data.get('classification'))
    n_pad = sum(1 for data in canonical.values()
                if data.get('messages', [{}])[0].get('pad'))

    corpus_stats = {
        'total_canonical': len(canonical),
        'total_loaded': len(loaded),
        'total_validated_pre_dedup': len(validated),
        'duplicates_removed': n_dupes,
        'non_english_removed': len(non_english),
        'has_classification': n_classified,
        'has_pad': n_pad,
        'needs_classification': len(canonical) - n_classified,
        'needs_pad': len(canonical) - n_pad,
        'source_breakdown': dict(source_counts.most_common()),
        'message_stats': {
            'mean': round(avg_msgs, 1),
            'median': sorted(msg_counts)[len(msg_counts) // 2] if msg_counts else 0,
            'min': min(msg_counts) if msg_counts else 0,
            'max': max(msg_counts) if msg_counts else 0,
            'total': sum(msg_counts),
        },
        'length_distribution': {
            '4-5 messages': sum(1 for m in msg_counts if 4 <= m <= 5),
            '6-9 messages': sum(1 for m in msg_counts if 6 <= m <= 9),
            '10-19 messages': sum(1 for m in msg_counts if 10 <= m <= 19),
            '20+ messages': sum(1 for m in msg_counts if m >= 20),
        },
    }
    with open(MANIFEST_DIR / 'corpus_stats.json', 'w') as f:
        json.dump(corpus_stats, f, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print("CORPUS SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Canonical corpus: {len(canonical)} conversations")
    print(f"  Sources:")
    for source, count in source_counts.most_common():
        print(f"    - {source}: {count} ({count/len(canonical)*100:.1f}%)")
    print(f"  Messages: mean={avg_msgs:.1f}, median={corpus_stats['message_stats']['median']}")
    print(f"  Length distribution:")
    for bucket, count in corpus_stats['length_distribution'].items():
        pct = count / len(canonical) * 100 if len(canonical) > 0 else 0
        print(f"    - {bucket}: {count} ({pct:.1f}%)")
    print(f"\n  Pre-existing enrichment:")
    print(f"    - Has classification: {n_classified} ({n_classified/len(canonical)*100:.1f}%)")
    print(f"    - Has PAD: {n_pad} ({n_pad/len(canonical)*100:.1f}%)")
    print(f"    - Needs classification: {len(canonical) - n_classified}")
    print(f"    - Needs PAD: {len(canonical) - n_pad}")

    return canonical


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Build unified canonical corpus")
    parser.add_argument('--min-turns', type=int, default=MIN_TURNS,
                        help=f"Minimum number of turns (default: {MIN_TURNS})")
    args = parser.parse_args()
    build_corpus(min_turns=args.min_turns)
