#!/usr/bin/env python3
"""
Atlas Graph Pipeline Orchestrator

Runs the full classification pipeline on existing task-classified conversations:
  1. Load enriched data + raw conversations
  2. Classify Moves (hybrid: regex + LLM)
  3. Detect Interaction Modes (regex + LLM fallback)  [parallel with step 2]
  4. Track Constraint Lifecycles (deterministic)
  5. Build Atlas Graph (deterministic)
  6. Compute Metrics (deterministic)
  7. Export + aggregate

Usage:
    # Full run with LLM
    python -m atlas.run_pipeline \\
        --enriched data/task_classified/all_task_enriched.json \\
        --source-dir /Users/zac/Downloads/Cartography/public/output \\
        --output-dir data/atlas \\
        --model gpt-4o-mini \\
        --concurrent 10

    # Deterministic-only (no LLM, no API key needed)
    python -m atlas.run_pipeline \\
        --enriched data/task_classified/all_task_enriched.json \\
        --source-dir /Users/zac/Downloads/Cartography/public/output \\
        --output-dir data/atlas \\
        --no-llm

    # Sample 10 for testing
    python -m atlas.run_pipeline \\
        --enriched data/task_classified/all_task_enriched.json \\
        --source-dir /Users/zac/Downloads/Cartography/public/output \\
        --output-dir data/atlas \\
        --sample 10
"""

import os
import sys
import json
import asyncio
import argparse
import time
import random
import hashlib
from pathlib import Path
from dataclasses import asdict

# Add parent dir to path for features.py import
sys.path.insert(0, str(Path(__file__).parent.parent))

from atlas.utils import (
    ConversationMetrics,
    load_conversation,
)
from atlas.move_classifier import classify_moves
from atlas.mode_detector import detect_mode_violations
from atlas.constraint_tracker import build_constraint_tracker
from atlas.build_atlas_graph import build_graph, export_graph, graph_summary
from atlas.graph_metrics import compute_metrics, aggregate_metrics, generate_report


# ============= Pipeline =============

async def process_conversation(
    entry: dict,
    source_dir: Path,
    output_dir: Path,
    client,
    model: str,
    use_llm: bool = True,
    force: bool = False,
) -> dict:
    """
    Process a single conversation through the full pipeline.

    Returns dict with conversation_id, metrics, and graph_summary.
    """
    conv_id = entry.get("id", "unknown")
    file_path = entry.get("file_path", "")
    cls = entry.get("classification", {})
    tax = entry.get("taxonomy", {})

    # Check cache
    cache_file = output_dir / "cache" / "metrics" / f"{conv_id}.json"
    if cache_file.exists() and not force:
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass

    # 1. Load raw conversation
    raw = load_conversation(file_path)
    if not raw or not raw.get("messages"):
        # Try resolving via source_dir
        fname = Path(file_path).name
        alt_path = source_dir / fname
        raw = load_conversation(str(alt_path))

    if not raw or not raw.get("messages"):
        return {"conversation_id": conv_id, "error": "raw_not_found"}

    messages = raw["messages"]
    primary_constraints = cls.get("primary_constraints", [])
    evidence = cls.get("evidence", {})
    task_goal = cls.get("task_goal", "")

    llm_client = client if use_llm else None

    # 2 & 3. Run Move classifier and Mode detector in parallel
    move_task = classify_moves(
        messages, primary_constraints, evidence, task_goal,
        client=llm_client, model=model,
    )
    mode_task = detect_mode_violations(
        messages, client=llm_client, model=model,
    )

    messages_with_moves, mode_annotations = await asyncio.gather(
        move_task, mode_task
    )

    # 4. Constraint tracker (deterministic, depends on moves)
    constraint_track = build_constraint_tracker(
        messages_with_moves, primary_constraints, evidence,
    )

    # 5. Build graph
    G = build_graph(
        conv_id, messages_with_moves, constraint_track,
        mode_annotations, entry,
    )

    # 6. Compute metrics
    metrics = compute_metrics(
        G,
        conversation_id=conv_id,
        stability_class=cls.get("stability_class", ""),
        task_architecture=tax.get("architecture", ""),
        constraint_hardness=tax.get("constraint_hardness", ""),
    )

    # 7. Export graph
    graph_dir = output_dir / "graphs"
    graph_dir.mkdir(parents=True, exist_ok=True)
    export_graph(G, graph_dir / f"{conv_id}.json", fmt="json")

    # Cache individual results
    summary = graph_summary(G)
    result = {
        "conversation_id": conv_id,
        "metrics": metrics.model_dump(),
        "graph_summary": summary,
    }

    # Cache moves
    moves_cache = output_dir / "cache" / "moves" / f"{conv_id}.json"
    moves_cache.parent.mkdir(parents=True, exist_ok=True)
    with open(moves_cache, 'w') as f:
        json.dump(messages_with_moves, f, indent=2, default=str)

    # Cache modes
    modes_cache = output_dir / "cache" / "modes" / f"{conv_id}.json"
    modes_cache.parent.mkdir(parents=True, exist_ok=True)
    with open(modes_cache, 'w') as f:
        json.dump([m.model_dump() for m in mode_annotations], f, indent=2)

    # Cache constraints
    constraints_cache = output_dir / "cache" / "constraints" / f"{conv_id}.json"
    constraints_cache.parent.mkdir(parents=True, exist_ok=True)
    with open(constraints_cache, 'w') as f:
        json.dump(constraint_track.model_dump(), f, indent=2)

    # Cache metrics
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(result, f, indent=2)

    return result


async def run_pipeline(args):
    """Main pipeline execution."""

    # Load enriched data
    print(f"Loading enriched data from {args.enriched}...")
    with open(args.enriched, 'r') as f:
        data = json.load(f)
    print(f"  Loaded {len(data)} entries")

    # Sample if requested
    if args.sample:
        data = random.sample(data, min(args.sample, len(data)))
        print(f"  Sampled {len(data)} entries")

    # Setup output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = Path(args.source_dir)

    # Setup LLM client
    client = None
    use_llm = not args.no_llm
    if use_llm:
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        except ImportError:
            pass

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  Warning: OPENAI_API_KEY not set. Running deterministic-only.")
            use_llm = False
        else:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            print(f"  LLM enabled: {args.model}")

    if not use_llm:
        print("  Running in deterministic-only mode (no LLM)")

    # Process conversations
    semaphore = asyncio.Semaphore(args.concurrent)
    results = []
    errors = []
    start_time = time.time()

    async def process_with_limit(entry):
        async with semaphore:
            try:
                return await process_conversation(
                    entry, source_dir, output_dir, client, args.model, use_llm, 
                    force=args.force,
                )
            except Exception as e:
                conv_id = entry.get("id", "?")
                print(f"\n  Error processing {conv_id}: {e}")
                return {"conversation_id": conv_id, "error": str(e)}

    print(f"\nProcessing {len(data)} conversations (concurrency: {args.concurrent})...")

    tasks = [process_with_limit(entry) for entry in data]
    completed = 0

    for coro in asyncio.as_completed(tasks):
        result = await coro
        if result.get("error"):
            errors.append(result)
        else:
            results.append(result)
        completed += 1
        if completed % 50 == 0 or completed == len(data):
            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            print(f"  [{completed}/{len(data)}] {len(results)} ok, {len(errors)} errors ({rate:.1f}/s)")

    duration = time.time() - start_time
    print(f"\nCompleted in {duration:.1f}s")
    print(f"  Success: {len(results)}")
    print(f"  Errors: {len(errors)}")

    if not results:
        print("No results to aggregate.")
        return

    # Aggregate metrics
    all_metrics = [
        ConversationMetrics(**r["metrics"])
        for r in results
        if "metrics" in r
    ]

    # Save aggregate metrics
    metrics_dir = output_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    agg = aggregate_metrics(all_metrics)

    with open(metrics_dir / "all_metrics.json", 'w') as f:
        json.dump([m.model_dump() for m in all_metrics], f, indent=2)

    with open(metrics_dir / "aggregate.json", 'w') as f:
        json.dump(agg, f, indent=2)

    # Breakdown files
    with open(metrics_dir / "by_stability_class.json", 'w') as f:
        json.dump(agg.get("by_stability_class", {}), f, indent=2)

    with open(metrics_dir / "by_architecture.json", 'w') as f:
        json.dump(agg.get("by_architecture", {}), f, indent=2)

    with open(metrics_dir / "by_hardness.json", 'w') as f:
        json.dump(agg.get("by_hardness", {}), f, indent=2)

    # Generate report
    generate_report(all_metrics, metrics_dir / "metrics_report.md")

    # Print summary
    overall = agg.get("overall", {})
    print(f"\n{'='*60}")
    print(f"ATLAS PIPELINE RESULTS (N={agg['total']})")
    print(f"{'='*60}")
    print(f"  Drift Velocity (mean):        {overall.get('mean_drift_velocity', '-')}")
    print(f"  Agency Tax (mean):            {overall.get('mean_agency_tax', '-')}")
    print(f"  Constraint Half-Life (mean):  {overall.get('mean_constraint_half_life', '-')}")
    print(f"  Constraint Survival Rate:     {overall.get('mean_survival_rate', '-')}")
    print(f"  Mode Violation Rate:          {overall.get('mean_mode_violation_rate', '-')}")
    print(f"  Move Coverage:                {overall.get('mean_move_coverage', '-')}")
    print(f"  Repair Success Rate:          {overall.get('mean_repair_success_rate', '-')}")
    print(f"  Total Constraints:            {overall.get('total_constraints', 0)}")
    print(f"  Total Violations:             {overall.get('total_violations', 0)}")
    print(f"  Total Repairs:                {overall.get('total_repairs', 0)}")

    print(f"\nBy Stability Class:")
    for cls_name, stats in agg.get("by_stability_class", {}).items():
        print(f"  {cls_name:<20} N={stats['n']:<5} drift={stats.get('mean_drift_velocity', '-')}")

    print(f"\nOutputs saved to: {output_dir}")
    print(f"  Graphs:  {output_dir}/graphs/")
    print(f"  Metrics: {output_dir}/metrics/")
    print(f"  Cache:   {output_dir}/cache/")

    if errors:
        error_log = output_dir / "errors.json"
        with open(error_log, 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"  Errors:  {error_log}")


def main():
    parser = argparse.ArgumentParser(
        description="Atlas Graph Pipeline: classify conversations into task-state graphs"
    )
    parser.add_argument(
        "--enriched", required=True,
        help="Path to all_task_enriched.json (aggregate input)",
    )
    parser.add_argument(
        "--source-dir", required=True,
        help="Directory containing raw conversation JSONs",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Output directory for graphs, metrics, and cache",
    )
    parser.add_argument(
        "--sample", type=int, default=None,
        help="Process only N random conversations (for testing)",
    )
    parser.add_argument(
        "--model", default="gpt-4o-mini",
        help="OpenAI model for LLM steps (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--concurrent", type=int, default=10,
        help="Max concurrent LLM requests (default: 10)",
    )
    parser.add_argument(
        "--no-llm", action="store_true",
        help="Run deterministic-only (no API calls)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Bypass cache and re-process all sampled conversations",
    )
    args = parser.parse_args()

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
