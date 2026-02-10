# Agency Collapse: When Conversational Repair Fails in Human-AI Interaction

**CHI 2026 Full Paper Proposal**

## Problem: The Context Trap

Conversational interfaces have become the dominant paradigm for large language models, yet **71.5% of user-specified constraints fail silently** within sustained interactions. When a user says "write me a story set on Mars with no aliens," the constraint *no aliens* has a median half-life of **2.49 turns** before the system violates it—not at turn 50, but within the first few exchanges.

Current discourse attributes these failures to model limitations (context window, attention decay, hallucination). We argue they are **structural governance failures** inherent to the conversational medium itself.

### The Broken Social Contract

Recent work confirms that LLMs reactivate "Computers Are Social Actors" (CASA) expectations (Nass & Reeves, 1996; de Melo et al., 2023). Users unconsciously import functional expectations from human conversation—specifically, **conversational repair** (Schegloff et al., 1977), the self-righting mechanism that allows participants to detect and fix misunderstandings.

However, LLMs lack the structural machinery for this. They are **stateless**. When a user attempts to correct a violation ("No, I said *no aliens*"), the system treats this not as a state update, but as *more context*. This creates the **Context Trap**: repair attempts paradoxically degrade performance by adding noise to the very channel that must carry the constraint signal.

This leads to **Agency Collapse**—a structural failure state where the user's capacity to govern the interaction systematically degrades despite increasing effort.

## A Multi-Phase Research Program

Our work spans three interconnected studies totaling **N=1,606** conversations:

| Phase | Study | Question | Method | Key Finding |
|-------|-------|----------|--------|-------------|
| **Phase 1** | Conversational Cartography<br>(N=562) | Do interaction dynamics matter more than role categories? | PAD trajectory clustering | **83% variance from dynamics, 17% from roles**<br>Role labels do not predict experience. |
| **Phase 2** | Agency Collapse<br>(N=863) | What structural mechanisms drive those dynamics? | Repair-based structural clustering | **50.4% collapse rate**<br>The "Repair Loop" is a structural trap. |
| **Phase 3** | Atlas 2.0<br>(N=744, canonical) | Can we map the governance failure precisely? | Graph-based Interactional Cartography | **71.5% constraint failure**<br>Half-life of 2.49 turns; repair rate 19.9%, but success <0.1%. |

## Method: Interactional Cartography (Atlas 2.0)

We introduce **Interactional Cartography**, a computational framework that transforms flat conversational text into **graph-structural diagnostics** of relational stability.

### The Pipeline Architecture

Unlike prior work that imposes a priori role taxonomies, we employ a **cluster-first methodology** combined with **graph-structural analysis** to discover natural failure modes. The Atlas 2.0 pipeline consists of:

1.  **Move Classifier:** Decomposes turns into communicative acts (Proposals, Repairs, Violations).
2.  **Mode Detector:** Distinguishes requested interaction modes (Listener, Advisor, Executor) from enacted modes.
3.  **Constraint Tracker:** A state machine following each constraint from `STATED` → `ACTIVE` → terminal states (`VIOLATED`, `REPAIRED`, `SURVIVED`).

The resulting **MultiDiGraph** contains 6 node types (Conversation, Turn, Move, Constraint, ViolationEvent, InteractionMode) and 8 edge types, enabling precise causal analysis.

### Data: The Canonical Corpus (N=744)

We analyzed **744 verified conversations** from three diverse datasets:
*   **WildChat (N=535):** Organic, in-the-wild user logs.
*   **Chatbot Arena (N=180):** Adversarial testing logs.
*   **OASST (N=29):** Instruction-following dialogues.

**Quality Filter:** We track only **376 high-quality, verifiable constraints** (e.g., "format as JSON," "don't use the word 'AI'"), rejecting vague aspirations like "be helpful."

### The Atlas Suite: Interactive Visualization

To enable replicable diagnosis, we developed an open-source visual analytics platform:
*   **The Dashboard:** Metrics view showing the "Context Cliff" (where violations concentrate) and "Agency Tax Map" (effort vs. drift).
*   **The Explorer:** Node-link visualizer with **Clockwise Polar Layout**, revealing "Repair Loops" as tightening spirals.
*   **Global View:** Force-directed map clustering the entire corpus by structural similarity.

## Key Findings: The Three-Part Diagnosis

### 1. Silent Drift is the Norm (71.5% Constraint Failure)

Over 7 in 10 user-specified constraints are violated **without apology or acknowledgment**. This is not "hallucination" (fabricated facts); it is **relational drift**—the system abandons agreed-upon interaction rules while maintaining topical coherence.

### 2. The Context Cliff (Half-Life: 2.49 Turns)

Violations concentrate on **Turn 1 (25% of all violations)**, proving this is not a "long-context problem." The AI fails to prioritize constraints during its *first response*, suggesting a fundamental failure of **grounding** (Clark & Brennan, 1991) rather than memory decay.

### 3. The Repair Gap (19.9% Attempt Rate, <0.1% Success)

Users are not passive. They attempt repair in **1 out of 5 violations**. However, repairs rarely persist. The system treats user corrections as additional context rather than **state updates**, forcing users into the role of "Exhausted Auditors" who must re-assert the same constraint every turn.

### 4. The Repair Loop Trap (Phase 2 Structural Finding)

In our Phase 2 study (N=863), we identified **Cluster 0 (N=258, 30% of corpus)**: conversations where users attempt **5+ repair moves**.
*   **Collapse Rate:** **89.1%**.
*   **Escape Probability:** **<11%**.
*   **Visual Signature:** Using the Polar Layout, these conversations form **tightening spirals**, physically trapping users in a "gravity well" of repeated corrections.

## The Mechanism: Implicit State Pathology

We identify the root cause as **Implicit State Pathology**—the conversational interface overloads three distinct functions into a single undifferentiated channel:

1.  **Coordination** (negotiating what we're doing).
2.  **Memory** (storing agreements and constraints).
3.  **Execution** (generating content).

Because LLMs are stateless, they must **re-infer common ground** from the scrolling chat history at every turn. As the conversation grows, the signal-to-noise ratio degrades:

> **The Trap:** Repair attempts add tokens → dilute constraint signal → increase violation probability → require more repair.

This explains why the "Repair Loop" is a structural doom state: *user effort paradoxically guarantees failure*.

### Authority-Agency Decoupling

The interface presents **high authority** (confident, fluent outputs) but **low agency** (no accountability, no memory persistence). Users keep trying to correct the "expert" because social scripts suggest it should work, but the lack of structural agency means corrections never "stick."

## Contribution

This work makes **four contributions** to CHI:

### 1. Empirical Map (71.5% Failure, 2.49 Turn Half-Life)
We provide the first **graph-structural evidence** that constraint adherence failures are:
*   Near-universal (71.5%), not edge cases.
*   Early-onset (Turn 1-3), not long-context problems.
*   Repair-resistant (<0.1% success), not easily fixable.

### 2. Multi-Phase Synthesis (Dynamics → Structure → Mechanisms)
We connect three studies into a unified causal narrative:
*   **Phase 1 (Cartography):** Proved that role labels don't explain variance—*dynamics* do.
*   **Phase 2 (Agency Collapse):** Identified the Repair Loop as the dominant failure structure.
*   **Phase 3 (Atlas 2.0):** Quantified the precise mechanisms (half-life, repair gap, context cliff).

### 3. Theoretical Framework (Grounding + Repair)
We ground these failures in **Conversation Analysis** (Schegloff) and **Grounding Theory** (Clark), providing the first theoretical account of *why* conversational LLM interfaces structurally cannot support effective repair: they conflate coordination, memory, and execution into an implicit, stateless channel.

### 4. Design Argument: Context Inventory Interface (CII)
**Diagnosis:** If the problem is Implicit State and Authority Decoupling...  
**Prescription:** We must **externalize state** and **calibrate authority**.

**Proposed Features:**
*   **Constraint Anchors:** Pinned, visible rules (sidebar UI) to fix memory persistence (R3).
*   **Explicit Checkpoints:** Structural acknowledgment signals to terminate repair sequences (R2).
*   **Authority Calibration:** Visible uncertainty indicators to prevent over-trust (R4).

We propose **Context Inventory Interface (CII)** as the architectural intervention, moving constraints out of the scrolling chat stream into a persistent, governable registry.

## Fit to CHI

This paper sits at the intersection of **AI Alignment**, **Conversation Analysis**, and **Interaction Design**. It challenges the field to look beyond *model capabilities* and address the **structural interactional failures** of current interfaces.

**Why CHI:** By proving that many failures attributed to "model limitations" are actually **interface design choices** (the decision to make everything implicit), we open a new design space for **High-Agency Interfaces** that support human governance rather than undermine it.

**Impact:** Our open-source Atlas Suite enables practitioners to diagnose relational failures in their own systems, and the Context Inventory Interface provides a concrete, testable design intervention.
