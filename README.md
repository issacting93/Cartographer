# Atlas: Interactional Cartography for Human-AI Conversation

**A graph-structural method for diagnosing governance failure in human-AI dialogue.**

Atlas transforms linear chat logs into heterogeneous multi-relational graphs, mapping how user constraints degrade across conversational turns. It provides computational evidence that constraint failure in AI conversation is a structural property of the interaction medium, not a model capability problem.

---

## Key Findings (N=744)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Constraint Survival Rate** | 28.5% | 71.5% of verifiable instructions are violated silently |
| **Constraint Half-Life** | 2.49 turns | Decay happens within 2-3 exchanges, not at context limits |
| **Repair Success Rate** | 0.1% | Users attempt repair (19.9%), but the medium fails them |
| **Mode Violation Rate** | 42.0% | The AI oversteps its role in nearly half of exchanges |

---

## Architecture

```
Atlas Pipeline
==============

Raw Conversations ──> Move Classifier ──> Constraint Tracker ──> Graph Builder ──> Metrics
                  ──> Mode Detector  ──┘                         (NetworkX         (Aggregation
                      (parallel)                                  MultiDiGraph)      + Reports)
```

### Graph Schema

**6 Node Types:**
- `Conversation` — session-level metadata (source, domain, stability class)
- `Turn` — individual message (role, content preview, move count)
- `Move` — communicative act (PROPOSE_CONSTRAINT, REPAIR_INITIATE, VIOLATE_CONSTRAINT, etc.)
- `Constraint` — tracked rule with state machine (STATED → ACTIVE → VIOLATED → REPAIRED/ABANDONED/SURVIVED)
- `ViolationEvent` — individual violation instance with repair tracking
- `InteractionMode` — per-turn mode annotation (LISTENER, ADVISOR, EXECUTOR)

**8+ Edge Types:**
- `NEXT` — temporal ordering between turns
- `CONTAINS` — conversation → turn hierarchy
- `HAS_MOVE` — turn → move association
- `VIOLATES` — violation event → constraint link
- `REPAIRS` — repair move → violation event link
- `TRIGGERS` — causal edges (move → violation)
- `OPERATES_IN` — turn → interaction mode
- `RATIFIES` — constraint acceptance

### Stability Classes

Conversations are classified into four archetypes based on graph topology:
- **Task Maintained** — model stays on track (low drift)
- **Constraint Drift** — rules are stated but progressively ignored
- **Task Shift** — the core goal is renegotiated
- **Agency Collapse** — user surrenders effort to control output

---

## Project Structure

```
Atlas/
├── scripts/
│   └── atlas/                    # Core pipeline
│       ├── core/
│       │   ├── enums.py          # Node types, edge types, move types, states
│       │   └── models.py         # Pydantic models (Constraint, Turn, Move, etc.)
│       ├── graph/
│       │   └── validators.py     # Graph schema validation
│       ├── run_pipeline.py       # Main orchestrator
│       ├── move_classifier.py    # Hybrid regex + LLM move classification
│       ├── mode_detector.py      # Interaction mode detection
│       ├── constraint_tracker.py # Constraint lifecycle state machine
│       ├── build_atlas_graph.py  # NetworkX graph construction
│       ├── graph_metrics.py      # Drift velocity, agency tax, half-life, etc.
│       ├── utils.py              # Shared utilities and data loaders
│       ├── export_dashboard_data.py
│       ├── generate_visualizations.py
│       ├── generate_friction_heatmap.py
│       ├── dashboard.html        # Interactive metrics dashboard
│       └── explorer.html         # D3.js conversation graph explorer
│
├── frontend/                     # CII Prototype (React + Vite)
│   └── src/
│       ├── components/           # ConstraintSidebar, ChatInterface, etc.
│       └── pages/                # BaselineChat, TreatmentChat, Workspace
│
├── backend/                      # FastAPI backend for prototype
│
├── context_engine/               # Task-first context management
│
├── paper/                        # Paper drafts, figures, references
│   ├── CUI_2026_Paper.tex
│   └── figures/
│
├── CUI-Docs/                     # Research planning and strategy
│   ├── Atlas-One-Pager.md        # CHI submission one-pager
│   ├── CHI-Review-Strategy.md    # Execution plan for CHI
│   ├── CHI-Related-Work-Map.md   # Literature positioning (6 buckets)
│   └── archive/                  # Earlier paper iterations
│
└── data/                         # Computed metrics and analysis outputs
    ├── atlas_v2_production/      # Production run metrics + visualizations
    ├── atlas_canonical/          # Canonical analysis metrics
    ├── analysis/                 # Cluster analysis results
    └── atlas/graphs/samples/     # 5 sample graphs (full set: 979 graphs, ~190MB)
```

---

## Quick Start

### Run the Atlas Pipeline

```bash
# Install dependencies
pip install networkx pydantic openai python-dotenv

# Full run (requires OpenAI API key in .env)
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir /path/to/raw/conversations \
    --output-dir data/atlas \
    --model gpt-4o-mini \
    --concurrent 10

# Deterministic-only (no API key needed)
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir /path/to/raw/conversations \
    --output-dir data/atlas \
    --no-llm

# Sample 10 conversations for testing
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir /path/to/raw/conversations \
    --output-dir data/atlas \
    --sample 10
```

### Run the CII Prototype

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your API key
uvicorn main:app --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Explore the Data

- Open `scripts/atlas/explorer.html` in a browser to visualize individual conversation graphs
- Open `scripts/atlas/dashboard.html` for aggregate metrics dashboards
- See `data/atlas_v2_production/metrics/` for computed metrics

---

## Data Note

The full graph dataset (979 MultiDiGraphs, ~190MB) and LLM annotation caches are excluded from this repository. 5 sample graphs are included in `data/atlas/graphs/samples/` for reference. The raw conversation sources (WildChat, Chatbot Arena, OASST) are available from their respective repositories.

---

## Technical Stack

- **Graph Engine:** NetworkX (MultiDiGraph with Pydantic schema validation)
- **Annotation:** Hybrid regex + LLM (GPT-4o-mini) classification
- **Frontend:** React + Vite + TypeScript + D3.js
- **Backend:** FastAPI + Python
- **Visualization:** D3.js (explorer), Matplotlib (paper figures)

---

## Research Context

This project supports two submission tracks:

- **CUI 2026:** Empirical analysis of conversational drift + CII prototype
- **CHI 2027 (planned):** Validated method paper — Interactional Cartography as a reusable diagnostic framework, with graph clustering validation, predictive motifs, and constraint resurfacing simulation

See `CUI-Docs/Atlas-One-Pager.md` and `CUI-Docs/CHI-Review-Strategy.md` for the full research strategy.

---

## License

Research use. Please cite if you use this work.
