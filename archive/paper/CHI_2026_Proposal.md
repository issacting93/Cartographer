# So… What Are We? Role Rigidity and the Structural Foreclosure of Human-AI Relationship

**CHI 2026 Full Paper Proposal**

## Problem: Relational Foreclosure

Human-AI conversation is structurally foreclosed. Across **2,577 conversations** from three independent corpora, we find that **97% of human participants adopt instrumental roles** and **70% of all interactions collapse into a single dyad** — Information Seeker to Expert System. Users approach AI as a search engine dressed in conversational clothing, and the system reinforces this by defaulting to authoritative knowledge delivery 77.6% of the time.

This would be unremarkable if the resulting interactions were stable. They are not. Within that dominant IS→ES pairing, conversations sharing identical role labels exhibit up to **2,817x variance** in affective trajectories. The role label predicts the *destination* but not the *journey* — and the journey is where governance fails.

The missing piece: **role rigidity prevents repair.** When 70% of interactions are locked into Expert System mode, the AI has no relational infrastructure for the work that constraint maintenance requires — negotiation, acknowledgment, mode-shifting. The result: **71.5% of user-specified constraints fail silently**, with a mean time-to-violation of **2.5 turns**. Repair attempts succeed less than **1% of the time**. We term this structural failure state **Agency Collapse**, and find it in **50.3%** of sustained conversations.

### The Mechanism: Why Role Rigidity Causes Constraint Failure

Current discourse attributes these failures to model limitations (context window, attention decay, hallucination). We argue they are **interactional pathologies** caused by the convergence of three structural properties:

1. **Bounded Personhood.** Users attribute high epistemic authority to a system with zero volitional agency. The AI sounds like an expert, so users expect it to behave like one — tracking agreements, maintaining constraints, acknowledging errors. It cannot.

2. **Implicit State Pathology.** The conversational interface overloads coordination (managing the dialogue), memory (retaining context), and execution (performing the task) into a single undifferentiated channel. Constraints exist only as tokens in the scrolling history.

3. **The Instrumental Trap.** The 97% instrumental concentration creates a "narrow funnel" where diverse human needs — collaboration, exploration, learning — are compressed into query-response transactions. When constraints fail within this mode, users have no relational framework for recovery. Expert Systems deliver answers; they don't negotiate.

These three properties create the **Context Trap**: repair attempts add tokens, diluting the constraint signal, increasing violation probability, requiring more repair. User effort paradoxically guarantees failure.

---

## A Multi-Phase Research Program

Our work spans three interconnected studies:

| Phase | Study | N | Question | Key Finding |
|-------|-------|---|----------|-------------|
| **1** | Conversational Cartography | 2,577 | What roles emerge, and do they predict experience? | **97% instrumental; 2,817x affect variance within identical role labels.** Role categories don't predict experience — dynamics do. |
| **2** | Agency Collapse | 863 | What structural mechanisms drive those dynamics? | **50.3% collapse rate.** The "Repair Loop" is a structural doom state. |
| **3** | Interactional Cartography (Atlas) | 745 | Can we map the governance failure precisely? | **71.5% constraint failure; mean 2.5 turns to violation; <1% repair success.** |

### Phase 1 → 2 → 3: The Causal Chain

The phases are not independent studies. They establish a causal narrative:

**Phase 1** proves that role labels are insufficient — the 2,817x variance ratio shows that conversations with the same structural label have radically different affective experiences. The question becomes: *what drives that variance?*

**Phase 2** answers: **repair failure**. Conversations that enter the Repair Loop (5+ correction attempts) collapse 89.1% of the time. The variance is not noise — it traces the boundary between conversations that maintain constraints and those that fight the system.

**Phase 3** quantifies the mechanism. 71.5% of constraints fail. 24.5% fail on the very first AI response (turn 0). Repair succeeds less than 1% of the time. The role rigidity from Phase 1 explains why: an Expert System that cannot shift to Collaborator mode has no mechanism for the relational work that repair requires.

---

## Method: Interactional Cartography

We introduce **Interactional Cartography**, a computational framework that transforms flat conversational text into **graph-structural diagnostics** of relational stability.

### The Pipeline Architecture

1. **Move Classifier:** Decomposes turns into communicative acts (Proposals, Repairs, Violations) using a 13-move taxonomy.
2. **Mode Detector:** Distinguishes requested interaction modes (Listener, Advisor, Executor) from enacted modes, flagging mismatches as mode violations.
3. **Constraint Tracker:** A state machine following each constraint from `STATED` → `ACTIVE` → terminal states (`VIOLATED`, `REPAIRED`, `SURVIVED`).

The resulting **MultiDiGraph** contains 6 node types (Conversation, Turn, Move, Constraint, ViolationEvent, InteractionMode) and 8 edge types, enabling precise causal analysis.

### Data

**Constraint analysis** (Phases 2-3): **745 verified conversations** (WildChat 536, Chatbot Arena 180, OASST 29) with **376 high-quality, verifiable constraints** (e.g., "format as JSON," "don't use the word 'AI'"), rejecting vague aspirations.

**Role and dynamics analysis** (Phase 1): **2,577 conversations** (Chatbot Arena 1,739; WildChat 786; OASST 50) with 30 evidence features across 5 channels (Affect, Divergence, Dynamics, Expressiveness, Structure).

### Validation

All statistics are computed from raw data via `scripts/compute_verified_stats.py` and validated by `scripts/validate_report.py` (51/51 claims PASS). Anti-circularity acceptance tests confirm that evidence features and role labels capture different variance structures (ablation: labels silhouette 0.45 vs evidence 0.11 vs combined 0.09).

---

## Key Findings

### 1. Relational Foreclosure (Phase 1)

The 12-role taxonomy (6 human, 6 AI) reveals extreme concentration:

| Human Role | % | AI Role | % |
|-----------|---|---------|---|
| Information Seeker | 73.9 | Expert System | 77.6 |
| Director | 14.7 | Co-Constructor | 10.0 |
| Provider | 4.8 | Advisor | 4.7 |
| Collaborator | 3.6 | Social Facilitator | 4.2 |
| Social Expressor | 2.4 | Relational Peer | 2.4 |
| Relational Peer | 0.6 | Learning Facilitator | 1.2 |

Only **1.2%** of AI responses function as Learning Facilitators — arguably the most valuable mode for sustained, constraint-sensitive work. The system defaults to delivery, not negotiation.

### 2. Same Role, Different Journey (Phase 1)

Within the IS→ES dyad (N=1,039 conversations with 6+ messages), affect variance spans **2,817x**:
- **Smoothest:** variance = 0.000007 (flat, emotionally neutral)
- **Most volatile:** variance = 0.021 (dramatic oscillations — frustration, recovery, frustration)

Evidence features predict role-pairs at **71.6% accuracy** (16 classes, chance 6.2%), confirming that behavioral signals carry real interactional meaning. The dominant channels: Affect (39.3%), Divergence (21.6%), Dynamics (16.5%).

### 3. Silent Drift is the Norm (Phase 3)

**71.5%** of user-specified constraints are violated without acknowledgment. This is not a "long-context problem" — **24.5% of violations occur at turn 0**, the AI's very first response. Mean time-to-violation: **2.5 turns**.

### 4. The Repair Gap (Phase 3)

Repair succeeds less than **1%** of the time. Users attempt correction, but the system treats these as additional context rather than state updates. The structural explanation: an AI locked in Expert System mode has no mechanism for the acknowledgment, negotiation, and mode-shifting that repair requires.

### 5. The Repair Loop Trap (Phase 2)

Conversations where users attempt **5+ repair moves** (Cluster 0, N=258, 30% of corpus) collapse **89.1%** of the time. Escape probability: **<11%**. These conversations form tightening spirals in the Polar Layout — a visual signature of user effort paradoxically guaranteeing failure.

### 6. Mode Violations as Trigger Events

**535 mode violations** across the corpus: Premature Execution (49.5%), Unsolicited Advice (38.5%), Execution Avoidance (12.0%). Each violation is a potential entry point into the Repair Loop — the AI acts on incomplete specifications or provides unrequested recommendations, and the user must correct it.

---

## The Intervention: Making Roles Visible

### Diagnosis → Prescription

If the problem is **Implicit State** (constraints hidden in scrolling text) compounded by **Role Rigidity** (the AI cannot shift modes), the solution must:
1. **Externalize state** — move constraints out of the chat stream into a persistent, governable registry.
2. **Surface roles** — make the current interaction mode visible so users can recognize the "Instrumental Corridor" and deliberately shift toward more effective modes.

### The Atlas Suite

We implemented this as the **Atlas Suite**, an open-source interactive analytics platform:
- **Findings Dashboard:** Aggregate KPIs and role distributions — the 97% instrumental concentration, the 535 mode violations — as navigable data.
- **Atlas Global View:** Force-directed meta-graph clustering 745 conversations by structural similarity.
- **Cartography Explorer:** Single-conversation deep dive — graph topology, affective trajectory, repair loop visualization. Makes the 2,817x variance tangible.
- **Side-by-Side Comparison:** Direct structural comparison of two conversations.

The suite externalizes role assignments, constraint state, and repair sequences — the three components of Implicit State Pathology — as persistent, navigable visual artifacts.

### Planned Evaluation

A comparative study (N=20+) will measure the effect of role/state visibility on user behavior:
- **H1:** Visibility increases perceived user agency.
- **H2:** Externalizing constraints reduces repair loop frequency.
- **H3:** Making the Instrumental Corridor visible enables deliberate mode-shifting.

---

## Contribution

This work makes **four contributions** to CHI:

### 1. Empirical Map of Relational Foreclosure
We provide the first large-scale evidence (N=2,577) that human-AI interaction is structurally foreclosed: 97% instrumental, 70% in a single dyad, 2,817x affect variance within identical labels. Replicated at 5.1x scale from v1.

### 2. Causal Chain: Role Rigidity → Constraint Failure → Agency Collapse
We connect three studies into a unified narrative: role labels don't predict experience (Phase 1) → repair failure drives the variance (Phase 2) → 71.5% of constraints fail because the dominant role mode has no mechanism for relational repair (Phase 3).

### 3. Theoretical Framework: Bounded Personhood + Implicit State Pathology
We ground these failures in Conversation Analysis (Schegloff) and Grounding Theory (Clark), providing the first account of *why* conversational LLM interfaces structurally cannot support repair: they attribute expert authority to a stateless system locked in a single delivery mode.

### 4. Design Intervention: The Atlas Suite
An open-source diagnostic and visibility platform that externalizes the three components of Implicit State Pathology. Provides practitioners with tools to diagnose relational failure in their own systems, and a testable intervention (role + constraint visibility) for restoring user agency.

---

## Fit to CHI

This paper sits at the intersection of **AI Alignment**, **Conversation Analysis**, and **Interaction Design**. It challenges the field to look beyond model capabilities and address the **structural interactional failures** of current interfaces.

**Why CHI:** By proving that failures attributed to "model limitations" are actually **interface design choices** — the decision to make roles implicit, constraints invisible, and repair unstructured — we open a design space for **High-Agency Interfaces** that support human governance rather than undermine it.

**Why now:** The 97% instrumental finding suggests we are at a critical juncture. If the dominant interaction paradigm calcifies around query-response transactions, the relational potential of conversational AI will be permanently foreclosed. Design intervention is needed before the pattern becomes self-reinforcing.
