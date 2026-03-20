# CUI 2026 Short Paper Outline: Making the Implicit Explicit

**Proposed Title:** *Making the Implicit Explicit: A Diagnostic Framework for Observing Grounding Failure in CUIs*

**Target Length:** 4–6 pages + references (ACM Short Paper Format)
**Goal:** Present the **Atlas Suite** (Dashboard + Explorer) as a tool for observing and diagnosing interactional drift.

## 1. Introduction: The Visibility Gap (0.5 - 1 page)
*   **The Problem**: Conversational logs are "flat"—they show what was said, but hide the interactional state.
*   **The Consequence**: **Grounding Failure** (Agency Collapse)—when researchers can't easily see *why* or *when* the breakdown started.
*   **The Solution**: Introducing **Atlas**, a visualization suite that maps the "Implicit State" of human-AI dialogue.

## 2. Methodology: Interactional Cartography (1 page)
*   **The Pipeline**: Briefly describe the textual-to-structural transformation.
    *   **Move Classification**: 13-category CA-grounded taxonomy.
    *   **Mode Detection**: Identifying Listener/Advisor/Executor shifts.
    *   **Constraint Survival Analysis**: State machine following each rule.
*   **The Graph**: Explain the MultiDiGraph representation (nodes = events, edges = causal links).

## 3. The Atlas Suite (The Contribution) (1.5 - 2 pages)
*   **The Dashboard (Macro-Scale)**:
    *   Visualizing **Repair Load vs. Constraint Survival** across the N=745 canonical corpus.
    *   Identifying the "Interactional Cliff" where the load exceeds the utility.
*   **The Session Explorer (Micro-Scale)**:
    *   Tracing the "Implicit State" turn-by-turn.
    *   Visualizing **Repair Cascades** and **Mode Mismatches** (`PREMATURE_EXECUTION`).
*   **Design Rationale**: Why we chose graph-based trajectories over linear text (Persistence of state).

## 4. Case Study: Diagnosing Grounding Failure (1 page)
*   **Demonstration**: Use the canonical data to show how Atlas "catches" failures.
    *   Example 1: The **Repair Cascade Trap** (Visualizing the 89.1% collapse rate).
    *   Example 2: **Initiative Inversion** (Visualizing the 42% mode violation rate).
*   **Observation**: How the tool reveals that failure is structural (**Stateless Architecture**), not just linguistic.

## 5. CUI Value & Discussion (0.5 page)
*   **Diagnostic Power**: Identifying "Exhausted Auditors" via **Repair Density** metrics.
*   **Design Implications**: Moving from "chat-only" to **Externalized Grounding**.
*   **Future Work**: Building dynamic feedback loops using Atlas-style state tracking.

## 6. Conclusion (0.25 page)
*   Summarize the shift from "watching chat" to **"observing state"** in CUIs.
