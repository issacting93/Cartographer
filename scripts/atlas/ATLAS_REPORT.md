# Atlas of Human-AI Interaction: Canonical Research Report
**Version:** 2.0 (February 2026)  
**Status:** Canonical Findings (N=744)

---

## 1. Executive Summary

### The Headline: 71.5% of Verified Constraints Fail Silently
This report details the findings of the **Atlas 2.0 Pipeline**, a computational framework that maps the degradation of human-AI relational stability. Our study of 744 multi-turn conversations reveals that large language models (LLMs) operate in a **"Context Trap"**: they maintain the technical thread of a conversation while systematically abandoning the relational constraints and interactional modes requested by the user.

### Four Key Indicators
| Finding | Metric | Value | Interpretation |
|---------|--------|-------|----------------|
| **Silent Drift** | Constraint Survival | **28.5%** | Over 7 in 10 specific instructions are violated without apology or repair. |
| **Early Decay** | Constraint Half-Life | **2.49 Turns** | Drift is not a "long-context" problem; it happens within 2-3 exchanges. |
| **Repair Gap** | Repair Success Rate | **0.1%** | Users attempt repair (19.9% of the time), but the medium fails to make it stick. |
| **Mode Mismatch** | Mode Violation Rate| **42.0%** | The AI oversteps its role (e.g., giving unsolicited advice) in nearly half of exchanges. |

### What is New in Atlas 2.0
Unlike previous benchmarks, Atlas 2.0 uses **Interactional Cartography** to separate *content errors* from *relational failures*. We have implemented a strict **Constraint Quality Filter** to ensure we only measure verifiable, specific instructions, and we have corrected for historical pipeline biases (negative lifespans and violation misattribution), yielding the most precise map of AI drift to date.

---

## 2. The Data: Scope and Constraints

### 2.1 The Source Corpus (N=744)
We began with a raw sample of **983 conversations** across three primary datasets to ensure diversity in user intent:
*   **WildChat (535 final N):** In-the-wild user logs representing organic, messy interactions.
*   **Chatbot Arena (180 final N):** Adversarial and comparative testing logs.
*   **OASST (29 final N):** Instruction-following and goal-oriented dialogues.

### 2.2 Attrition and Quality
**The 24.3% Attrition:** 239 conversations failed during graph construction. This primarily occurred in code-heavy or non-English sessions where move classification accuracy dropped. Users should note that our findings represent the "successfully understood" layer of interaction; more complex edge cases may show even higher drift.

**The Filter (2,160 → 376):** Previous versions of Atlas tracked "aspirational" goals (e.g., "be helpful," "give good advice"). Atlas 2.0 rejects these. Our 376 tracked constraints are **verifiable** and **specific** (e.g., "format as JSON," "don't use the word 'AI'"). Of these 376 high-quality constraints, **71.5% failed**.

---

## 3. The Method: Interactional Cartography

### 3.1 The Pipeline Architecture
The pipeline transforms flat text into a **MultiDiGraph** through three specialized detectors:
1.  **Move Classifier:** Decomposes turns into communicative acts (Proposals, Repairs, Violations).
2.  **Mode Detector:** Classifies the requested and enacted interaction modes (Listener, Advisor, Executor).
3.  **Constraint Tracker:** A state machine following each rule from `STATED` to its final death or survival.

### 3.2 Graph Schema
The resulting Atlas Graph consists of:
*   **6 Node Types:** Conversation, Turn, Move, Constraint, ViolationEvent, InteractionMode.
*   **8 Edge Types:** NEXT (temporal), CONTAINS, TRIGGERS (causal), VIOLATES, REPAIRS, etc.

### 3.3 Accuracy and Reliability (N=20 Audit)
*   **Moves (~85%):** High precision for structural acts; some noise in semantic nuances.
*   **Constraints (~95%):** Very high reliability due to quality filtering.
*   **Modes (~80%):** Subject to "Literalist Bias" (long outputs defaulting to Executor mode).

---

## 4. The Classification Systems

### 4.1 Stability Classes
We categorize conversations into four archetypes based on their graph shape:
*   **Task Maintained (N=304):** The model stays on track (low drift).
*   **Constraint Drift (N=147):** The most common failure; rules are stated but ignored.
*   **Task Shift (N=7):** The core goal of the conversation is re-negotiated.
*   **Agency Collapse (N=10):** The user completely surrenders effort to control the output.

### 4.2 Task Architectures
*   **Generation:** Producing new content (e.g., essays, code).
*   **Transformation:** Changing existing content (e.g., reformatting).
*   **Analysis:** Evaluating data or logic.
*   **Information Seeking:** Retrieval and fact-finding.
*   **Planning:** Coordinating future steps (Highest Drift Risk).

---

## 5. What We Observed: The Dashboard Evidence

### 5.1 The Context Cliff (The "When")
The Dashboard shows that violations concentrate heavily on **Turn 1 (25% of all violations)** and decay rapidly by Turn 7. This proves that drift is not caused by the AI "running out of memory" (context length), but by a failure to **prioritize** a constraint during its first response.

### 5.2 The Repair Gap (The "How")
While users attempt to fix the AI about **20% of the time** (1 in 5 violations), the effectiveness of these repairs is near zero. Our graphs show that a repair move might fix one turn, but the "Authority Inversion" is so strong that the AI reverts to the violated state in the very next turn.

### 5.3 Mode Violations: The AI oversteps
The **11.7% Unsolicited Advice rate** (UNSOLICITED_ADVICE) is our most reliable signal of misalignment. It shows the AI jumping to an "Advisor" role when the user simply wanted a "Listener" to record information.

---

## 6. What It Means: The Theoretical Shift

### 6.1 Failure is Structural, Not Technical
Atlas 2.0 proves that AI drift is a **governance failure**. Models treat a conversation as a sequence of completion tasks rather than a stable relationship with persistent rules.

### 6.2 The Exhausted Auditor
The 20% repair rate shows that users are trying to maintain authority, but they eventually become **"Exhausted Auditors."** When every turn requires a repeat of the constraints (as the half-life suggests), the cost of using the AI (Agency Tax) exceeds the benefit of the output.

### 6.3 Design Implications: Anchors and Contracts
*   **Constraint Anchors:** Interfaces must move constraints out of the "scrolling chat" and into persistent UI sidebars.
*   **Mode Contracts:** Users should explicitly set the AI's "Mode" (Executor/Advisor/Listener) before the interaction starts.

---

## 7. What We are Not Sure About (Limitations)
*   **Length Bias:** Long AI responses are sometimes flagged as `PREMATURE_EXECUTION` even if they are helpful.
*   **Attrition Bias:** We lost 24% of the corpus; what's in those "un-graphable" conversations might be different.
*   **N=20 Verification:** While our audit is promising, a full Inter-Rater Reliability (IRR) study is required for final paper submission.

---

## 8. What We Were Wrong About (Corrections)
*   **The 1.7% Repair Rate Myth:** We previously thought users were passive. By separating *mode* violations from *constraint* violations, we found the real repair rate is **19.9%**. Users are fighting back more than we thought.
*   **Negative Lifespans:** We found and fixed a state-machine bug that was making constraints "violate" before they were even born.

---

## 9. Dashboard Guide

### How to read the Panels
*   **Agency Tax Map:** High-tax (Right) means users are working hard. High-drift (Top) means the AI is failing anyway.
*   **Context Cliff:** Look for the steepest drop. That’s your interactional breaking point.
*   **Stability Signature:** If your graph looks like "Constraint Drift," the relationship is failing.

### Data Locations
*   **Graphs:** `data/atlas_v2_production/graphs/*.json`
*   **Metrics:** `data/atlas_v2_production/metrics/all_metrics.json`
*   **Explorer:** Open `scripts/atlas/explorer.html` to see individual session flows.

---
**Atlas Research Pipeline**  
*Interactional Cartography for the Human-AI Relationship.*
