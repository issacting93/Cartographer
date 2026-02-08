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

## Methodology

Atlas employs a rigorous, empirically-driven pipeline to identify "Agency Collapse." Unlike purely qualitative approaches, our archetypes are post-hoc labels assigned to empirically derived clusters.

### 7-Step Pipeline

1.  **Construct Definition:** We define theoretical constructs (Repair, Passivity, Specificity) before looking at data.
2.  **Feature Extraction:** We compute deterministic features (e.g., `repair_count`, `politeness_delta`).
3.  **Unsupervised Clustering:** We use **HDBSCAN** to find natural groupings in the feature space ($X \in \mathbb{R}^{N \times D}$).
4.  **Cluster Characterization:** We compute descriptive statistics for each cluster (e.g., "Cluster 0 has high repair count and low success").
5.  **Agency Collapse Definition:** We define "Collapse" as a binary outcome variable based on specific thresholds (e.g., repeated failed repairs, tone degradation).
6.  **Archetype Naming:** We assign descriptive post-hoc labels to clusters (e.g., "Passive Acceptance").
7.  **Validation:** We validate findings via clustering stability (Silhouette > 0.3) and human agreement ($\kappa > 0.65$).

### Key Definitions

| Construct | Definition |
|-----------|------------|
| **Agency Collapse** | Theoretical outcome where the user's capacity to direct interaction degrades over time. Defined by repeated failed repairs, tone degradation, or specificity collapse. |
| **Repair** | User attempts to correct AI misunderstanding. |
| **Passivity** | User accepts AI output without modification. |
| **Specificity** | Precision of user's stated requirements. |
| **Politeness** | Markers of face-saving behavior. |

**Note:** "Agency Collapse" is an outcome variable, while "Archetypes" are cluster patterns. A conversation can show collapse without fitting a specific archetype.

---

## BLOOM Design System (New in v2.0)

Atlas v2.0 exclusively uses the **BLOOM Design System**, a high-contrast interaction language designed for clarity and agency preservation.

### Core Principles
- **Light Mode Aesthetic:** High-contrast Black/Yellow/Orange palette on white.
- **Semantic Components:** "Pills" for filters, "Nodes" for graph entities, and "Cards" for inspection.
- **Visual Hierarchy:** Critical failures (Violations) are alarmed with Orange/Red, while maintained agency is Green.

### Views

| View | Description | File |
|------|-------------|------|
| **Atlas Meta-Graph** | A macro-view of the entire dataset (700+ conversations), clustered by stability. | `scripts/atlas/atlas.html` |
| **Explorer** | A detailed, single-conversation inspector for diagnosing constraint collapse. | `scripts/atlas/explorer.html` |

---

## Architecture & Graph Schema

The Atlas pipeline converts raw text into a NetworkX MultiDiGraph, which is then visualized via D3.js.

### Node Types
- `Conversation` — Metadata (source, domain, stability class)
- `Turn` — Individual message (role: user/model)
- `Move` — Communicative act (PROPOSE_CONSTRAINT, REPAIR_INITIATE, etc.)
- `Constraint` — Tracked rule state (STATED → ACTIVE → VIOLATED → SURVIVED)
- `ViolationEvent` — Instance of a constraint violation
- `InteractionMode` — Per-turn mode (LISTENER, ADVISOR, EXECUTOR)

### Edge Types
- `NEXT` — Temporal flow
- `CONTAINS` — Hierarchy
- `HAS_MOVE` — Turn-to-Move
- `VIOLATES` — Violation linking
- `REPAIRS` — Repair attempts
- `TRIGGERS` — Causal links

---

## Project Structure

```
Atlas/
├── scripts/
│   └── atlas/                    # Core pipeline
│       ├── core/                 # Enums and Pydantic models
│       ├── graph/                # Schema validation
│       ├── run_pipeline.py       # Main orchestrator
│       ├── atlas.html            # [NEW] Meta-Graph View (BLOOM Style)
│       ├── explorer.html         # [UPDATED] Single Graph Explorer (BLOOM Style)
│       ├── bloom.css             # [NEW] Shared Design System
│       └── ...                   # Analysis scripts
│
├── frontend/                     # CII Prototype (React + Vite)
├── backend/                      # FastAPI backend
├── context_engine/               # Task-first context management
└── paper/                        # Paper drafts, figures, references
```

## Running the Explorer

1.  Start a local server:
    ```bash
    python3 -m http.server 8001
    ```
2.  Open **Atlas View** to see the landscape:
    `http://localhost:8001/scripts/atlas/atlas.html`
3.  Open **Explorer** to dive into a specific conversation:
    `http://localhost:8001/scripts/atlas/explorer.html`
