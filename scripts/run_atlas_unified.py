#!/usr/bin/env python3
"""
Run Atlas Pipeline on Unified Corpus
======================================
Wrapper that prepares unified corpus conversations for the atlas pipeline.
Creates the enriched input format expected by run_pipeline.py, then runs it.

The atlas pipeline requires task-classified input (primary_constraints, evidence,
task_goal). This script runs the task-first classifier on conversations that
don't yet have this data, then feeds everything to the pipeline.

Usage:
    # Full run
    python3 scripts/run_atlas_unified.py [--sample N] [--no-llm] [--force]

    # Dry run (just prepare enriched data, don't run pipeline)
    python3 scripts/run_atlas_unified.py --dry-run
"""

import json
import sys
import os
import asyncio
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONVERSATIONS_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "atlas"
ENRICHED_FILE = OUTPUT_DIR / "all_task_enriched.json"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


def prepare_enriched_data(conversations_dir: Path, output_file: Path):
    """
    Prepare enriched data from unified corpus conversations.

    For conversations that already have task classification (from v2 pipeline),
    use it directly. For others, create minimal entries that the pipeline
    can process in deterministic mode.
    """
    entries = []

    for fpath in sorted(conversations_dir.glob('*.json')):
        with open(fpath) as f:
            data = json.load(f)

        conv_id = data.get('id', fpath.stem)
        messages = data.get('messages', [])
        if not messages:
            continue

        # Check for existing task classification
        cls = data.get('task_classification', data.get('classification', {}))

        entry = {
            'id': conv_id,
            'file_path': str(fpath),
            'classification': {
                'primary_constraints': cls.get('primary_constraints', []),
                'evidence': cls.get('evidence', {}),
                'task_goal': cls.get('task_goal', cls.get('conversationPurpose', {}).get('category', '')),
                'stability_class': cls.get('stability_class') or None,
            },
            'taxonomy': {
                'architecture': cls.get('architecture', ''),
                'constraint_hardness': cls.get('constraint_hardness', ''),
            },
        }

        entries.append(entry)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(entries, f, indent=2)

    return entries


def main():
    parser = argparse.ArgumentParser(description="Run Atlas pipeline on unified corpus")
    parser.add_argument('--sample', type=int, help="Process only N conversations")
    parser.add_argument('--no-llm', action='store_true', help="Deterministic-only mode")
    parser.add_argument('--force', action='store_true', help="Bypass cache")
    parser.add_argument('--model', default='gpt-4o-mini', help="LLM model")
    parser.add_argument('--concurrent', type=int, default=10, help="Max concurrent requests")
    parser.add_argument('--dry-run', action='store_true', help="Just prepare data, don't run pipeline")
    args = parser.parse_args()

    print("=" * 60)
    print("ATLAS PIPELINE - UNIFIED CORPUS")
    print("=" * 60)

    # Prepare enriched data
    print(f"\nPreparing enriched data from {CONVERSATIONS_DIR}...")
    entries = prepare_enriched_data(CONVERSATIONS_DIR, ENRICHED_FILE)
    print(f"  Prepared {len(entries)} entries")
    print(f"  Saved to {ENRICHED_FILE}")

    if args.dry_run:
        print("\nDRY RUN - pipeline not executed")
        return

    # Build pipeline args
    pipeline_args = [
        sys.executable, '-m', 'atlas.run_pipeline',
        '--enriched', str(ENRICHED_FILE),
        '--source-dir', str(CONVERSATIONS_DIR),
        '--output-dir', str(OUTPUT_DIR),
        '--model', args.model,
        '--concurrent', str(args.concurrent),
    ]

    if args.sample:
        pipeline_args.extend(['--sample', str(args.sample)])
    if args.no_llm:
        pipeline_args.append('--no-llm')
    if args.force:
        pipeline_args.append('--force')

    print(f"\nRunning atlas pipeline...")
    print(f"  Command: {' '.join(pipeline_args[1:])}")

    os.chdir(PROJECT_ROOT / "scripts")
    # Add pipeline dir to PYTHONPATH so `from features import ...` works
    pipeline_dir = str(PROJECT_ROOT / "scripts" / "atlas" / "pipeline")
    existing = os.environ.get('PYTHONPATH', '')
    os.environ['PYTHONPATH'] = pipeline_dir + (':' + existing if existing else '')
    os.execv(sys.executable, pipeline_args)


if __name__ == '__main__':
    main()
