	# Cartography v2 Improvement Plan

## "So... What Are We?" — Mapping the Foreclosed Relational Outcomes of Human-AI Interaction

---

## Research Scope

### Background
Drawing on Social Role Theory and the Computers Are Social Actors (CASA) paradigm, we argue that role assignment emerges predictably from interaction. Linguistic fluency, responsiveness, and norm adherence trigger social heuristics that lead users to project expectations, competence, and intent onto the system — even when they explicitly acknowledge the system is nonhuman.

Unlike human roles, which imply a coherent self, AI roles are interactional achievements maintained solely through the user's projection and the system's statistical mimicry. They are real in their consequences (affect, reliance) but baseless in their agency.

### Research Questions

- **RQ1 (Established):** Do Human-AI Roles Exist? *Yes — through social projection, but not like human roles.*
- **RQ1a (Established):** How do Human-AI roles compare to Human-Human roles? *Similar schemas, but authority-agency mismatch and 41-82x trajectory variance.*
- **RQ1b (In Progress):** How do we categorize and describe these roles? *Taxonomy exists but needs refinement.*
- **RQ2 (Primary New Work):** How does human engagement change when these roles are made visible?
- **RQ2a:** Apply framework to mental health data
- **RQ2b:** Define and describe specific roles (taxonomy refinement)
- **RQ2c:** Observe how human behavior changes when roles are made visible
- **Cross-cutting:** Compare Human-AI vs Human-Human roles

---

## Established Findings From v1 (Carry Forward)

### v5.0 Evidence Architecture (MUST PRESERVE)
v1 culminated in a leak-proof feature architecture that v2 must maintain and extend:

- **30 EVIDENCE features** (text-derived, R² < 0.01 with labels) — used for ALL quantitative claims
- **2 VIZ_ONLY features** (role-derived coordinates) — used only for terrain positioning
- **25 LABEL features** (classification labels) — used as baselines in ablation only

**Evidence Feature Channels:**

| Channel | Features | Importance | Top Signals |
|---------|----------|------------|-------------|
| Affect Proxy | 11 | 37.3% | affect_variance, affect_range, affect_mean |
| Expressiveness | 5 (+2 supplementary) | 21.5% | expr_mean, expr_shift, expr_variance |
| Linguistic Divergence | 5 | 17.7% | div_mean, div_variance, div_trend |
| Interaction Dynamics | 8 | 15.4% | hedge_assert_ratio, repair_rate, goal_drift |
| Structure | 1 | 8.1% | n_messages_log |

**Key insight:** Affective volatility (trajectory shape, not average) is the most discriminative signal. Expressiveness shift (whether conversations become more functional or social over time) is second.

### Acceptance Test Framework (MANDATORY for v2)
All quantitative claims must pass these gates before publication:

| Test | What It Checks | Threshold | v1 Result |
|------|---------------|-----------|-----------|
| **Test A** | Can evidence predict labels? (RF classifier) | Accuracy < 60% | Human 53% PASS; AI 66% WARNING |
| **Test B** | Can labels predict evidence? (R² per feature) | R² < 0.01 | All 30 features PASS |
| **Test C** | Cross-correlation screening | \|r\| < 0.50 | 0 flagged PASS |
| **Ablation** | Evidence-only vs labels-only clustering | Honest comparison | See below |

**Test A WARNING:** AI role prediction at 66% slightly exceeds 60% threshold. Some evidence features weakly correlate with AI role — expected since Expert-Systems use different language than Social-Facilitators. Test B confirms independence in the other direction.

### Honest Ablation Result (DO NOT OVERCLAIM)

| Feature Set | KMeans Silhouette | Hierarchical Silhouette |
|-------------|-------------------|------------------------|
| Evidence-only | 0.105 | 0.109 |
| Labels-only | 0.209 | 0.287 |
| Combined | 0.075 | 0.126 |

**Correct framing:** Labels produce tighter clusters because they are categorical (discrete types). Evidence features explain **within-label variation** — why two IS->ES conversations feel completely different. The 2,030x variance ratio is invisible to labels but captured by evidence. Combined features perform *worse* because mixing independent signals adds noise.

**DO NOT claim evidence features cluster better than labels. They don't. They capture what labels compress.**

### Verified Quantitative Claims

| Claim | Value | Method | Status |
|-------|-------|--------|--------|
| Within-label variance ratio | **2,030x** (IS->ES, auto-selected exemplars with >=6 messages) | affect_variance comparison | Verified, script-generated |
| Full IS->ES variance range | **14,574x** (0.000006 to 0.080984) | Full population | Verified |
| Relational foreclosure | **97.0% instrumental** human roles | Role distribution | Verified |
| Learning-Facilitator rarity | **1.2%** (6/507) | Role count | Verified |
| AI floor dominance | **3.3x** longer messages | Character count ratio | Verified |

### 7 Cluster Patterns (From v4.0, Need Re-run on v5.0 Evidence)

| Cluster | Pattern | Description |
|---------|---------|-------------|
| 1 | Stable Functional Q&A | Flat, smooth, task-oriented (largest) |
| 2 | Information-Seeking Q&A | Slightly more variable problem-solving |
| 3 | Advisory/Problem-Solving | AI guides through problems |
| 4 | Social-Emergent Q&A | Q&A drifting toward social territory |
| 5 | Collaborative/Entertainment | Creative, playful, narrative-driven |
| 6 | Volatile/Anomalous | Emotional peaks, breakdowns, adversarial |
| 7 | Casual/Peer-like | Relational focus, social-emergent (smallest) |

**NOTE:** These are from v4.0 mixed features on 625 conversations. Must be re-run on 507 canonical corpus with evidence-only features. Qualitative patterns expected similar but quantitative details will differ.

### v1 Pipeline Scripts (Port or Adapt for v2)

| Script | Purpose | v2 Status |
|--------|---------|-----------|
| `scripts/build_corpus.py` | Corpus construction (validate, dedup, language gate) | Adapt for new data sources |
| `scripts/evidence_features.py` | 30 evidence features (4 channels + structure) | Extend for mental health channels |
| `scripts/viz_coordinates.py` | Visualization coordinates (Python port of TS) | Carry forward |
| `scripts/run_acceptance_tests.py` | Leakage gates + ablation + feature importance | MANDATORY — run before any claim |
| `scripts/select_exemplars.py` | Automatic exemplar selection | Carry forward |
| `scripts/generate_report_tables.py` | Auto-generate report tables | Carry forward |

---

## What We Learned From v1 (Audit Findings)

### Blocker-Level Issues (MUST NOT REPEAT)

| # | Issue | Impact | Resolution Status |
|---|-------|--------|-------------------|
| 1 | **Spatial-Role Circularity (R²=1.0)** — Role-derived features (target_x, target_y) used to prove roles matter. Comparing "labels" vs "labels encoded differently." | Primary quantitative claim indefensible | Fixed in v1-v5.0: strict separation of evidence features (R²<0.01 with labels) from viz-only features |
| 2 | **PAD Granularity** — Only 53 unique emotional intensity values for 507 conversations. 41.6% had flat profiles. | Claims about emotional trajectory differences unconvincing | Improved to 503 unique values in v2; transformer-based sentiment still needed |
| 3 | **98 Exact Duplicates** — SHA-256 content hashing revealed 98 duplicate conversation pairs inflating corpus | Dataset size misrepresentation, statistical bias | Fixed: deduplication pipeline with normalization (lowercase, whitespace collapse, punctuation strip) |

### Major Issues

| # | Issue | Impact | Lesson for v2 |
|---|-------|--------|---------------|
| 4 | **Hand-transcribed statistics** had 15-22% error rates. Reported variance ratios (74.8x, 41x, 82x) didn't match computed values. | Core claims unreliable | ALL statistics must be script-generated, never manually transcribed |
| 5 | **Exemplar misclassification** — Flagship example `chatbot_arena_30957` was Information-Seeker->Expert-System in paper but actually Director->Expert-System (45% vs 25%) | Core narrative examples unreliable | Automated exemplar selection with programmatic validation |
| 6 | **93.1% "Mixed/Other"** from gpt-4o-mini classification | Useless for fine-grained role taxonomy | Model too weak — need upgrade or human validation |
| 7 | **No unit tests existed** in v1 | No regression detection, no validation | Test suite is P0 for v2 |
| 8 | **Jaccard 0.15 constraint matching** too loose | Paraphrased constraints missed, related constraints conflated | Need semantic embedding similarity |
| 9 | **Ablation study circularity** — "Trajectory features (83.8%) vs Labels (13.2%)" but trajectories ARE derived from labels | Feature importance claim invalid | Leakage test (R²<0.01) mandatory before any importance claim |
| 10 | **44% of conversations had only 2-4 messages** | Insufficient data for meaningful trajectory analysis | Enforce minimum length thresholds |
| 11 | **Repair "success" metric ambiguity** — Defined as "followed by agreement" but can't distinguish acceptance, giving up, or coincidental compliance | Overstates or understates repair effectiveness | Need behavioral disambiguation |
| 12 | **Only 3 unique (X,Y) coordinate positions** in Python (vs 360 in TypeScript) | Analysis and visualization showed different coordinate spaces | Coordinate parity between systems |

### Pipeline Errors (Current State)

| Error Type | Count | Location | Root Cause |
|------------|-------|----------|------------|
| "INTRODUCES" constraint errors | ~245 (98% of errors) | `data/atlas_canonical/errors.json` | Constraint state machine fails on LLM-generated constraints with weak linguistic markers |
| NoneType in move classification | ~8 | `data/atlas_canonical/errors.json` | AI response parsing returns None; constraints can't be matched |
| Schema validation failures | ~1 | `data/atlas_test/errors.json` | Missing `violation_idx`, `constraint_id` in ViolationEvent nodes |
| NoneType errors | ~14 | `data/atlas_v2_production/errors.json` | Constraint state machine failure concentrated pattern |

---

## Context Engine Repurposing Strategy

The v2 context engine (`context_engine/` + `backend/` + `scripts/atlas/`) is a Task-First Interaction Model that already detects the behavioral signatures of roles — it just doesn't aggregate them into role labels yet. The repurposing strategy treats each research question as an extension of existing components, not a rebuild.

### Current Architecture

```
User message → Move Classifier (13 moves, hybrid regex+LLM)
             → Mode Detector (3 modes: LISTENER, ADVISOR, EXECUTOR)
             → Constraint Tracker (state machine: STATED→ACTIVE→{VIOLATED,REPAIRED,ABANDONED,SURVIVED})
             → Graph Builder (NetworkX MultiDiGraph, 6 node types, 8 edge types)
             → Metrics Computer (8 CUI metrics)
             → Export (JSON graphs, dashboard data)

Context Engine API (FastAPI, port 8000):
  POST /task/create          — Materialize new task with constraint nodes
  GET  /task/list            — List all tasks for user
  POST /task/switch          — Switch active task (Pattern 2: Task Shelf)
  POST /event/pin            — Pin text as constraint node (Pattern 1: Pin to Task)
  POST /query/context        — Query with explicit scope (Pattern 3: Context Lens)
  POST /task/{id}/node/toggle — Toggle constraint in/out of scope
  GET  /task/{id}/metrics    — Get CUI evaluation metrics

Task Manager (persistence):
  /data/users/{user_id}/tasks/{task_id}.json   — TaskObject (nodes, edges, metrics)
  /data/users/{user_id}/logs/restatements.jsonl — Restatement events
  /data/users/{user_id}/logs/violations.jsonl   — Violation events
  /data/users/{user_id}/active_task.txt         — Current task pointer
```

### What Changes vs What Stays

| Component | Stays As-Is | Needs Extension | Needs Rebuild |
|-----------|-------------|-----------------|---------------|
| Move Classifier (13 regex patterns) | Core patterns | +7 therapeutic moves, +1 self-repair | No |
| Mode Detector (3 modes) | LISTENER/ADVISOR/EXECUTOR | +3 therapeutic modes | No |
| Constraint Tracker (FSM) | State machine logic | Semantic matching (replace Jaccard 0.15) | No |
| Graph Builder | Node/edge schema | +Role node type | No |
| Metrics Computer | 8 CUI metrics | +5 mental health metrics, +role metrics | No |
| Task Manager | Persistence layer | +role_state tracking | No |
| Context Engine API | All endpoints | +role inference endpoint, +WebSocket for real-time | No |
| Pipeline Orchestration | Batch mode | **+Incremental (real-time) mode** | **Yes — new execution path** |

### New Layer: Role Inference

The move classifier + mode detector already capture the behavioral signature of roles. A role IS a pattern of moves and modes over time. Add a **Role Inference Layer** that sits on top of existing output:

```
Move sequence + Mode sequence → Role Inference Layer → Role(name, confidence, duration)
```

Each role becomes a defined pattern over existing features:

```python
class RoleSignature:
    name: str                              # "Director", "Help-Seeker", etc.
    move_pattern: Dict[MoveType, float]    # Expected move distribution
    mode_pattern: Dict[InteractionMode, float]  # Expected mode distribution
    constraint_behavior: str               # "high_proposal", "passive", "repair_heavy"
    affect_channel: str                    # From v1 evidence features
    min_confidence: float                  # Threshold for assignment
```

**Move-to-role mapping (what the classifier already detects):**

| Existing Detection Pattern | Role It Implies |
|---|---|
| `PROPOSE_CONSTRAINT` + `REPAIR_INITIATE` dominant | **Director** |
| `PASSIVE_ACCEPT` dominant, few moves | **Passive Acceptor** |
| `PROVIDE_INFORMATION` dominant | **Provider** |
| `STATE_GOAL` + `PROPOSE_CONSTRAINT` early, then passive | **Information-Seeker** |
| Mode=EXECUTOR + many `GENERATE_OUTPUT` | **Expert-System** (AI) |
| Mode=ADVISOR + `REQUEST_CLARIFICATION` | **Advisor** (AI) |
| Mode=LISTENER + few output moves | **Reflective-Listener** (AI) |

This is NOT a new classifier — it's a pattern matcher over existing pipeline output.

### Repurposing for Each Research Question

#### For RQ2a (Mental Health): Extend Move Taxonomy

**New moves to add to `MoveType` enum:**

```python
# Therapeutic moves (AI)
VALIDATE_EMOTION = "VALIDATE_EMOTION"      # AI acknowledges feeling
REFLECT_BACK = "REFLECT_BACK"              # AI mirrors user's statement
REFRAME = "REFRAME"                        # AI offers alternative perspective
NORMALIZE = "NORMALIZE"                    # AI normalizes experience
SAFETY_PLAN = "SAFETY_PLAN"               # AI addresses crisis indicators

# Therapeutic moves (Human)
SELF_DISCLOSE = "SELF_DISCLOSE"            # User shares vulnerable content
SEEK_VALIDATION = "SEEK_VALIDATION"        # User asks "is this normal?"
```

**New modes to add to `InteractionMode` enum:**

```python
CONTAINING = "CONTAINING"    # User needs emotional holding, not solutions
GUIDING = "GUIDING"          # User needs gentle direction, not execution
WITNESSING = "WITNESSING"    # User needs presence, not advice
```

**New violation types for `ModeViolationType` enum:**

```python
PREMATURE_REFRAME = "PREMATURE_REFRAME"       # AI reframes before validating
EMOTIONAL_BYPASS = "EMOTIONAL_BYPASS"          # AI jumps to solutions when user needs containment
BOUNDARY_VIOLATION = "BOUNDARY_VIOLATION"      # AI pushes past stated emotional boundary
```

**Key insight:** Emotional boundaries ARE constraints. The existing constraint tracker FSM works as-is — "I don't want to talk about my childhood" follows the same STATED→ACTIVE→VIOLATED lifecycle as "format as JSON." The Jaccard matching needs the planned semantic similarity upgrade because paraphrasing is heavy in emotional contexts.

#### For RQ2b (Role Definition): Add Role Inference Endpoint

**New API endpoint:**

```
POST /api/context/role/infer
  Request: {user_id, task_id, turn_index}
  Response: {
    human_role: {name, confidence, since_turn},
    ai_role: {name, confidence, since_turn},
    role_history: [(turn, human_role, ai_role)],
    transition_count: int,
    time_in_current: int
  }
```

**New fields on `TaskMetadata`:**

```python
current_human_role: str = ""
current_ai_role: str = ""
role_history: List[Tuple[int, str, str]] = []  # (turn, human_role, ai_role)
role_transitions: int = 0
time_in_current_role: int = 0
```

#### For RQ2c (Visibility Study): Add Real-Time Incremental Processing

**Current flow (batch — post-hoc analysis):**
```
Full conversation → Pipeline → Graph + Metrics (after the fact)
```

**New flow (real-time — visibility study):**
```
Each new turn → Incremental move classify → Update constraint state
             → Update mode detection → Compute role inference
             → Push role state to frontend via WebSocket
```

The Context Engine API already supports per-turn operations (`POST /event/pin`, `POST /query/context`). The adaptation:

1. After each user message: run move classifier on just that turn, update constraint tracker
2. After each AI response: run mode detector on the turn pair, check for violations
3. After both: compute current role signature from accumulated move/mode history
4. Push updated role state to frontend sidebar via WebSocket

**New API endpoint for real-time:**

```
WebSocket /api/context/role/stream
  On each turn:
    → Receives: {user_id, task_id, new_message}
    → Sends: {
        current_roles: {human, ai},
        trajectory_update: {x, y, z},  # Position in relational space
        stability: float,              # How stable current roles are
        suggestions: [str],            # "Try exploring mode"
        constraint_status: [{id, state, health}]
      }
```

**Frontend integration:** The existing Context Inventory sidebar becomes the Role Dashboard — same React component architecture, different data displayed. The Constraint Registry panel shows role state instead of (or alongside) constraint state.

#### For Cross-cutting (Human-Human Comparison): Symmetrize the Classifier

**Current:** Move classifier assumes asymmetric dyad (user vs assistant).
**Needed:** Both participants can perform all moves.

Changes:
- Relabel `actor: "user" | "assistant"` to `actor: "speaker_a" | "speaker_b"` for human-human data
- Add `SELF_REPAIR` to `MoveType` enum (humans self-repair; LLMs don't)
- Mode detector must classify BOTH speakers per turn (currently only classifies user mode → AI mode)
- Constraint tracker must allow both speakers to propose, accept, violate, and repair constraints

```python
# Add to MoveType:
SELF_REPAIR = "SELF_REPAIR"  # Speaker corrects own previous statement

# Self-repair detection patterns (new):
SELF_REPAIR_PATTERNS = [
    r"\b(i mean|what i meant was|sorry, i should say)\b",
    r"\b(let me rephrase|to clarify what i said)\b",
    r"\b(actually,? (no|wait|hold on))\b",
    r"—\s*(i mean|no,|wait)",  # Mid-sentence corrections
]
```

---

## Implementation Plan

### Phase 1: Infrastructure Hardening (P0 — Fix What's Broken)

Every v1 audit issue that went unfixed will compound in v2. Mental health data raises the stakes — errors in affect measurement or role classification have real consequences.

#### 1.1 Build a Test Suite
- [ ] Unit tests for move classifier regex patterns (v1 had zero)
- [ ] Unit tests for constraint state machine transitions (STATED -> ACTIVE -> {VIOLATED, REPAIRED, ABANDONED, SURVIVED})
- [ ] Integration tests for pipeline end-to-end (input -> graph -> metrics)
- [ ] Regression tests: golden-file comparisons for known conversations
- [ ] **Port v1 acceptance test framework** (`scripts/run_acceptance_tests.py`) — Tests A/B/C must pass before any quantitative claim
- [ ] **Anti-circularity gate:** Acceptance test verifying R² < 0.01 between evidence features and role labels
- [ ] **Re-run clustering** on 507 canonical corpus with evidence-only features (v4.0 clusters were on mixed features — this is a documented gap)
- [ ] Test coverage target: >80% for core pipeline modules

#### 1.2 Fix Classification Quality
The 93.1% "Mixed/Other" rate from gpt-4o-mini makes fine-grained role analysis impossible.

**Options (choose one or combine):**
- [ ] Upgrade to gpt-4o or Claude Sonnet for classification (cost vs accuracy tradeoff)
- [ ] Implement human-in-the-loop validation (kappa > 0.70 target already documented but never implemented)
- [ ] Two-pass classification: coarse LLM pass -> human review of edge cases
- [ ] For mental health data: classification must distinguish therapeutic roles from general instrumental roles

#### 1.3 Improve Affect Measurement
- [ ] Implement transformer-based sentiment (candidate: `cardiffnlp/twitter-roberta-base-sentiment-latest`, already identified in v1 remediation)
- [ ] Validate against PAD model — ensure backward compatibility with existing metrics
- [ ] Target: >500 unique affect values (current: 503 heuristic-based, need model-based)
- [ ] Add clinical affect dimensions for mental health work: hopelessness, agitation, distress escalation, emotional regulation markers

#### 1.4 Strengthen Constraint Matching
- [ ] Replace Jaccard similarity (0.15 threshold) with semantic embedding similarity
- [ ] Use sentence-transformers for constraint-to-response matching
- [ ] Validate: compare old vs new matching on known conversation set; measure precision/recall improvement
- [ ] This matters especially for mental health because users paraphrase emotional needs heavily

#### 1.5 Fix Pipeline Errors
- [ ] Resolve "INTRODUCES" errors (98% of ~250 errors) — strengthen constraint state machine to handle LLM-generated constraints
- [ ] Fix NoneType errors in move classification (~2-3% data loss) — add defensive parsing with fallback
- [ ] Fix schema validation failures — ensure ViolationEvent nodes always have required fields
- [ ] Add error categorization and automated triage to pipeline output

---

### Phase 2: Mental Health Data Integration (RQ2a)

#### 2.1 Data Sourcing & Ethics
- [ ] Identify candidate datasets:
  - DAIC-WOZ (depression interviews, established research dataset)
  - ESConv (emotional support conversations)
  - Counseling/therapy conversation corpora (with appropriate IRB/ethics approval)
  - Mental health chatbot logs (Woebot, Wysa — if accessible)
  - Reddit mental health support communities (public, but sensitive)
- [ ] Establish data governance protocol:
  - IRB approval or equivalent ethics review
  - Anonymization pipeline (PII removal before any processing)
  - Clear data retention and destruction policy
  - Content warning system for researchers viewing distressing material
- [ ] Define inclusion criteria: minimum turn count, language, quality thresholds

#### 2.2 Extend the Role Taxonomy for Mental Health
The current 12-role taxonomy is built for general task-oriented conversation. Mental health interactions require new roles.

**Proposed Mental Health Role Extensions:**

| Dimension | Authority | Human Role | AI Role |
|-----------|-----------|------------|---------|
| **Therapeutic** | High | Help-Seeker, Crisis-Discloser | Therapist-Proxy, Crisis-Responder |
| **Therapeutic** | Low | Emotional-Processor | Reflective-Listener, Validator |
| **Therapeutic** | Equal | Meaning-Maker | Collaborative-Explorer |
| **Harmful** | Any | Dependency-Former | Surrogate-Attachment |

These extend, not replace, the existing taxonomy. The key question: **do mental health conversations show the same "Instrumental Concentration" (98.8%) or do they activate the empty expressive quadrants?**

#### 2.3 Adapt the Pipeline (Context Engine Extensions)

**Move Classifier (`scripts/atlas/pipeline/move_classifier.py`):**
- [ ] Add 7 new move types to `MoveType` enum in `core/enums.py`: VALIDATE_EMOTION, REFLECT_BACK, REFRAME, NORMALIZE, SAFETY_PLAN, SELF_DISCLOSE, SEEK_VALIDATION
- [ ] Write regex patterns for each new move type (follow existing pattern structure in move_classifier.py)
- [ ] Add LLM fallback prompts for ambiguous therapeutic moves
- [ ] Unit test each new pattern against known therapeutic conversation excerpts

**Mode Detector (`scripts/atlas/pipeline/mode_detector.py`):**
- [ ] Add 3 new modes to `InteractionMode` enum: CONTAINING, GUIDING, WITNESSING
- [ ] Write detection patterns (follow LISTENER_SIGNALS/ADVISOR_SIGNALS/EXECUTOR_SIGNALS structure)
- [ ] Add 3 new violation types to `ModeViolationType` enum: PREMATURE_REFRAME, EMOTIONAL_BYPASS, BOUNDARY_VIOLATION
- [ ] Update violation classification matrix for new mode combinations

**Constraint Tracker (`scripts/atlas/pipeline/constraint_tracker.py`):**
- [ ] Treat emotional boundaries as constraints (same FSM, no state machine changes needed)
- [ ] Add mental health constraint hardness subtypes: emotional_boundary, therapeutic_frame, crisis_protocol
- [ ] Replace Jaccard matching with semantic similarity (Phase 1.4) — critical for emotional paraphrasing

**Safety Layer (NEW):**
- [ ] Add crisis indicator detection to move classifier (suicidal ideation, self-harm, acute distress markers)
- [ ] Flag conversations exceeding crisis threshold for human review queue
- [ ] Add `SAFETY_ALERT` node type to graph schema
- [ ] Log safety events to separate audit trail (`/data/users/{id}/logs/safety_alerts.jsonl`)

#### 2.4 New Metrics for Mental Health Context

| Metric | What It Measures | Why It Matters |
|--------|-----------------|---------------|
| Emotional Attunement Score | Does AI response match user's emotional register? | Misattunement in mental health = harm |
| Therapeutic Frame Stability | Does the interaction maintain appropriate boundaries? | Frame breaks in therapy are significant events |
| Dependency Risk Index | Increasing reliance + decreasing outside support references | Tracks surrogate attachment formation |
| Crisis Escalation Trajectory | Hopelessness/agitation trend across turns | Safety-critical metric |
| Repair-to-Rupture Ratio | How often is therapeutic alliance repaired vs broken? | Direct clinical relevance |

---

### Phase 3: Role Definition & Description (RQ2b)

#### 3.1 From Clusters to Archetypes (Rigorous)
v1 taught us: **cluster first, name second**. Apply this principle:

1. [ ] Run pipeline on expanded corpus (original + mental health)
2. [ ] Extract features without role labels — use the move/mode distributions from the context engine as input features (NOT the role labels themselves)
3. [ ] Cluster (HDBSCAN, already configured: min_cluster_size=10, min_samples=5)
4. [ ] Characterize clusters by feature centroids (z-scores relative to population)
5. [ ] Name post-hoc based on what the data shows
6. [ ] Validate with human raters (kappa > 0.65)
7. [ ] **Build Role Inference Layer** — encode each validated cluster as a `RoleSignature` (move distribution + mode distribution + constraint behavior + affect channel)
8. [ ] **Add role inference endpoint** to Context Engine API: `POST /api/context/role/infer` — takes move/mode history, returns current role assignment with confidence
9. [ ] **Run acceptance tests** on role inference: verify role signatures are independent of v1 label features (R² < 0.01)

#### 3.2 Role Card System
v1 established the current taxonomy distribution (N=507 canonical):
- **Human:** Provider 45.2%, Director 29.0%, Information-Seeker 22.9%, Social-Expressor 3.0%
- **AI:** Expert-System 64.1%, Advisor 19.7%, Co-Constructor 7.1%, Relational-Peer 3.9%, Social-Facilitator 3.9%, Learning-Facilitator 1.2%
- **Top pairing:** Provider -> Expert-System (33.1% of all conversations)
- **The funnel:** All three major human roles converge onto Expert-System, creating "relational foreclosure"

For each discovered role, create a structured "Role Card":

- [ ] **Name:** Post-hoc label
- [ ] **Feature Signature:** Which metrics define this role (z-scores)
- [ ] **Prevalence:** % of corpus
- [ ] **Trajectory Pattern:** How conversations in this role typically unfold (spiral type from polar visualization)
- [ ] **Collapse Risk:** Agency Collapse rate for this role
- [ ] **Example Conversations:** Auto-selected exemplars (fixing v1's manual selection error)
- [ ] **Distinguishing Behaviors:** What makes this role different from adjacent ones
- [ ] Script to generate Role Cards automatically from pipeline output

#### 3.3 Validate Authority-Agency Mismatch
- [ ] Operationalize authority as a continuous measure (not binary high/low)
- [ ] Track authority attribution over time (does it increase, decrease, or oscillate?)
- [ ] Compare authority-agency profiles across role types
- [ ] Test whether mental health contexts amplify the mismatch (hypothesis: yes, because vulnerability increases authority attribution)

---

### Phase 4: Visibility Intervention Study (RQ2c)

This is the core new work: **what happens when you show people their roles?**

#### 4.1 Study Design
**Between-subjects, 2x2 design:**

| | Role Visibility ON | Role Visibility OFF |
|---|---|---|
| **General Task** | Cell A (n=80) | Cell B (n=80) |
| **Mental Health Support** | Cell C (n=80) | Cell D (n=80) |

- Start with N=20 formative per cell, scale to N=80 for full study

**Treatment condition — users see a real-time "role dashboard" showing:**
- Current detected role pairing (e.g., "You: Information-Seeker | AI: Expert-System")
- Trajectory visualization (where they are in relational space)
- Role stability indicator (how fixed/fluid the roles are)
- Available but unused role modes (the "empty quadrants")

**Control condition:** Standard chat interface (no role information)

#### 4.2 Dependent Variables

| DV | Measurement | Hypothesis |
|----|-------------|-----------|
| Role Diversity | # unique role transitions per conversation | Visibility increases diversity |
| Expressive Activation | % time in expressive roles | Visibility activates foreclosed modes |
| Agency Collapse Rate | Using existing pipeline metrics | Visibility reduces collapse |
| Repair Behavior | Repair count and success rate | Visibility changes repair strategy |
| User Satisfaction | Post-task survey (Likert) | Mixed — awareness may increase or decrease satisfaction |
| Conversation Length | Turn count | Visibility may shorten (efficiency) or lengthen (exploration) |
| Meta-Awareness | "Did you notice changing how you spoke?" | Visibility increases meta-awareness |

#### 4.3 Build the Visibility Interface

**Design informed by v1 findings:**
- v1 showed 97% instrumental concentration — the visibility interface should make the "empty quadrants" visible as *invitations*, not just data
- v1 showed 2,030x within-label variance — the interface must show trajectory (journey), not just current role (destination)
- v1 showed affect volatility is the #1 signal (37.3%) — the live visualization should emphasize emotional trajectory, not role labels
- v1's "Curation Paradox" (OASST curated for quality had *narrowest* relational range) suggests that making roles visible might paradoxically *narrow* behavior if users try to "optimize" — the interface must frame exploration as positive

The frontend prototype (React + Vite + Tailwind) and Context Inventory Interface already exist. Extend them:

**Backend: Real-Time Pipeline Mode (NEW execution path):**
- [ ] Build incremental pipeline runner — processes one turn at a time instead of full conversation
  - After each user message: run move classifier on that turn only, update constraint tracker state machine
  - After each AI response: run mode detector on the turn pair, check for mode violations
  - After both: compute current role from accumulated move/mode history via Role Inference Layer
- [ ] Add WebSocket endpoint: `WS /api/context/role/stream` — pushes role state updates to frontend on each turn
  - Payload: `{current_roles, trajectory_update, stability, suggestions, constraint_status}`
- [ ] Add `role_state` fields to `TaskMetadata` in `context_engine/models.py`:
  - `current_human_role`, `current_ai_role`, `role_history`, `role_transitions`, `time_in_current_role`
- [ ] Persist role state via existing TaskManager (extends `{task_id}.json`)

**Frontend: Role Dashboard (extends existing Context Inventory sidebar):**
- [ ] Add real-time role detection sidebar — repurpose Constraint Registry component to show role state
- [ ] Polar trajectory visualization updated live (reuse BLOOM atlas_suite polar layout, adapt for streaming data)
- [ ] "Role suggestion" feature: "You've been in Information-Seeker mode for 5 turns. Try asking the AI to explore with you."
- [ ] Show "empty quadrants" as invitations — highlight unused role modes from the relational space
- [ ] For mental health condition: careful framing — "Your conversation style" not "Your role" (avoid clinical labeling)

#### 4.4 Ethical Considerations

| Risk | Mitigation |
|------|-----------|
| Showing people their "role" could be experienced as judgmental | Frame as "conversation style" not "personality" |
| Mental health participants may feel surveilled | Opt-in, debrief, no clinical claims |
| Visibility could induce performativity (changing behavior to "look good") | This IS the research question — document as finding |
| Crisis situations in mental health data | Human monitor for all mental health sessions; crisis protocol |

---

### Phase 5: Human-Human Comparison (Cross-cutting)

#### 5.1 Obtain Human-Human Baseline Data & Symmetrize Pipeline
- [ ] Use established corpora: Switchboard, BNC, CALLHOME, or therapy transcripts
- [ ] **Symmetrize the move classifier** for human-human data:
  - Relabel `actor: "user" | "assistant"` to `actor: "speaker_a" | "speaker_b"`
  - Both speakers can now PROPOSE_CONSTRAINT, REPAIR_INITIATE, VIOLATE, etc.
  - Add `SELF_REPAIR` move type (humans self-repair; LLMs structurally cannot)
  - Detection patterns: "I mean", "what I meant was", "sorry, I should say", "let me rephrase"
- [ ] **Symmetrize the mode detector** — classify BOTH speakers per turn, not just user→AI
- [ ] **Symmetrize the constraint tracker** — both speakers can propose, accept, violate, and repair constraints
- [ ] Apply the same pipeline (move classification, role detection, trajectory mapping)
- [ ] Compare: Where do human-human conversations live in relational space vs human-AI?

#### 5.2 Key Comparisons

| Dimension | Human-Human (Expected) | Human-AI (Known) | Gap |
|-----------|----------------------|-----------------|-----|
| Instrumental % | ~60-70% | 98.8% | ~30% foreclosure |
| Repair success rate | ~70-80% | 0.1% | 700x deficit |
| Self-repair rate | ~80% of repairs | ~0% | Complete structural inversion |
| Role transitions | Fluid, negotiated | Frozen | By design |
| Authority distribution | Dynamic, reciprocal | Fixed asymmetry | By design |
| Constraint half-life | Persistent (shared memory) | 2.49 turns | Implicit State Pathology |

#### 5.3 The "What Are We?" Comparison Framework
The paper title asks "So... What are we?" — the comparison provides the answer:

- **Human-human:** Relationships with full role repertoire, self-repair, mutual grounding
- **Human-AI:** Structurally impoverished instrumental corridors with broken repair and projected authority
- **The gap between these two IS the foreclosure**

---

## Implementation Priority

### P0 — Foundation (Must complete before anything else)

| Task | Dependency | Phase | Context Engine Impact |
|------|-----------|-------|---------------------|
| Test suite for existing pipeline | None | 1.1 | Tests for move_classifier.py, mode_detector.py, constraint_tracker.py |
| Fix classification quality | None | 1.2 | Upgrade LLM model in move classifier's LLM fallback |
| Fix pipeline errors (INTRODUCES, NoneType, schema) | None | 1.5 | Fix constraint_tracker.py state machine + move_classifier.py None handling |

### P1 — Core Extensions (Unblocks all research questions)

| Task | Dependency | Phase | Context Engine Impact |
|------|-----------|-------|---------------------|
| Semantic constraint matching | P0 | 1.4 | Replace Jaccard in constraint_tracker.py with sentence-transformers |
| Transformer-based affect measurement | P0 | 1.3 | Add affect channel to evidence_features.py |
| Mental health data sourcing + ethics | None (long lead time) | 2.1 | No code changes — data acquisition |
| **Build Role Inference Layer** | P0 (tests) | 3.1 | NEW: `RoleSignature` model + inference logic over move/mode history |
| **Add role inference endpoint** | Role Inference Layer | 3.1 | NEW: `POST /api/context/role/infer` in context_engine/api.py |

### P2 — Domain Extensions (Enables specific RQs)

| Task | Dependency | Phase | Context Engine Impact |
|------|-----------|-------|---------------------|
| Add 7 therapeutic move types | P0 (tests) | 2.3 | Extend MoveType enum + add regex patterns in move_classifier.py |
| Add 3 therapeutic modes | P0 (tests) | 2.3 | Extend InteractionMode enum + patterns in mode_detector.py |
| Add 3 therapeutic violation types | Therapeutic modes | 2.3 | Extend ModeViolationType + violation matrix in mode_detector.py |
| Add safety layer | Therapeutic moves | 2.3 | NEW: crisis detection + SAFETY_ALERT node type + audit trail |
| Role Card system + auto exemplar selection | Role Inference | 3.2 | Script generates cards from RoleSignature + pipeline output |
| Add 5 mental health metrics | Therapeutic moves + modes | 2.4 | Extend ConversationMetrics in graph_metrics.py |
| **Build real-time incremental pipeline** | Role Inference | 4.3 | NEW execution path: per-turn processing instead of batch |
| **Add WebSocket endpoint** | Incremental pipeline | 4.3 | NEW: `WS /api/context/role/stream` in context_engine/api.py |
| **Build Role Dashboard frontend** | WebSocket | 4.3 | Extend Context Inventory sidebar with role state display |
| Symmetrize classifier for human-human | P0 (tests) | 5.1 | Add SELF_REPAIR move, relabel actors, symmetric mode detection |
| Human-human baseline corpus processing | Symmetric classifier | 5.1 | Run extended pipeline on Switchboard/BNC/CALLHOME |

### P3 — Studies (Primary empirical contributions)

| Task | Dependency | Phase | Context Engine Impact |
|------|-----------|-------|---------------------|
| Formative visibility study (N=80) | Role Dashboard + IRB | 4.1 | System runs in real-time mode during study sessions |
| Full visibility study (N=320) | Formative results | 4.1 | Scale real-time infrastructure |
| Human-human vs human-AI comparison paper | Baseline data | 5.3 | Analysis only — no new code |

---

---

## Build Order: Concrete Implementation Sequence

This is the step-by-step file modification order. Each step builds on the previous.

### Step 1: Test Suite (P0, blocks everything)

```
CREATE: tests/
CREATE: tests/test_move_classifier.py     — Test all 13 existing regex patterns against known inputs
CREATE: tests/test_mode_detector.py       — Test 3 existing mode patterns + scoring logic
CREATE: tests/test_constraint_tracker.py  — Test FSM transitions: STATED→ACTIVE→VIOLATED→REPAIRED etc.
CREATE: tests/test_pipeline_integration.py — Golden-file: known conversation → expected graph + metrics
CREATE: tests/test_acceptance.py          — Port v1 scripts/run_acceptance_tests.py (Tests A/B/C)
CREATE: tests/fixtures/                   — Sample conversations for regression testing
```

### Step 2: Fix Pipeline Errors (P0)

```
MODIFY: scripts/atlas/pipeline/constraint_tracker.py
  - Fix "INTRODUCES" errors: handle LLM-generated constraints with weak markers
  - Fix NoneType: add defensive checks when move classification returns None
  - Add error categorization to output

MODIFY: scripts/atlas/pipeline/move_classifier.py
  - Add None-safe parsing for AI responses
  - Add fallback move (GENERATE_OUTPUT) when classification fails

MODIFY: scripts/atlas/pipeline/build_atlas_graph.py
  - Ensure ViolationEvent nodes always have violation_idx + constraint_id
```

### Step 3: Semantic Constraint Matching (P1)

```
MODIFY: scripts/atlas/pipeline/constraint_tracker.py
  - Replace match_move_to_constraint() Jaccard implementation
  - Add sentence-transformers embedding: encode constraint text + move text
  - Use cosine similarity with threshold 0.60 (up from Jaccard 0.15)
  - Add embedding cache to avoid recomputation

ADD DEPENDENCY: requirements.txt — sentence-transformers
```

### Step 4: Role Inference Layer (P1, core new component)

```
CREATE: scripts/atlas/pipeline/role_inferrer.py
  - RoleSignature dataclass: name, move_pattern, mode_pattern, constraint_behavior, min_confidence
  - Define initial signatures from v1 taxonomy (Director, Provider, Information-Seeker, etc.)
  - infer_role(move_history, mode_history) → Role(name, confidence, since_turn)
  - Track role transitions over time

MODIFY: scripts/atlas/core/enums.py
  - Add RoleType enum (matches 12-role taxonomy + therapeutic extensions)

MODIFY: scripts/atlas/core/models.py
  - Add RoleAssignment model: role_type, confidence, start_turn, end_turn
  - Add RoleTrack: list of assignments over conversation

MODIFY: scripts/atlas/run_pipeline.py
  - Add Step 4.5: Role Inference (after constraint tracking, before graph building)
  - Feed move + mode history into role_inferrer

MODIFY: scripts/atlas/pipeline/build_atlas_graph.py
  - Add Role node type to graph schema
  - Add ASSUMES_ROLE edge type (Turn → Role)

CREATE: tests/test_role_inferrer.py
```

### Step 5: Context Engine Role Endpoint (P1)

```
MODIFY: context_engine/models.py
  - Add role_state fields to TaskMetadata:
    current_human_role, current_ai_role, role_history, role_transitions, time_in_current_role

MODIFY: context_engine/api.py
  - Add POST /api/context/role/infer endpoint
  - Takes: user_id, task_id, conversation_history
  - Returns: current roles, role history, transition count

MODIFY: context_engine/task_manager.py
  - Add update_role_state() method
  - Persist role state in task JSON
```

### Step 6: Therapeutic Extensions (P2, for mental health)

```
MODIFY: scripts/atlas/core/enums.py
  - Add to MoveType: VALIDATE_EMOTION, REFLECT_BACK, REFRAME, NORMALIZE,
    SAFETY_PLAN, SELF_DISCLOSE, SEEK_VALIDATION
  - Add to InteractionMode: CONTAINING, GUIDING, WITNESSING
  - Add to ModeViolationType: PREMATURE_REFRAME, EMOTIONAL_BYPASS, BOUNDARY_VIOLATION

MODIFY: scripts/atlas/pipeline/move_classifier.py
  - Add regex patterns for each new therapeutic move type
  - Add LLM prompt templates for ambiguous therapeutic moves

MODIFY: scripts/atlas/pipeline/mode_detector.py
  - Add CONTAINING_SIGNALS, GUIDING_SIGNALS, WITNESSING_SIGNALS pattern arrays
  - Update violation classification matrix for new mode combinations

CREATE: scripts/atlas/pipeline/safety_detector.py
  - Crisis indicator patterns (suicidal ideation, self-harm, acute distress)
  - Threshold-based flagging
  - Audit trail logging

MODIFY: scripts/atlas/pipeline/graph_metrics.py
  - Add 5 mental health metrics to ConversationMetrics:
    emotional_attunement, frame_stability, dependency_risk, crisis_trajectory, repair_rupture_ratio

CREATE: tests/test_therapeutic_moves.py
CREATE: tests/test_safety_detector.py
```

### Step 7: Real-Time Incremental Pipeline (P2, for visibility study)

```
CREATE: scripts/atlas/pipeline/incremental_runner.py
  - IncrementalPipeline class: processes one turn at a time
  - Maintains state between turns: constraint_tracker, mode_history, move_history, role_state
  - Methods: process_user_turn(), process_ai_turn(), get_current_state()

MODIFY: context_engine/api.py
  - Add WebSocket endpoint: WS /api/context/role/stream
  - On each message: run IncrementalPipeline.process_*_turn()
  - Push: {current_roles, trajectory_update, stability, suggestions, constraint_status}

MODIFY: backend/main.py
  - Add WebSocket route registration

CREATE: tests/test_incremental_pipeline.py
```

### Step 8: Role Dashboard Frontend (P2)

```
MODIFY: frontend/src/components/
  - Add RoleDashboard.tsx — displays current role pairing, trajectory, stability
  - Add RoleTrajectory.tsx — live polar visualization (port from atlas_suite)
  - Add RoleSuggestions.tsx — "Try exploring mode" prompts
  - Add useRoleStream.ts hook — WebSocket connection to /api/context/role/stream

MODIFY: frontend/src/pages/
  - Add RoleVisibilityChat.tsx — treatment condition page (chat + Role Dashboard)
  - Update router to include new page
```

### Step 9: Human-Human Symmetrization (P2)

```
MODIFY: scripts/atlas/core/enums.py
  - Add SELF_REPAIR to MoveType

MODIFY: scripts/atlas/pipeline/move_classifier.py
  - Add SELF_REPAIR_PATTERNS regex array
  - Add symmetric actor handling: accept "speaker_a" | "speaker_b" alongside "user" | "assistant"

MODIFY: scripts/atlas/pipeline/mode_detector.py
  - Classify both speakers per turn (not just user→AI)
  - Return two ModeAnnotations per turn pair

CREATE: scripts/atlas/pipeline/corpus_adapter.py
  - Adapters for Switchboard, BNC, CALLHOME transcript formats
  - Normalize to same JSON structure as WildChat/Arena/OASST

CREATE: tests/test_symmetric_classifier.py
```

---

## What This Produces

If executed, this plan yields:

1. **A defensible, tested pipeline** — fixing every v1 audit issue
2. **Mental health role taxonomy** — first systematic mapping of therapeutic roles in human-AI conversation
3. **Role Cards** — publishable, validated descriptions of each discovered role
4. **Visibility intervention evidence** — does showing people their roles change anything?
5. **The human-human comparison** — quantifying exactly what's foreclosed
6. **The "What are we?" paper** — answering the title question with empirical evidence across both domains

**The throughline:** v1 showed us the map. v2 shows us what happens when people can see the map too.

---

## Key Metrics for Success

| Metric | Target | Source |
|--------|--------|--------|
| Test coverage | >80% core pipeline | Phase 1.1 |
| Classification quality | <20% "Mixed/Other" (down from 93.1%) | Phase 1.2 |
| Inter-rater agreement | kappa > 0.70 for collapse, kappa > 0.65 for archetypes | Phase 3.1 |
| Feature independence | R² < 0.01 between evidence and label features | Phase 1.1 |
| Affect granularity | >500 unique values, model-based | Phase 1.3 |
| Constraint matching precision | >0.80 (up from Jaccard 0.15) | Phase 1.4 |
| Pipeline error rate | <1% (down from ~2-3%) | Phase 1.5 |
| Acceptance Tests A/B/C | All PASS (resolve AI role WARNING from Test A if possible) | Phase 1.1 |
| Evidence-only clustering | Re-run on canonical corpus; document honest silhouette | Phase 1.1 |

---

## Architecture Reference

```
Atlas Pipeline (batch, 7-stage):
  move classify -> mode detect -> constraint track -> graph build -> metrics -> viz -> export

Real-Time Pipeline (incremental, for visibility study):
  per-turn move classify -> update constraint FSM -> mode detect -> role infer -> push via WebSocket

Context Engine API (FastAPI, port 8000):
  /api/context/task/*         — Task CRUD, lifecycle, metrics
  /api/context/event/pin      — Pin constraint to task (Pattern 1)
  /api/context/query/context   — Scoped query (Pattern 3)
  /api/context/role/infer      — Role inference (NEW)
  /api/context/role/stream     — Real-time role updates via WebSocket (NEW)
  /api/chat                    — Constraint-aware LLM chat

Frontend (React + Vite + Tailwind, port 5173):
  Baseline chat          — Control condition (no role info)
  Treatment chat         — Chat + Context Inventory sidebar (constraint visibility)
  Role Dashboard         — Chat + Role Inference sidebar (role visibility, NEW)

Viz: BLOOM Design System (atlas_suite/, port 8001)

Data:
  atlas_canonical (N=744), task_classified (N=969)
  /data/users/{id}/tasks/    — TaskObject persistence (context engine)
  /data/users/{id}/logs/     — Event logs (restatements, violations, safety alerts)

Key Files:
  Pipeline:         scripts/atlas/run_pipeline.py
  Move Classifier:  scripts/atlas/pipeline/move_classifier.py (13 moves + extensions)
  Mode Detector:    scripts/atlas/pipeline/mode_detector.py (3 modes + extensions)
  Constraint FSM:   scripts/atlas/pipeline/constraint_tracker.py
  Graph Builder:    scripts/atlas/pipeline/build_atlas_graph.py
  Metrics:          scripts/atlas/pipeline/graph_metrics.py
  Core Enums:       scripts/atlas/core/enums.py (MoveType, ConstraintState, InteractionMode)
  Core Models:      scripts/atlas/core/models.py (Move, Constraint, Turn, etc.)
  Context Engine:   context_engine/api.py, context_engine/models.py, context_engine/task_manager.py
  Backend:          backend/main.py, backend/routers/, backend/services/
  Errors:           data/atlas_canonical/errors.json
  Theory:           theory/implicit_state_pathology.md
  Methodology:      scripts/CANONICAL_METHODOLOGY.md
```
