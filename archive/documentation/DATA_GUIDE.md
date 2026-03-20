# Data Guide

**Understanding the data directory structure, provenance, and reproduction.**

---

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [Data Provenance](#data-provenance)
3. [Key Files](#key-files)
4. [Reproduction Guide](#reproduction-guide)
5. [Data Validation](#data-validation)
6. [Adding New Data](#adding-new-data)

---

## Directory Structure

```
data/
├── raw/                          # ⚠️ .gitignored (too large)
│   ├── wildchat/                 # WildChat conversations
│   ├── oasst/                    # OpenAssistant
│   └── arena/                    # Chatbot Arena
│
├── task_classified/              # 📝 LLM-enriched classifications
│   └── all_task_enriched.json   # N=969 classified conversations
│
├── atlas_canonical/              # 📊 Production pipeline run (N=744)
│   ├── cache/                    # ⚠️ .gitignored (intermediate LLM outputs)
│   │   ├── moves/{conv_id}.json
│   │   ├── modes/{conv_id}.json
│   │   └── constraints/{conv_id}.json
│   ├── graphs/                   # 🔀 Conversation graphs (NetworkX exports)
│   │   └── {conv_id}.json       # Node-link format
│   ├── metrics/                  # 📈 Computed CUI metrics
│   │   ├── all_metrics.json     # Per-conversation metrics
│   │   ├── aggregate.json       # Cross-conversation aggregates
│   │   ├── by_stability_class.json
│   │   ├── by_architecture.json
│   │   ├── by_hardness.json
│   │   └── metrics_report.md    # Human-readable summary
│   ├── dashboard_data.json      # D3.js visualization data
│   └── meta_graph.json          # Graph of graph metrics
│
├── atlas_v2_production/         # 📊 Latest production run (paper results)
│   ├── metrics/
│   └── visualizations/          # Generated figures
│       ├── drift_velocity_distribution.png
│       ├── agency_tax_boxplot.png
│       └── constraint_half_life.png
│
├── analysis/                    # 📉 Statistical analysis
│   └── figures/                 # Cluster visualizations
│
├── analysis_all/                # 📉 Full dataset analysis
│   └── figures/
│       ├── cluster_heatmap.png
│       ├── stability_breakdown.png
│       └── repair_distribution.png
│
├── classified/                  # Early classification experiments
├── clustered/                   # HDBSCAN/k-means outputs
├── clustered_llm/               # LLM-enhanced clustering
│
└── features*.json               # Extracted features (19 per conversation)
```

---

## Data Provenance

### Source Datasets

| Dataset | N | License | Source | Purpose |
|---------|---|---------|--------|---------|
| **WildChat** | 1M | CC-BY-SA 4.0 | [Hugging Face](https://huggingface.co/datasets/allenai/wildchat) | Organic human-AI conversations |
| **Chatbot Arena** | 100K+ | MIT | [LMSYS](https://chat.lmsys.org/) | Comparative evaluations |
| **OpenAssistant (OASST)** | 161K+ | Apache 2.0 | [GitHub](https://github.com/LAION-AI/Open-Assistant) | Community conversations |

**Our Subset:**
- **Total:** 969 conversations (post-filtering)
- **Canonical Analysis:** 744 conversations
- **Filtering criteria:**
  - Contains ≥1 user-defined constraint
  - ≥ 5 turns
  - English language
  - Valid JSON structure

### Processing Pipeline

```
┌─────────────────┐
│  Raw Data       │  WildChat, OASST, Arena (JSON files)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  features.py    │  Extract 19 deterministic features
└────────┬────────┘
         │ features.json
         ▼
┌─────────────────┐
│  cluster.py     │  HDBSCAN clustering (k=5)
└────────┬────────┘
         │ clustered/
         ▼
┌─────────────────┐
│classify_task    │  LLM classification (stability class, constraints)
│  _first.py      │  Model: gpt-4o-mini
└────────┬────────┘
         │ all_task_enriched.json
         ▼
┌─────────────────┐
│run_pipeline.py  │  7-stage pipeline (moves, modes, constraints, graph, metrics)
└────────┬────────┘
         │
         ├─ cache/              (LLM annotations)
         ├─ graphs/             (NetworkX exports)
         └─ metrics/            (8 CUI metrics)
```

### **Version History**

| Version | Date | N | Notes |
|---------|------|---|-------|
| `atlas_v1` | 2025-11 | 562 | Initial Conversational Cartography study |
| `atlas_v2_production` | 2026-01 | 744 | Canonical run for CUI 2026 paper |
| `atlas_canonical` | 2026-02 | 744 | Frozen version for reproducibility |

---

## Key Files

### 1. `all_task_enriched.json`

**Purpose:** LLM-classified conversations with task metadata

**Location:** `data/task_classified/all_task_enriched.json`

**Schema:**
```json
{
  "id": "wildchat_new_abc123",
  "file_path": "/path/to/raw/abc123.json",
  "source": "WildChat",
  "domain": "coding",
  "total_turns": 12,
  "classification": {
    "task_goal": "Write a Python web scraper",
    "stability_class": "Constraint Drift",
    "task_architecture": "Single-shot code generation",
    "constraint_hardness": "hard",
    "constraints": [
      {
        "id": "c_0",
        "text": "use only Python standard library",
        "type": "hard"
      }
    ]
  }
}
```

**Size:** ~2-5 MB (969 entries)

**Generation command:**
```bash
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/ \
  --output data/task_classified/all_task_enriched.json \
  --model gpt-4o-mini
```

---

### 2. `all_metrics.json`

**Purpose:** Computed CUI metrics for each conversation

**Location:** `data/atlas_canonical/metrics/all_metrics.json`

**Schema:**
```json
{
  "conversation_id": "wildchat_new_abc123",
  "drift_velocity": 0.42,
  "agency_tax": 1.75,
  "constraint_half_life": 2.5,
  "constraint_survival_rate": 0.33,
  "mode_violation_rate": 0.25,
  "repair_success_rate": 0.67,
  "mean_constraint_lifespan": 4.2,
  "mode_entropy": 1.35,
  "total_violations": 5,
  "total_repairs": 3,
  "total_constraints": 3,
  "total_turns": 12,
  "move_coverage": 0.92,
  "stability_class": "Constraint Drift",
  "task_architecture": "Single-shot code generation",
  "constraint_hardness": "hard"
}
```

**Size:** ~500 KB - 1 MB (744 entries)

---

### 3. `aggregate.json`

**Purpose:** Cross-conversation statistics

**Location:** `data/atlas_canonical/metrics/aggregate.json`

**Schema:**
```json
{
  "overall": {
    "drift_velocity_mean": 0.52,
    "drift_velocity_std": 0.31,
    "agency_tax_mean": 1.42,
    "constraint_half_life_mean": 2.49,
    "constraint_survival_rate_mean": 0.285,
    ...
  },
  "by_stability_class": {
    "Task Maintained": { "drift_velocity_mean": 0.12, ... },
    "Constraint Drift": { "drift_velocity_mean": 0.48, ... },
    "Agency Collapse": { "drift_velocity_mean": 0.89, ... }
  }
}
```

---

### 4. Conversation Graphs (`graphs/{conv_id}.json`)

**Purpose:** NetworkX MultiDiGraph in node-link format

**Location:** `data/atlas_canonical/graphs/wildchat_new_abc123.json`

**Schema:** See [DOCUMENTATION.md Section 7.1](DOCUMENTATION.md#71-graph-json-node-link)

**Example:**
```json
{
  "directed": true,
  "multigraph": true,
  "nodes": [
    {"node_type": "Conversation", "conv_id": "abc123", ...},
    {"node_type": "Turn", "turn_index": 0, ...},
    {"node_type": "Move", "move_type": "PROPOSE_CONSTRAINT", ...}
  ],
  "links": [
    {"edge_type": "CONTAINS", "source": "conv_abc123", "target": "t_abc123_0"}
  ]
}
```

**Size:** 5-50 KB per graph

---

### 5. `dashboard_data.json`

**Purpose:** D3.js visualization data

**Location:** `data/atlas_canonical/dashboard_data.json`

**Contains:**
- Scatter plot coordinates (Drift vs. Agency Tax)
- Color coding by stability class
- Hover data (conversation IDs, metrics)

---

## Reproduction Guide

### Reproduce Canonical Results

**Prerequisites:**
1. Python 3.10+
2. OpenAI API key
3. ~3 hours of compute time

**Steps:**

```bash
# 1. Download source data (if not already present)
# See INSTALLATION.md for dataset downloads

# 2. Generate classifications
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/ \
  --output data/task_classified/all_task_enriched.json \
  --model gpt-4o-mini \
  --workers 3

# 3. Run full pipeline
python -m scripts.atlas.run_pipeline \
  --enriched data/task_classified/all_task_enriched.json \
  --output-dir data/atlas_canonical \
  --model gpt-4o-mini \
  --workers 5 \
  --force  # Overwrite existing cache

# 4. Validate results
python scripts/validate_data.py
```

**Expected outputs:**
- `data/atlas_canonical/metrics/all_metrics.json` (744 conversations)
- `data/atlas_canonical/metrics/aggregate.json`
- `data/atlas_canonical/graphs/*.json` (744 graph files)

---

### Reproduce Paper Figures

```bash
# Generate visualizations
python scripts/analysis/generate_comparative_viz.py \
  --metrics data/atlas_canonical/metrics/all_metrics.json \
  --output data/atlas_v2_production/visualizations/

# Figures generated:
# - drift_velocity_distribution.png
# - agency_tax_boxplot.png
# - constraint_half_life.png
# - stability_class_breakdown.png
```

---

## Data Validation

### Automated Validation Script

Create `scripts/validate_data.py`:

```python
#!/usr/bin/env python3
"""Validate data integrity for reproducibility."""

import json
from pathlib import Path

def validate():
    """Run validation checks."""
    
    # Check file existence
    required_files = [
        "data/task_classified/all_task_enriched.json",
        "data/atlas_canonical/metrics/all_metrics.json",
        "data/atlas_canonical/metrics/aggregate.json"
    ]
    
    for file_path in required_files:
        assert Path(file_path).exists(), f"Missing: {file_path}"
    
    # Check conversation count
    with open("data/atlas_canonical/metrics/all_metrics.json") as f:
        metrics = json.load(f)
    
    assert len(metrics) == 744, f"Expected N=744, got {len(metrics)}"
    
    # Check metric ranges
    for m in metrics:
        assert 0 <= m["drift_velocity"] <= 10, "drift_velocity out of range"
        assert 0 <= m["constraint_survival_rate"] <= 1, "survival_rate out of range"
    
    print("✅ All validation checks passed")

if __name__ == "__main__":
    validate()
```

**Run:**
```bash
python scripts/validate_data.py
```

---

### Manual Checks

```bash
# Check conversation count
jq '. | length' data/atlas_canonical/metrics/all_metrics.json
# Expected: 744

# Check stability class distribution
jq '[.[] | .stability_class] | group_by(.) | map({class: .[0], count: length})' \
  data/atlas_canonical/metrics/all_metrics.json

# Check average metrics
jq '[.[] | .drift_velocity] | add/length' \
  data/atlas_canonical/metrics/all_metrics.json
# Expected: ~0.52
```

---

## Adding New Data

### Add a Single Conversation

```bash
# 1. Create JSON file
cat > data/raw/my_conversation.json << 'EOF'
{
  "messages": [
    {"role": "user", "content": "Write a Python function to reverse a string"},
    {"role": "assistant", "content": "Here's a function:\n\ndef reverse_string(s):\n    return s[::-1]"}
  ]
}
EOF

# 2. Classify it
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/my_conversation.json \
  --output data/my_enriched.json \
  --model gpt-4o-mini

# 3. Run pipeline
python -m scripts.atlas.run_pipeline \
  --enriched data/my_enriched.json \
  --output-dir data/my_output
```

---

### Add a New Dataset

```bash
# 1. Place raw files in data/raw/{dataset_name}/

# 2. Convert to standard format (if needed)
python scripts/converters/convert_{dataset}_to_standard.py

# 3. Classify
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/{dataset_name}/ \
  --output data/task_classified/{dataset}_enriched.json

# 4. Merge with existing
jq -s 'add' \
  data/task_classified/all_task_enriched.json \
  data/task_classified/{dataset}_enriched.json \
  > data/task_classified/merged.json

# 5. Run pipeline on merged data
python -m scripts.atlas.run_pipeline \
  --enriched data/task_classified/merged.json \
  --output-dir data/atlas_merged
```

---

## Data Size Summary

| Directory | Tracked (Git) | Ignored (.gitignore) |
|-----------|---------------|----------------------|
| `raw/` | 0 | ~500 MB |
| `task_classified/` | 2-5 MB | 0 |
| `atlas_canonical/cache/` | 0 | ~50 MB |
| `atlas_canonical/graphs/` | ~30 MB | 0 |
| `atlas_canonical/metrics/` | ~1 MB | 0 |
| **Total** | **~35 MB** | **~550 MB** |

**Git-tracked files:** 1,895 files (metadata, graphs, metrics)  
**Gitignored files:** Raw data, LLM caches

---

## Data Licenses

All output data (`graphs/`, `metrics/`) inherits licenses from source datasets:

- **WildChat:** CC-BY-SA 4.0 (share-alike)
- **OASST:** Apache 2.0 (permissive)
- **Chatbot Arena:** MIT (permissive)

**Citation:**
```bibtex
@inproceedings{cartographer2026,
  title={Agency Collapse: Diagnosing Governance Failure in Human-AI Dialogue},
  author={...},
  booktitle={CUI 2026},
  year={2026}
}
```

---

## Next Steps

- **Understand the pipeline:** [DOCUMENTATION.md Section 2](DOCUMENTATION.md#2-pipeline-deep-dive)
- **Run your first analysis:** [GETTING_STARTED.md](GETTING_STARTED.md)
- **Explore metrics:** [DOCUMENTATION.md Section 5](DOCUMENTATION.md#5-metrics-reference)

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue.
