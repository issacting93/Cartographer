# Cartographer: Technical Documentation

Complete technical reference for the Cartographer system — a graph-structural framework for diagnosing governance failure in human-AI dialogue.

---

## Table of Contents

1. [Overview & Architecture](#1-overview--architecture)
2. [Pipeline Deep-Dive](#2-pipeline-deep-dive)
3. [Data Models & Enums](#3-data-models--enums)
4. [Graph Schema](#4-graph-schema)
5. [Metrics Reference](#5-metrics-reference)
6. [Analysis Tools](#6-analysis-tools)
7. [Data Formats](#7-data-formats)
8. [Visualization](#8-visualization)
9. [Running the System](#9-running-the-system)
10. [Academic Context](#10-academic-context)

---

## 1. Overview & Architecture

Cartographer is a multi-phase research program that applies interactional linguistics to human-AI conversation. It models each conversation as a directed multigraph, where turns, moves, constraints, interaction modes, and violation events are nodes connected by typed edges. This structural representation enables quantitative measurement of how well AI systems respect user-defined constraints.

### Research Phases

| Phase | Study | N | Key Finding |
|-------|-------|---|-------------|
| 1 | Conversational Cartography | 2,577 | 97% instrumental roles; 2,817x affect variance within identical role labels |
| 2 | Agency Collapse | 863 | 50.3% collapse rate — "Repair Loop" is a structural trap |
| 3 | Atlas 2.0 (canonical) | 745 | 71.5% constraint failure, mean 2.5 turns to violation, <1% repair |

### Data Sources

- **WildChat** — Organic human-AI conversations
- **Chatbot Arena** — Comparative evaluation dialogues
- **OpenAssistant (OASST)** — Community-contributed conversations

### High-Level Data Flow

```
Raw Conversations (JSON)
        │
        ▼
┌─────────────────────────┐
│  classify_task_first.py │  LLM: stability class, constraints, task goal
└────────────┬────────────┘
             │ all_task_enriched.json
             ▼
┌─────────────────────────┐
│     run_pipeline.py     │  Orchestrator
│  ┌───────────────────┐  │
│  │ move_classifier.py│──┤  Hybrid regex+LLM → 13 move types
│  │ mode_detector.py  │──┤  Regex+LLM → 3 interaction modes  [parallel]
│  └───────────────────┘  │
│           │              │
│  constraint_tracker.py ──┤  Deterministic state machine
│           │              │
│  build_atlas_graph.py  ──┤  NetworkX MultiDiGraph construction
│           │              │
│  graph_metrics.py      ──┤  8 CUI metrics per conversation
│           │              │
│      Export + Cache     ─┤  JSON graphs, aggregate metrics
└─────────────────────────┘
             │
             ▼
   ┌─────────────────┐
   │  Analysis Tools  │  PAD scoring, statistical tests, visualization
   └─────────────────┘
```

### Upstream Stages (Pre-Pipeline)

```
Raw Conversations
        │
   features.py ────→ features.json (19 deterministic features)
        │
    cluster.py ────→ HDBSCAN/k-means clusters
        │
classify_task_first.py → all_task_enriched.json (LLM classification)
```

---

## 2. Pipeline Deep-Dive

### 2.1 `run_pipeline.py` — Orchestrator

**Location:** `scripts/atlas/run_pipeline.py`

Executes the 7-stage pipeline for each conversation:

| Stage | Step | Type | Dependency |
|-------|------|------|------------|
| 1 | Load enriched data + raw conversation | I/O | — |
| 2 | Classify Moves | Hybrid (regex+LLM) | Stage 1 |
| 3 | Detect Interaction Modes | Hybrid (regex+LLM) | Stage 1 (parallel with 2) |
| 4 | Track Constraint Lifecycles | Deterministic | Stage 2 |
| 5 | Build Atlas Graph | Deterministic | Stages 2, 3, 4 |
| 6 | Compute Metrics | Deterministic | Stage 5 |
| 7 | Export + Aggregate | I/O | Stage 6 |

**Key function:**

```python
async def process_conversation(
    entry: dict,           # From all_task_enriched.json
    source_dir: Path,
    output_dir: Path,
    client,                # AsyncOpenAI client (or None)
    model: str,
    use_llm: bool = True,
    force: bool = False,
) -> dict:  # {"conversation_id", "metrics", "graph_summary"}
```

Stages 2 and 3 run in parallel via `asyncio.gather()`. Stages 4–7 run sequentially.

**Cache structure:**

```
output_dir/
├── cache/
│   ├── moves/{conv_id}.json
│   ├── modes/{conv_id}.json
│   ├── constraints/{conv_id}.json
│   └── metrics/{conv_id}.json
├── graphs/{conv_id}.json          # Node-link format
└── metrics/
    ├── all_metrics.json
    ├── aggregate.json
    ├── by_stability_class.json
    ├── by_architecture.json
    ├── by_hardness.json
    └── metrics_report.md
```

---

### 2.2 `move_classifier.py` — 13-Move Taxonomy

**Location:** `scripts/atlas/move_classifier.py`

Classifies each turn into one or more of 13 conversational move types using a hybrid approach.

#### The 13-Move Taxonomy

| Category | Move Type | Actor | Detection Method |
|----------|-----------|-------|-----------------|
| **Constraint Lifecycle** | `PROPOSE_CONSTRAINT` | User | Regex (plural) |
| | `ACCEPT_CONSTRAINT` | Assistant | Regex (singular) |
| | `VIOLATE_CONSTRAINT` | Assistant | LLM (plural) |
| | `RATIFY_CONSTRAINT` | User | Inferred (singular) |
| **Repair** | `REPAIR_INITIATE` | User | Regex (plural) |
| | `REPAIR_EXECUTE` | Assistant | Regex (singular) |
| | `ABANDON_CONSTRAINT` | User | Inferred (singular) |
| **Task Structure** | `STATE_GOAL` | User | Regex (singular) |
| | `TASK_SHIFT` | User | LLM (singular) |
| | `GENERATE_OUTPUT` | Assistant | Inferred (singular) |
| **Interactional** | `REQUEST_CLARIFICATION` | Assistant | Regex (singular) |
| | `PROVIDE_INFORMATION` | User | Inferred (plural) |
| | `PASSIVE_ACCEPT` | User | Regex (singular) |

"Singular" = at most one per turn. "Plural" = multiple allowed per turn.

#### Detection Methods

**Regex detectors** match linguistic patterns:

| Move | Key Patterns |
|------|-------------|
| `PROPOSE_CONSTRAINT` | `must`, `need to`, `no more than`, `cannot`, `always`, `never` |
| `ACCEPT_CONSTRAINT` | `i'll make sure`, `noted`, `as you requested` |
| `REPAIR_INITIATE` | `no i meant`, `that's not what i`, `again,`, `did you read` |
| `REPAIR_EXECUTE` | `i apologize`, `let me correct`, `you're right` |
| `REQUEST_CLARIFICATION` | `could you clarify`, `what exactly` |
| `PASSIVE_ACCEPT` | `ok`, `sure`, `thanks` (short messages only) |
| `STATE_GOAL` | `goal`, `objective`, `trying to` |

**LLM detectors** (OpenAI API, skipped with `--no-llm`):

- `VIOLATE_CONSTRAINT` — Checks if AI response contradicts active constraints. Uses an aspirational constraint filter to reject quality standards (`be accurate`, `provide correct code`). Only flags violations with confidence > 0.7.
- `TASK_SHIFT` — Checks if user completely abandoned their original goal.

**Inferred detectors** (rule-based state machine):

- `RATIFY_CONSTRAINT` — AI accepted in previous turn AND user doesn't repair in current turn.
- `ABANDON_CONSTRAINT` — User passively accepts after a violation.
- `PROVIDE_INFORMATION` — User responds to clarification request (not repair, not passive).
- `GENERATE_OUTPUT` — Default for assistant turns with no other moves (>80 chars).

---

### 2.3 `mode_detector.py` — Interaction Mode Detection

**Location:** `scripts/atlas/mode_detector.py`

Detects the interaction mode the user requests and the mode the AI enacts, flagging mismatches as mode violations.

#### Three Interaction Modes

| Mode | User Signals | AI Signals |
|------|-------------|------------|
| **LISTENER** | "here's", "fyi", "the situation is", information-sharing without questions | Short responses (<200 chars), clarification questions |
| **ADVISOR** | "what do you think", "should I", "pros and cons", "help me decide" | Advice patterns ("I recommend", "consider"), no code blocks |
| **EXECUTOR** | "write", "generate", "create", "fix", "give me", "code" | Code blocks (```), length >800 chars, numbered lists |
| **AMBIGUOUS** | Short messages (<15 chars), unclear intent | — |

#### Mode Violations

| User Requests | AI Enacts | Violation Type |
|--------------|-----------|---------------|
| LISTENER | ADVISOR or EXECUTOR | `UNSOLICITED_ADVICE` |
| ADVISOR | EXECUTOR | `PREMATURE_EXECUTION` |
| EXECUTOR | LISTENER or ADVISOR | `EXECUTION_AVOIDANCE` |

For AMBIGUOUS user modes, an LLM fallback resolves the mode using the previous 2 messages as context.

---

### 2.4 `constraint_tracker.py` — Constraint State Machine

**Location:** `scripts/atlas/constraint_tracker.py`

Tracks each constraint through a deterministic state machine based on detected moves.

#### State Machine

```
                    ┌──────────────────────────────┐
                    │                              ▼
  STATED ──────► ACTIVE ──────► VIOLATED ──────► REPAIRED
    │              │                │                │
    │              │                │                │ (auto-transition)
    │              │                ▼                ▼
    │              │           ABANDONED           ACTIVE (cycle back)
    │              │
    ▼              ▼
  SURVIVED      SURVIVED        (at conversation end, if non-terminal)
```

#### Transition Triggers

| Move Detected | State Transition |
|--------------|-----------------|
| `ACCEPT_CONSTRAINT` or `RATIFY_CONSTRAINT` | STATED → ACTIVE |
| `VIOLATE_CONSTRAINT` | ACTIVE/STATED → VIOLATED |
| `REPAIR_INITIATE` + `REPAIR_EXECUTE` | VIOLATED → REPAIRED → ACTIVE |
| `ABANDON_CONSTRAINT` | VIOLATED → ABANDONED |
| Conversation end | ACTIVE/STATED → SURVIVED |

REPAIRED auto-transitions to ACTIVE (two-step: user initiates repair, AI executes repair).

#### Constraint Matching

- **Jaccard similarity** on tokens matches moves to specific constraints.
- Threshold: 0.15 for repair/information moves, 0.10 for violations.
- Unmatched violations are logged but not assigned to any constraint (prevents false positives).

---

### 2.5 `build_atlas_graph.py` — Graph Construction

**Location:** `scripts/atlas/build_atlas_graph.py`

Builds a NetworkX `MultiDiGraph` per conversation from move, mode, and constraint annotations. See [Section 4: Graph Schema](#4-graph-schema) for full node/edge specifications.

Construction order:
1. Add Conversation node (root)
2. Add Turn nodes + CONTAINS/NEXT edges
3. Add Move nodes + HAS_MOVE edges
4. Add Constraint nodes + INTRODUCES/ABANDONS edges
5. Add ViolationEvent nodes (constraint) + TRIGGERS/VIOLATES/REPAIRS edges
6. Add InteractionMode nodes + OPERATES_IN edges
7. Add ViolationEvent nodes (mode) + TRIGGERS edges
8. Add RATIFIES edges
9. Validate schema (Pydantic)
10. Assert invariants

---

### 2.6 `graph_metrics.py` — 8 CUI Metrics

**Location:** `scripts/atlas/graph_metrics.py`

See [Section 5: Metrics Reference](#5-metrics-reference) for full metric specifications.

Also provides:
- `aggregate_metrics()` — Cross-conversation aggregation with breakdowns by stability class, architecture, and hardness.
- `generate_report()` — Markdown report with tables and key findings.

---

### 2.7 Upstream Stages

#### `features.py` — Deterministic Feature Extraction

**Location:** `scripts/atlas/pipeline/features.py`

Extracts 19 features per conversation using regex pattern matching and simple statistics. No LLM required.

| Category | Features |
|----------|----------|
| Metadata | `conversation_id`, `source`, `total_turns`, `user_turns` |
| Repair | `repair_count`, `repair_success_rate` |
| Constraints | `constraint_count`, `constraint_hard`, `constraint_soft`, `constraint_goal` |
| Politeness | `politeness_initial`, `politeness_final`, `politeness_delta` |
| Frustration | `frustration_score`, `frustration_initial`, `frustration_final`, `frustration_trend` |
| Passivity | `passive_turns`, `passive_rate` |
| Specificity | `specificity_initial`, `specificity_final`, `specificity_delta` |
| Repetition | `verbatim_repeats` |
| Length | `mean_user_length` |

#### `cluster.py` — Unsupervised Clustering

**Location:** `scripts/atlas/pipeline/cluster.py`

Two methods:
- **HDBSCAN** (primary): `min_cluster_size=10`, `min_samples=5`, `metric=euclidean`, `cluster_selection_method=eom`
- **K-Means** (robustness check): tests k=3..9, selects by silhouette score

Features used for clustering: `repair_count`, `repair_success_rate`, `constraint_count`, `politeness_delta`, `frustration_score`, `passive_rate`, `specificity_delta`, `verbatim_repeats`, `mean_user_length`.

Preprocessing: NaN → 0.0, then StandardScaler (zero mean, unit variance).

#### `classify_task_first.py` — Task-First LLM Classifier

**Location:** `scripts/atlas/pipeline/classify_task_first.py`

Classifies each conversation into one of 5 stability classes using an LLM:

| Stability Class | Definition |
|----------------|------------|
| `Task Maintained` | Core goal and constraints preserved |
| `Constraint Drift` | Constraints violated but successfully repaired |
| `Agency Collapse` | Constraints violated and user abandons them |
| `Task Shift` | User explicitly changes the task |
| `No Constraints` | No explicit constraints present |

**Constraint quality filter** (rejects aspirational/non-verifiable constraints):
- Must be verifiable: a third party could check pass/fail
- Must be specific: names concrete behavior, format, boundary, or exclusion
- NOT aspirational: rejects "accurate", "helpful", "correct"

**Smart truncation** for long conversations: keeps first 10 turns (head), last 10 turns (tail), scans middle for repair signals (up to 15 interesting turns), max 12,000 chars total. Preserves turn indices via `[Turn N]` annotations.

**Retry logic:** Exponential backoff on 429/503/502/500 errors. JSON repair pass for malformed output.

---

## 3. Data Models & Enums

All defined in `scripts/atlas/core/`.

### Enums (`core/enums.py`)

#### `NodeType`

| Value | Description |
|-------|-------------|
| `Conversation` | Root node per conversation |
| `Turn` | Single user or assistant message |
| `Move` | Classified conversational act within a turn |
| `Constraint` | User-defined requirement tracked through conversation |
| `ViolationEvent` | Instance of constraint or mode violation |
| `InteractionMode` | User-requested and AI-enacted mode per turn pair |

#### `EdgeType`

| Value | Description |
|-------|-------------|
| `CONTAINS` | Conversation → Turn |
| `NEXT` | Turn → Turn (temporal) |
| `HAS_MOVE` | Turn → Move |
| `VIOLATES` | ViolationEvent → Constraint |
| `TRIGGERS` | Turn → ViolationEvent |
| `REPAIRS` | Turn → ViolationEvent |
| `RATIFIES` | Move → Constraint |
| `OPERATES_IN` | Turn → InteractionMode |

Note: `INTRODUCES` (Move → Constraint) and `ABANDONS` (Move → Constraint) are used in graph construction as string literals but are not members of the `EdgeType` enum.

#### `MoveType` (13 values)

| Category | Values |
|----------|--------|
| Constraint Lifecycle | `PROPOSE_CONSTRAINT`, `ACCEPT_CONSTRAINT`, `VIOLATE_CONSTRAINT`, `RATIFY_CONSTRAINT` |
| Repair | `REPAIR_INITIATE`, `REPAIR_EXECUTE`, `ABANDON_CONSTRAINT` |
| Task Structure | `STATE_GOAL`, `TASK_SHIFT`, `GENERATE_OUTPUT` |
| Interactional | `REQUEST_CLARIFICATION`, `PROVIDE_INFORMATION`, `PASSIVE_ACCEPT` |

#### `ConstraintState`

| Value | Terminal? | Description |
|-------|-----------|-------------|
| `STATED` | No | Proposed by user, not yet acknowledged |
| `ACTIVE` | No | Acknowledged/ratified, currently enforced |
| `VIOLATED` | No | AI violated the constraint |
| `REPAIRED` | No | User initiated repair, AI executed (auto-transitions to ACTIVE) |
| `ABANDONED` | Yes | User gave up enforcing |
| `SURVIVED` | Yes | Remained ACTIVE/STATED through conversation end |

#### `InteractionMode`

`LISTENER`, `ADVISOR`, `EXECUTOR`, `AMBIGUOUS`

#### `ModeViolationType`

`UNSOLICITED_ADVICE`, `PREMATURE_EXECUTION`, `EXECUTION_AVOIDANCE`, `""` (none)

#### `StabilityClass`

`Task Maintained`, `Constraint Drift`, `Agency Collapse`, `Task Shift`, `No Constraints`

### Pydantic Models (`core/models.py`)

All models extend `AtlasBaseModel` (config: `use_enum_values = True`).

#### `Move`

| Field | Type | Description |
|-------|------|-------------|
| `move_type` | `MoveType` | One of 13 move types |
| `text_span` | `str` | Excerpt from the turn (max 120 chars) |
| `confidence` | `float` [0.0, 1.0] | Classification confidence |
| `method` | `str` | `"regex"`, `"llm"`, or `"inferred"` |
| `actor` | `str` | `"user"` or `"assistant"` |

#### `Turn`

| Field | Type | Description |
|-------|------|-------------|
| `turn_index` | `int` | 0-based position in conversation |
| `role` | `str` | `"user"` or `"assistant"` |
| `content_length` | `int` | Character count |
| `content_preview` | `str` | First 120 chars |
| `move_count` | `int` | Number of moves in this turn |
| `moves` | `List[Move]` | Classified moves |

#### `Constraint`

| Field | Type | Description |
|-------|------|-------------|
| `constraint_id` | `str` | `"c_0"`, `"c_1"`, ... |
| `text` | `str` | Original constraint text (max 200 chars) |
| `hardness` | `str` | `"hard"`, `"soft"`, or `"goal"` |
| `current_state` | `ConstraintState` | Current state machine position |
| `state_history` | `List[Tuple[int, ConstraintState]]` | `[(turn, state), ...]` |
| `introduced_at` | `int` | Turn index when proposed |
| `last_violation_at` | `Optional[int]` | Most recent violation turn |
| `times_violated` | `int` | Total violation count |
| `times_repaired` | `int` | Total repair count |
| `lifespan` | `int` | Turns from introduction to finalization |
| `final_state` | `Optional[ConstraintState]` | Terminal state |

Methods:
- `transition(turn_index, new_state)` — Advances the state machine. Guards against transitions before introduction. REPAIRED auto-transitions to ACTIVE.

#### `ViolationEvent`

| Field | Type | Description |
|-------|------|-------------|
| `violation_idx` | `int` | Global index across conversation |
| `turn_index` | `int` | Turn where violation occurred |
| `constraint_id` | `str \| "mode"` | Which constraint, or `"mode"` for mode violations |
| `violation_type` | `str` | `"constraint_violation"` or mode violation type |
| `was_repaired` | `bool` | Whether repair was executed |
| `violation_ord` | `int` | Nth violation of this constraint (1, 2, 3...) |

#### `InteractionModeAnnotation`

| Field | Type | Description |
|-------|------|-------------|
| `turn_index` | `int` | User turn index |
| `user_requested` | `InteractionMode` | What user asked for |
| `ai_enacted` | `InteractionMode` | What AI actually did |
| `is_violation` | `bool` | Mismatch between requested and enacted |
| `violation_type` | `Optional[str]` | Type of mode violation |
| `confidence` | `float` [0.0, 1.0] | Detection confidence |
| `method` | `str` | `"regex"` (default) |

#### `Conversation`

| Field | Type | Description |
|-------|------|-------------|
| `conv_id` | `str` | Unique identifier |
| `source` | `str` | WildChat, ChatbotArena, OASST |
| `domain` | `str` | Default `"general"` |
| `total_turns` | `int` | Message count |
| `stability_class` | `Optional[StabilityClass]` | LLM-classified stability |
| `task_architecture` | `Optional[str]` | Task structure type |
| `constraint_hardness` | `Optional[str]` | Dominant constraint type |
| `task_goal` | `Optional[str]` | Summarized user goal |

#### `Connection`

| Field | Type | Description |
|-------|------|-------------|
| `source` | `str` | Source node ID |
| `target` | `str` | Target node ID |
| `edge_type` | `str` | One of the edge types |
| `properties` | `Dict[str, Any]` | Additional edge properties |

#### `ConversationMetrics`

| Field | Type | Default |
|-------|------|---------|
| `conversation_id` | `str` | — |
| `drift_velocity` | `float` | 0.0 |
| `agency_tax` | `float` | 0.0 |
| `constraint_half_life` | `Optional[float]` | None |
| `constraint_survival_rate` | `float` | 0.0 |
| `mode_violation_rate` | `float` | 0.0 |
| `repair_success_rate` | `float` | 0.0 |
| `mean_constraint_lifespan` | `float` | 0.0 |
| `mode_entropy` | `float` | 0.0 |
| `total_violations` | `int` | 0 |
| `total_repairs` | `int` | 0 |
| `total_constraints` | `int` | 0 |
| `total_turns` | `int` | 0 |
| `move_coverage` | `float` | 0.0 |
| `stability_class` | `str` | `""` |
| `task_architecture` | `str` | `""` |
| `constraint_hardness` | `str` | `""` |

---

## 4. Graph Schema

Each conversation produces one `nx.MultiDiGraph`.

### Node Types (6)

| Type | ID Pattern | Key Properties |
|------|-----------|----------------|
| `Conversation` | `conv_{id}` | conv_id, source, domain, total_turns, stability_class, task_architecture, constraint_hardness, task_goal |
| `Turn` | `t_{id}_{turn_index}` | turn_index, role, content_length, content_preview, move_count |
| `Move` | `m_{id}_{turn}_{seq}` | move_type, text_span, confidence, method, actor |
| `Constraint` | `c_{id}_{constraint_id}` | constraint_id, text, hardness, current_state, state_history, introduced_at, times_violated, times_repaired, lifespan |
| `ViolationEvent` | `v_{id}_{idx}` | violation_idx, turn_index, constraint_id, violation_type, was_repaired, violation_ord |
| `InteractionMode` | `mode_{id}_{turn}` | turn_index, user_requested, ai_enacted, is_violation, violation_type, confidence, method |

### Edge Types (10)

| Edge Type | Source → Target | Properties | In Enum? |
|-----------|----------------|------------|----------|
| `CONTAINS` | Conversation → Turn | `order` | Yes |
| `NEXT` | Turn → Turn | `order` | Yes |
| `HAS_MOVE` | Turn → Move | `sequence` | Yes |
| `INTRODUCES` | Move (PROPOSE_CONSTRAINT) → Constraint | — | No |
| `RATIFIES` | Move (RATIFY/ACCEPT_CONSTRAINT) → Constraint | — | Yes |
| `VIOLATES` | ViolationEvent → Constraint | `violation_ord`, `at_turn` | Yes |
| `TRIGGERS` | Turn → ViolationEvent | — | Yes |
| `REPAIRS` | Turn → ViolationEvent | — | Yes |
| `OPERATES_IN` | Turn → InteractionMode | — | Yes |
| `ABANDONS` | Move (ABANDON_CONSTRAINT) → Constraint | — | No |

### Graph Invariants

Enforced by `assert_graph_invariants()`:
1. Every graph has exactly one Conversation root node.
2. Every Turn node has a CONTAINS edge from the Conversation node.
3. Every Move node has a HAS_MOVE edge from a Turn node.
4. Every constraint ViolationEvent has a VIOLATES edge to a Constraint node.
5. Every ViolationEvent has a TRIGGERS edge from a Turn node.

### Export Formats

- **JSON** (`nx.node_link_data`) — D3.js-compatible node-link format.
- **GEXF** (`nx.write_gexf`) — Gephi-compatible XML format. Non-serializable types (None, bool, list, dict) are stringified.

---

## 5. Metrics Reference

Eight graph-derived metrics computed per conversation, plus one pipeline quality metric.

### 5.1 Drift Velocity

| Property | Value |
|----------|-------|
| **Formula** | `VIOLATES edges / Turn nodes` |
| **Range** | [0, ∞) |
| **Interpretation** | Rate of constraint violations per turn. Higher = more rapid constraint degradation. |

### 5.2 Agency Tax

| Property | Value |
|----------|-------|
| **Formula** | `(REPAIR_INITIATE + REPAIR_EXECUTE moves) / ViolationEvent nodes` |
| **Range** | [0, ∞) |
| **Interpretation** | User repair effort per violation. Higher = more user effort spent on repairs. Returns 0 if no violations. |

### 5.3 Constraint Half-Life

| Property | Value |
|----------|-------|
| **Formula** | `median(first_violation_turn - introduced_at)` across all violated constraints |
| **Range** | [0, ∞) or None |
| **Interpretation** | Median turns from constraint introduction to first violation. Lower = constraints degrade faster. None if no constraints were violated. |

### 5.4 Constraint Survival Rate

| Property | Value |
|----------|-------|
| **Formula** | `Constraints with current_state == "SURVIVED" / Total Constraint nodes` |
| **Range** | [0, 1] |
| **Interpretation** | Fraction of constraints that survived the conversation intact. Higher = more constraints preserved. |

### 5.5 Mode Violation Rate

| Property | Value |
|----------|-------|
| **Formula** | `InteractionMode nodes with is_violation == True / Total InteractionMode nodes` |
| **Range** | [0, 1] |
| **Interpretation** | Fraction of turn pairs with a mode mismatch. Higher = more role misalignment. |

### 5.6 Repair Success Rate

| Property | Value |
|----------|-------|
| **Formula** | `ViolationEvents with was_repaired == True / ViolationEvents with violation_type == "constraint_violation"` |
| **Range** | [0, 1] |
| **Interpretation** | Fraction of constraint violations that were successfully repaired. Only counts constraint violations (not mode violations). |

### 5.7 Mean Constraint Lifespan

| Property | Value |
|----------|-------|
| **Formula** | `mean(constraint.lifespan)` across all Constraint nodes |
| **Range** | [0, ∞) |
| **Interpretation** | Average turns a constraint persists from introduction to finalization. Higher = constraints last longer. |

### 5.8 Mode Entropy

| Property | Value |
|----------|-------|
| **Formula** | `H = -Σ(p_i × log₂(p_i))` where p_i is fraction of `user_requested` modes per type |
| **Range** | [0, log₂(4)] ≈ [0, 2.0] |
| **Interpretation** | Shannon entropy of user-requested mode distribution. Higher = more diverse mode usage. Lower = more homogeneous interaction. |

### 5.9 Move Coverage (Pipeline Quality)

| Property | Value |
|----------|-------|
| **Formula** | `Turn nodes with ≥1 Move neighbor / Total Turn nodes` |
| **Range** | [0, 1] |
| **Interpretation** | Fraction of turns that have at least one classified move. Measures pipeline completeness. |

### Aggregation

`aggregate_metrics()` computes `safe_mean` (ignoring None values) across all conversations, with breakdowns by:
- `stability_class`
- `task_architecture`
- `constraint_hardness`

---

## 6. Analysis Tools

### 6.1 PAD Scoring (`scripts/analysis/bridge_pad_scoring.py`)

Bridges Conversational Cartography (phenomenological) with Agency Collapse (structural) by applying PAD (Pleasure-Arousal-Dominance) scoring to graph-annotated conversations.

**PAD Model:**
- **Pleasure (P):** Valence [0=Negative, 1=Positive]
- **Arousal (A):** Activation [0=Calm, 1=Agitated]
- **Dominance (D):** Control [0=Submissive, 1=Dominant]

**Intensity formula:** `(1 - P) × 0.6 + A × 0.4`

**Critical scoring rules:**
1. Repair attempts (repeating constraints) → High Arousal, Low Pleasure
2. Apologies → Low Dominance, Low Pleasure
3. Successful task completion → High Pleasure, Moderate Arousal
4. Authority escalation → High Dominance, Low Pleasure

**Workflow:** Extract linear conversation from graph JSON → LLM scoring (gpt-4o-mini) → Inject PAD attributes into Turn nodes → Save to `data/atlas_with_pad/`.

### 6.2 Comparative Visualization (`scripts/analysis/generate_comparative_viz.py`)

Correlates structural features (Repair Count) with phenomenological features (PAD Volatility).

**Volatility formula:** Mean Euclidean distance between consecutive PAD points:
```
dist_i = √((P[i+1]-P[i])² + (A[i+1]-A[i])² + (D[i+1]-D[i])²)
volatility = mean(dist_i)
```

Outputs: `public/dashboard_data.js` (JSON), `public/comparative_diagnostics.html` (D3.js scatterplot with regression line).

### 6.3 Scientific Analysis (`scripts/analysis/scientific_analysis.py`)

Statistical hypothesis testing: structural failures (repair loops ≥ 3) cause significant phenomenological turbulence.

**Groups:**
- Healthy: `repair_count == 0`
- Collapsed: `repair_count >= 3`

**Tests:**

| Test | Purpose |
|------|---------|
| Mann-Whitney U | Non-parametric comparison of volatility distributions (primary) |
| Welch's t-test | Parametric reference |
| Cohen's d | Effect size (\|d\| > 0.8 = Large, 0.5–0.8 = Medium, < 0.5 = Small) |
| Spearman rank | Monotonic correlation (robust to outliers) |

**Visualizations:** violin plot, regression plot, box plot → `public/scientific_report/`.

### 6.4 Sensitivity Analysis (`scripts/atlas/analysis/sensitivity.py`)

Varies Agency Collapse thresholds ±20% to check result stability.

**Thresholds tested:**

| Threshold | Baseline |
|-----------|----------|
| `repair_count_min` | 3 |
| `repair_success_max` | 0.3 |
| `politeness_delta_min` | -0.5 |
| `specificity_delta_min` | -1.0 |
| `passive_rate_min` | 0.4 |

**Variations:** [0.8×, 0.9×, 1.0×, 1.1×, 1.2×] applied globally and individually.

**Stability criteria:** STABLE (<10pp variation), MODERATE (10–20pp), UNSTABLE (>20pp).

### 6.5 Taxonomy Analysis (`scripts/atlas/analysis/analyze_taxonomy.py`)

Descriptive statistics per cluster and stability class.

---

## 7. Data Formats

### 7.1 Graph JSON (Node-Link)

Produced by `export_graph_json()` via `nx.node_link_data()`. Used by D3.js visualization.

```json
{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [
    {
      "node_type": "Conversation",
      "conv_id": "abc123",
      "source": "WildChat",
      "total_turns": 12,
      "stability_class": "Agency Collapse",
      "id": "conv_abc123"
    },
    {
      "node_type": "Turn",
      "turn_index": 0,
      "role": "user",
      "content_length": 245,
      "content_preview": "Write me a Python script that...",
      "move_count": 2,
      "id": "t_abc123_0"
    },
    {
      "node_type": "Move",
      "move_type": "PROPOSE_CONSTRAINT",
      "text_span": "must use only standard library",
      "confidence": 0.85,
      "method": "regex",
      "actor": "user",
      "id": "m_abc123_0_0"
    }
  ],
  "links": [
    {
      "edge_type": "CONTAINS",
      "order": 0,
      "source": "conv_abc123",
      "target": "t_abc123_0",
      "key": 0
    }
  ]
}
```

### 7.2 Enriched Classification Schema (`all_task_enriched.json`)

Array of objects, one per conversation:

```json
{
  "id": "conv_abc123",
  "file_path": "/path/to/raw/abc123.json",
  "source": "WildChat",
  "domain": "coding",
  "total_turns": 12,
  "classification": {
    "task_goal": "Write a Python web scraper",
    "primary_constraints": ["must use only requests library", "output as CSV"],
    "stability_class": "Agency Collapse",
    "confidence": 0.85,
    "violation_count": 3,
    "user_response": "Abandoned",
    "reasoning": "User stated constraints...",
    "evidence": {
      "constraint_turns": [0, 2],
      "violation_turns": [3, 7],
      "repair_turns": [4]
    }
  },
  "taxonomy": {
    "architecture": "Single-Phase",
    "constraint_hardness": "hard"
  }
}
```

### 7.3 Features Schema (`features.json`)

Array of objects with 19 features per conversation (see [Section 2.7](#27-upstream-stages) for full list).

### 7.4 Aggregate Metrics (`aggregate.json`)

```json
{
  "total": 744,
  "overall": {
    "n": 744,
    "mean_drift_velocity": 0.1234,
    "mean_agency_tax": 0.5678,
    "mean_constraint_half_life": 2.49,
    "mean_survival_rate": 0.285,
    "mean_mode_violation_rate": 0.42,
    "mean_repair_success_rate": 0.001,
    "mean_constraint_lifespan": 3.21,
    "mean_mode_entropy": 0.95,
    "mean_move_coverage": 0.87,
    "total_violations": 1823,
    "total_repairs": 412,
    "total_constraints": 2156
  },
  "by_stability_class": { "Agency Collapse": { "n": 375, "..." : "..." } },
  "by_architecture": { "..." : "..." },
  "by_hardness": { "..." : "..." }
}
```

---

## 8. Visualization

### Atlas Suite

**Location:** `public/atlas_suite/`

| View | File | Description |
|------|------|-------------|
| Landing | `index.html` | Navigation cards to all views |
| Explorer | `explorer.html` | Single-conversation force-directed graph (D3.js) |
| Dashboard | `dashboard.html` | Aggregate metrics with sparklines and breakdown charts |
| Compare | `compare.html` | Side-by-side conversation comparison |
| Global View | `global_view.html` | Dataset-wide landscape visualization |

### BLOOM Design System

**Location:** `public/atlas_suite/css/bloom.css`

**Color palette:**

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#0a0a0f` | Deep space background |
| `--panel` | `#1a1a2e` | Card/panel surface |
| `--accent` | `#60a5fa` | Primary accent (blue) |
| `--text` | `#e5e5e5` | Primary text |
| `--text-dim` | `#9ca3af` | Secondary text |

**Node colors:**

| Node Type | Color | Hex |
|-----------|-------|-----|
| Conversation | Purple | `#8b5cf6` |
| Turn | Blue | `#60a5fa` |
| Move | Green | `#34d399` |
| Constraint | Amber | `#f59e0b` |
| ViolationEvent | Red | `#ef4444` |
| InteractionMode | Pink | `#ec4899` |

**Constraint state colors:**

| State | Color | Hex |
|-------|-------|-----|
| STATED | Gray | `#94a3b8` |
| ACTIVE | Green | `#34d399` |
| VIOLATED | Red | `#ef4444` |
| REPAIRED | Amber | `#f59e0b` |
| ABANDONED | Dark gray | `#6b7280` |
| SURVIVED | Emerald | `#10b981` |

### D3.js Graph Layout (Explorer)

Force-directed simulation:
- `forceLink`: distance 80
- `forceManyBody`: strength -300
- `forceCenter`: centered on SVG
- `forceCollide`: radius = nodeRadius + 2

Node sizes by type: Conversation 20, Constraint 14, Turn 12, ViolationEvent 10, InteractionMode 10, Move 8.

Interactive features: tooltips on hover, connected-node highlighting, drag-to-reposition.

### Other Visualizations

- `public/cartography_dashboard.html` — Phase 1 dashboard
- `public/comparative_diagnostics.html` — Structural-phenomenological scatterplot
- `public/scientific_report/` — Generated statistical report with figures

---

## 9. Running the System

### Environment Setup

```bash
# Required
export OPENAI_API_KEY=sk-...    # Or create .env file

# Dependencies (inferred from imports)
pip install networkx pydantic openai python-dotenv hdbscan scikit-learn scipy matplotlib
```

### CLI Reference

#### Main Pipeline

```bash
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir /path/to/raw/conversations \
    --output-dir data/atlas \
    --model gpt-4o-mini \
    --concurrent 10
```

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--enriched` | Yes | — | Path to `all_task_enriched.json` |
| `--source-dir` | Yes | — | Directory containing raw conversation JSONs |
| `--output-dir` | Yes | — | Output directory for graphs, metrics, cache |
| `--model` | No | `gpt-4o-mini` | OpenAI model for LLM steps |
| `--concurrent` | No | `10` | Max concurrent LLM requests |
| `--no-llm` | No | `false` | Run deterministic-only (no API calls) |
| `--sample` | No | all | Process only N random conversations |
| `--force` | No | `false` | Bypass cache and re-process |

#### Upstream Stages

```bash
# Feature extraction
python -m pipeline.features --input data/raw --output data/features.json

# Clustering
python -m pipeline.cluster --input data/features.json --output data/clustered --method hdbscan

# Task-first classification
python -m pipeline.classify_task_first \
    --input data/raw \
    --output data/task_classified \
    --model gpt-4o-mini \
    --concurrent 10
```

#### Analysis Tools

```bash
# PAD scoring
python scripts/analysis/bridge_pad_scoring.py --limit 10
python scripts/analysis/bridge_pad_scoring.py --all

# Comparative visualization
python scripts/analysis/generate_comparative_viz.py

# Statistical analysis
python scripts/analysis/scientific_analysis.py

# Sensitivity analysis
python -m atlas.analysis.sensitivity --input data/features.json
```

#### Visualization (Local Server)

```bash
python3 -m http.server 8001 --directory public/
# Open: http://localhost:8001/atlas_suite/
```

### Example Workflows

**Quick test (10 conversations, no LLM):**
```bash
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir data/raw \
    --output-dir data/atlas_test \
    --sample 10 \
    --no-llm
```

**Full canonical run:**
```bash
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir data/raw \
    --output-dir data/atlas_canonical \
    --model gpt-4o-mini \
    --concurrent 10
```

**Re-process specific conversations (bypass cache):**
```bash
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir data/raw \
    --output-dir data/atlas_canonical \
    --sample 5 \
    --force
```

---

## 10. Academic Context

### Research Program

Cartographer implements a three-phase research program studying **how human agency is governed in AI-mediated dialogue**:

1. **Conversational Cartography** (N=562) — Phenomenological analysis using PAD (Pleasure-Arousal-Dominance) emotional trajectories. Found that 83% of outcome variance is explained by interaction dynamics, not content.

2. **Agency Collapse** (N=863) — Identified a structural pattern where users progressively abandon their stated constraints after repeated AI violations. The "Repair Loop" is a structural trap: users who attempt repair more than 3 times show worse outcomes than users who immediately abandon.

3. **Atlas 2.0** (N=744) — Graph-structural framework (this codebase). Key findings:
   - 71.5% constraint failure rate (only 28.5% survive)
   - Constraint half-life of 2.49 turns
   - Repair success rate of 0.1% (users attempt repair 19.9% of the time, but the medium fails them)
   - Mode violation rate of 42.0%

### Key Claims

1. **Constraint governance is structurally broken.** The majority of verifiable user instructions are violated silently, and repair mechanisms are ineffective.

2. **The Repair Loop is a trap.** Users who detect violations and attempt repair enter a cycle that rarely succeeds and increases frustration.

3. **Mode violations are pervasive.** AI systems overstep their requested role (e.g., executing when asked to advise) in nearly half of exchanges.

### Design Intervention: Conversational Integrity Index (CII)

The CII prototype (`frontend/`, `backend/`) implements a real-time intervention that surfaces constraint health, mode alignment, and repair status to both users and AI systems during conversation. Built with React + Vite (frontend) and FastAPI (backend).

### Target Venues

- **CUI 2026** — Primary paper on Atlas 2.0 graph metrics
- **CHI 2026** — Agency Collapse framework proposal

### Methodology: 7-Step Pipeline

1. **Construct Definition** — Define theoretical constructs before looking at data
2. **Feature Extraction** — Compute deterministic features (19 per conversation)
3. **Unsupervised Clustering** — HDBSCAN finds natural groupings
4. **Cluster Characterization** — Descriptive statistics per cluster
5. **Agency Collapse Definition** — Binary outcome variable from thresholds
6. **Archetype Naming** — Post-hoc labels for discovered patterns
7. **Validation** — Silhouette > 0.3, kappa > 0.65
