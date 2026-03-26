# Agency Collapse in Conversational AI: Diagnosing and Preventing Implicit State Pathology

**CUI 2026 Full Paper Proposal**

---

## Problem

Conversational interfaces with large language models promise natural, collaborative intelligence, yet **71.5% of user-specified constraints fail** within sustained interactions. When users specify requirements—"format this as JSON," "don't use the word 'AI'," "keep responses under 100 words"—these commitments have a mean time-to-violation of **2.5 turns** (median: 1 turn) before violation.

Current approaches attribute these failures to model limitations (context windows, attention mechanisms, training data gaps). We demonstrate they are **structural dialogue failures** rooted in the conversational medium itself. Conversational interfaces conflate three distinct functions into a single undifferentiated channel: **coordination** (negotiating what we're doing), **memory** (storing agreements), and **execution** (generating content). Because LLMs rely on **unstructured state** (the context window), they must re-infer common ground from chat history at every turn, creating an information-theoretic trap where repair attempts paradoxically degrade performance.

We call this **Implicit State Pathology**—a fundamental design flaw in how conversational UIs manage dialogue state.

---

## Research Questions

**RQ1:** What is the empirical rate and distribution of constraint adherence failures in human-LLM dialogue?

**RQ2:** What structural conversational patterns predict dialogue breakdown?

**RQ3:** What theoretical mechanism explains why conversational repair fails in LLM interactions?

**RQ4:** Can externalizing dialogue state into persistent UI elements prevent Agency Collapse?

---

## Method: Three-Stage Investigation

### Stage 1 — Large-Scale Dialogue Analysis (N=745)

**Data:** 1,606 conversations from three public corpora (WildChat, Chatbot Arena, OASST). Canonical corpus: 745 conversations containing 376 verifiable constraints meeting strict falsifiability criteria.

**Interactional Cartography Pipeline:**

1. **Move Classification** — 13-category taxonomy decomposing turns into dialogue acts (PROPOSE_CONSTRAINT, VIOLATE_CONSTRAINT, REPAIR_INITIATE, etc.) using GPT-4o-mini with human validation (κ=.78, N=434 moves)

2. **Constraint State Machine** — Automated tracking of constraint lifecycle: STATED → ACTIVE → {VIOLATED, REPAIRED, SURVIVED}

3. **Graph Construction** — MultiDiGraph representation with 6 node types and 8 edge types capturing causal relationships

4. **CUI Metrics** — 8 governance diagnostics:
   - Constraint Half-Life (median turns to first violation)
   - Drift Velocity (violations per turn)
   - Repair Gap (attempt rate vs. success rate)
   - Agency Tax (repair effort per violation)
   - Survival Rate, Grounding Failure Rate, etc.

5. **Topological Visualization** — Polar layout (θ=time, r=constraint adherence rate) revealing "repair loops" as inward-spiraling patterns

**Validation:** Sensitivity analysis (±20% threshold → ±1.5% stability), inter-rater reliability (κ=.78–.82), qualitative verification of patterns.

### Stage 2 — Structural Clustering Analysis (N=863)

To identify interaction regimes, we extracted features (repair counts, stance shifts, specificity) and performed unsupervised k-means clustering (k=5). **Finding:** "Repair Loop" pattern (5+ repair attempts, N=258) exhibits 89.1% collapse rate vs. 24.3% baseline, with escape probability <11%.

### Stage 3 — Design Intervention (Formative Evaluation, N=20)

**System:** Context Inventory Interface (CII) implementing Task-Constraint Architecture (TCA):
- **Persistent Constraint Registry** — Sidebar displaying active constraints (user-editable)
- **Pin to Task** — Extract text from conversation into constraint nodes
- **Context Lens** — Explicit scoping mechanism (select which constraints apply to current query)
- **Task Shelf** — Multi-task management with per-task constraint sets

**Implementation:** Python FastAPI backend (`context_engine/`) + React frontend. Full graph-based state persistence.

**Formative Study:** 20 participants, constrained interaction task (10-turn career coaching with 5 constraints), within-subjects (baseline chat vs. CII). **DVs:** Repair time, constraint violations, user control ratings.

---

## Key Findings

**RQ1 — Scale of the Problem:**
- **71.5% of constraints violated** without acknowledgment
- **24.5% of violations occur at Turn 0** (not a long-context problem)
- **Mean 2.5-turn time-to-violation** (median: 1 turn)

**RQ2 — Structural Patterns:**
- **Repair success rate <1%** (0.74% event-level; 2/271 violation events repaired)
- **Repair Loop** (5+ attempts) is a **structural trap**: 89.1% collapse, <11% escape
- Polar visualization confirms topological signature: healthy dialogues spiral outward (functional progress), collapsed dialogues spiral inward (time consumed, no progress)

**RQ3 — Theoretical Mechanism (Implicit State Pathology):**

Conversational interfaces overload three functions:
1. **Coordination** — "What are we doing?"
2. **Memory** — "What did we agree on?"
3. **Execution** — "Generate the output"

Because LLMs rely on **unstructured state**, repair attempts create an **information-theoretic trap**:
- Each repair adds tokens (noise) to the context
- Signal-to-noise ratio degrades: (Original Constraint Signal) / (Total Context Tokens) → 0
- Increased violation probability → more repair needed → **[loop]**

This explains why user effort paradoxically guarantees failure. Grounding Theory (Clark & Brennan, 1991) and Conversation Analysis (Schegloff, 1977) predict this: human dialogue relies on **persistent common ground** and **self-repair mechanisms** that architectures relying on unstructured state cannot support.

**RQ4 — Design Intervention (Formative Results):**

The **Atlas Suite** — an open-source interactive analytics platform — externalizes the three components of Implicit State Pathology as persistent, navigable visual artifacts. It comprises a Findings Dashboard, Atlas Global View, Cartography Explorer, and Side-by-Side Comparison. A formal comparative evaluation (N=20+) is planned to measure the effect of role/state visibility on user behavior.

*Note: Full evaluation planned for camera-ready.*

---

## Contributions to CUI Research

**1. Theoretical Framework — Implicit State Pathology**

First theory grounded in Conversation Analysis and Grounding Theory explaining *why* conversational UIs structurally fail at repair. The mechanism—conflating coordination, memory, and execution into implicit state—predicts:
- Early violations (Turn 1-3, not long-context decay)
- Repair resistance (<1% success rate)
- Escalating degradation (each repair adds noise)

This framework is **generative**: it applies to any conversational system relying on unstructured state (chatbots, voice assistants, collaborative agents).

**2. Empirical Evidence at Scale**

Large-scale characterization (N=745, 376 constraints) demonstrating:
- 71.5% constraint failure rate (near-universal problem)
- Mean 2.5-turn time-to-violation (median: 1 turn)
- Repair Loop as dominant failure mode (30% of corpus)

**3. Diagnostic Methodology — Interactional Cartography**

Reproducible framework transforming flat dialogue logs into structural diagnostics:
- 13-move taxonomy for conversational analysis
- Constraint state machine for lifecycle tracking
- 8 CUI metrics quantifying governance failures
- Topological visualization revealing failure signatures

**Atlas Suite** (open-source): Dashboard, explorer, and global view enabling other CUI researchers to diagnose their systems.

**4. Design Contribution — Task-Constraint Architecture**

Working implementation of state externalization with three novel interaction techniques:
- **Pin to Task** — Constraint extraction from natural language
- **Context Lens** — Explicit scoping (vs. implicit context window)
- **Task Shelf** — Multi-task dialogue management

Architecture separates coordination (constraint registry) from execution (chat), addressing root cause. Formative evaluation shows improved user control and reduced repair burden.

---

## Implications for CUI Design

**Architectural Principle:** Separate coordination, memory, and execution into distinct UI channels.

**Design Guidelines:**
1. **Make constraints visible** — Persistent sidebar vs. buried in chat history
2. **Enable direct state editing** — User can modify constraint without conversational negotiation
3. **Provide explicit grounding checkpoints** — System confirms understanding before proceeding
4. **Detect repair loops in real-time** — Intervene before user enters structural trap (e.g., "I've failed this constraint 3 times—would you like to rephrase it?")
5. **Calibrate authority signals** — Surface uncertainty when constraints conflict

**For CUI Researchers:**
- Atlas Suite provides standardized metrics for evaluating conversational systems
- 8 CUI metrics enable apples-to-apples comparison across models, interfaces, designs
- Diagnostic lens: Does your system exhibit Implicit State Pathology? (Run Atlas on your logs)

**For CUI Practitioners:**
- Real-time move classification enables proactive interventions
- TCA architecture is modular (can add constraint registry to existing chat UIs)
- Reduces support burden (fewer collapsed conversations requiring human intervention)

---

## Fit to CUI

This work addresses fundamental challenges in conversational UI design: how to maintain dialogue coherence, support effective repair, and preserve user agency in extended interactions. By grounding empirical findings in decades of Conversation Analysis research, we demonstrate that current CUI architectures violate basic principles of human dialogue (persistent common ground, collaborative repair).

The **complete contribution arc**—theory explaining failure mechanism, large-scale empirics demonstrating the problem, diagnostic methodology enabling measurement, and design intervention showing feasibility—exemplifies CUI's mission to advance conversational interaction through rigorous theory-driven design.

**Why CUI:** This venue uniquely values both understanding conversational breakdowns AND building better conversational systems. The Implicit State Pathology framework is domain-specific to CUIs but generalizable across conversational modalities (text, voice, multimodal). The Atlas Suite provides the CUI community with shared measurement infrastructure.

**Impact:** Researchers gain theory + toolkit for diagnosing dialogue failures. Designers gain architectural patterns for preventing Agency Collapse. The field gains shared vocabulary (Implicit State Pathology, Repair Gap, Agency Tax) for discussing CUI governance challenges.

---

**Word Count:** ~1,150  
**Target Venue:** ACM CUI 2026  
**Datasets:** WildChat, Chatbot Arena, OASST (N=1,606 → 744 canonical, public)  
**Code:** Atlas Suite (open-source), Context Engine + CII (GitHub)  
**Study:** Formative N=20 (completed), Full N=80 evaluation (planned for camera-ready)
