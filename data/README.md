# Data Directory

This directory contains computed metrics, analysis outputs, and classification results.

## What's Included

- `atlas_v2_production/metrics/` — Production pipeline aggregate metrics (N=744)
- `atlas_v2_production/visualizations/` — Generated figures for the paper
- `atlas_canonical/` — Canonical analysis run with dashboard data
- `atlas/graphs/samples/` — 5 sample conversation graphs for reference
- `analysis/` and `analysis_all/` — Cluster analysis and archetype results
- `classified/` — Dataset classification outputs
- `features*.json` — Extracted conversation features (specificity, stance, repair)

## What's Excluded (too large for git)

- `atlas/graphs/` — 979 full conversation graphs (~190MB). Regenerate with `run_pipeline.py`
- `atlas/cache/` — LLM annotation caches (moves, modes, constraints per conversation)
- `raw/` — Raw conversation sources (available from WildChat, Chatbot Arena, OASST)

## Regenerating Data

```bash
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir /path/to/raw/conversations \
    --output-dir data/atlas
```
