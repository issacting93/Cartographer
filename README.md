# Cartographer: Interactional Cartography for Human-AI Conversation

**A graph-structural framework for diagnosing governance failure in human-AI dialogue.**

Cartographer transforms linear chat logs into heterogeneous multi-relational graphs, mapping how user constraints degrade across conversational turns. It provides computational evidence that constraint failure in AI conversation is a structural property of the interaction medium — not a model capability problem — leading to what we term **Agency Collapse**.

---

## Key Findings

| Phase | Study | N | Key Finding |
|-------|-------|---|-------------|
| **Phase 1** | Conversational Cartography | 562 | **83% of variance** explained by interaction dynamics, not role categories |
| **Phase 2** | Agency Collapse | 863 | **50.4% collapse rate** — the "Repair Loop" is a structural trap |
| **Phase 3** | Atlas 2.0 (canonical) | 744 | **71.5% constraint failure**, half-life of 2.49 turns, repair success <0.1% |

### Atlas 2.0 Metrics (N=744)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Constraint Survival Rate** | 28.5% | 71.5% of verifiable instructions are violated silently |
| **Constraint Half-Life** | 2.49 turns | Decay happens within 2–3 exchanges, not at context limits |
| **Repair Success Rate** | 0.1% | Users attempt repair (19.9%), but the medium fails them |
| **Mode Violation Rate** | 42.0% | The AI oversteps its role in nearly half of exchanges |

---

## Methodology

### 7-Step Pipeline

1. **Construct Definition** — Define theoretical constructs (Repair, Passivity, Specificity) before looking at data.
2. **Feature Extraction** — Compute deterministic features (e.g., `repair_count`, `politeness_delta`).
3. **Unsupervised Clustering** — HDBSCAN finds natural groupings in the feature space.
4. **Cluster Characterization** — Descriptive statistics for each cluster.
5. **Agency Collapse Definition** — Binary outcome variable based on thresholds (repeated failed repairs, tone degradation).
6. **Archetype Naming** — Post-hoc labels assigned to empirically derived clusters.
7. **Validation** — Clustering stability (Silhouette > 0.3) and human agreement (kappa > 0.65).

### Graph Schema

**Node Types:**
- `Conversation` — Metadata (source, domain, stability class)
- `Turn` — Individual message (role: user/model)
- `Move` — Communicative act (PROPOSE_CONSTRAINT, REPAIR_INITIATE, etc.)
- `Constraint` — Tracked rule state (STATED → ACTIVE → VIOLATED → SURVIVED)
- `ViolationEvent` — Instance of a constraint violation
- `InteractionMode` — Per-turn mode (LISTENER, ADVISOR, EXECUTOR)

**Edge Types:**
- `NEXT` — Temporal flow
- `CONTAINS` — Hierarchy
- `HAS_MOVE` — Turn-to-Move
- `VIOLATES` — Violation linking
- `REPAIRS` — Repair attempts
- `TRIGGERS` — Causal links

---

## Project Structure

```
Cartographer/
├── scripts/
│   ├── atlas/                       # Core pipeline
│   │   ├── core/                    # Enums and Pydantic models
│   │   ├── graph/                   # Schema validation
│   │   ├── pipeline/                # Pipeline stages
│   │   ├── run_pipeline.py          # Main orchestrator
│   │   ├── move_classifier.py       # Communicative act detection
│   │   ├── mode_detector.py         # Interaction mode classification
│   │   ├── constraint_tracker.py    # Constraint state machine
│   │   ├── graph_metrics.py         # Graph-level metric computation
│   │   └── analysis/                # Post-hoc analysis scripts
│   └── analysis/                    # Comparative analysis
│       ├── bridge_pad_scoring.py    # PAD (Pleasure-Arousal-Dominance) scoring
│       ├── generate_comparative_viz.py
│       └── scientific_analysis.py
│
├── data/
│   ├── atlas_with_pad/              # 100+ PAD-annotated conversation graphs
│   ├── atlas_canonical/             # Canonical Atlas 2.0 outputs
│   ├── features.json                # Extracted feature vectors
│   └── ...                          # Clustered/classified datasets
│
├── public/                          # Visualization & dashboards
│   ├── atlas_suite/                 # BLOOM Design System explorer
│   │   ├── index.html               # Landing page
│   │   ├── explorer.html            # Single-conversation inspector
│   │   ├── dashboard.html           # Aggregate metrics dashboard
│   │   ├── compare.html             # Side-by-side comparison
│   │   └── global_view.html         # Dataset-wide landscape
│   ├── scientific_report/           # Generated figures & report
│   ├── cartography_dashboard.html   # Cartography overview
│   └── comparative_diagnostics.html # Comparative diagnostics view
│
├── paper/                           # Academic papers
│   ├── CHI_2026_Proposal.md         # Agency Collapse (CHI 2026)
│   ├── CUI_2026_Paper.md            # CUI 2026 submission
│   ├── COMPREHENSIVE_FINDINGS_REPORT.md
│   ├── PRIOR_WORK_CONVERSATIONAL_CARTOGRAPHY.md
│   └── figures/                     # Paper figures
│
├── theory/                          # Working notes & theory development
├── frontend/                        # CII Prototype (React + Vite)
├── backend/                         # FastAPI backend
└── context_engine/                  # Task-first context management
```

---

## Running Locally

### Atlas Pipeline

```bash
# Run the full pipeline on a conversation dataset
python scripts/atlas/run_pipeline.py --input data/atlas_canonical/ --output data/atlas_with_pad/
```

### Analysis Scripts

```bash
# Generate PAD bridge scores
python scripts/analysis/bridge_pad_scoring.py

# Produce comparative visualizations
python scripts/analysis/generate_comparative_viz.py

# Run scientific analysis
python scripts/analysis/scientific_analysis.py
```

### Explorer (BLOOM Design System)

```bash
python3 -m http.server 8001 --directory public/
```

Then open:
- **Atlas Suite:** `http://localhost:8001/atlas_suite/`
- **Scientific Report:** `http://localhost:8001/scientific_report/`
- **Cartography Dashboard:** `http://localhost:8001/cartography_dashboard.html`

---

## Data Sources

Conversations are drawn from three public datasets:
- **WildChat** — Organic human-AI conversations
- **Chatbot Arena** — Comparative evaluation dialogues
- **OpenAssistant (OASST)** — Community-contributed conversations

---

## Papers

- **CHI 2026 Proposal** — *Agency Collapse: When Conversational Repair Fails in Human-AI Interaction*
- **CUI 2026** — *Interactional Cartography for Conversational User Interfaces*

---

## License

Research use. See individual data source licenses for dataset terms.
