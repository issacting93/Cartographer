# Core Research Topics: CUI 2026

This document maps the theoretical pillars, interaction dynamics, and design interventions that define the "Tasks, Not Turns" project.

## 1. Theoretical Pillars

### Agency as Architecture
**Core Concept:** Agency is not a psychological trait of the user, but a structural property of the interface. In chat-only systems, agency collapses because the interface architecture imposes high costs on maintaining intent.
*   **Role Drift:** Roles are permissions over task state. When state is weak, roles drift from *Director/Executor* to *Accepter/Proposer*.
*   **Authority Inversion:** Without explicit constraints, the AI (as the generator) gains de facto decision power, while the human (as the filter) is reduced to a reactive validator.

### The Agency Tax
**Core Concept:** The continuous cognitive effort required to maintain constraints in a system that naturally forgets them.
*   **Restatement Friction:** The specific cost (typing, constructing) of repairing context.
*   **Economic Maintenance:** Users act as "rational agents" who abandon precision when the "tax" of repair exceeds the utility of the output.

### Task State vs. Dialogue Flow
**Core Concept:** The fundamental mismatch between linear conversation strings and structured task perseverance.
*   **Epistemic Opacity:** In chat, users cannot *see* what the system knows. State is hidden in the scroll.
*   **Task Integrity:** Without artifacts, tasks lose their boundaries and "leak" into adjacent topics or optimizations.

---

## 2. Interaction Dynamics

### Constraint Drift (The Phantasm)
**Findings:** Analysis of N=983 interactions reveals that total collapse is rare (2.8%). The dominant failure mode is **Drift (48.6%)**.
*   **The Repair Loop:** Users are stuck in a cycle of `Violation -> Repair -> Drift`.
*   **Implication:** Users *want* to be in control, but the interface fights them. They are paying a high tax to stay afloat.

### The Exhausted Auditor
**Core Concept:** An "Irony of Automation" effect where the user is relieved of execution work but burdened with high-stakes monitoring work.
*   **Fragility:** Monitoring fluent prose for subtle constraint violations is cognitively demanding and prone to fatigue.
*   **Result:** Users become "sidelined" observers rather than active directors.

### The Moral Hazard of Fluency
**Core Concept:** Textual fluency masks competence gaps.
*   **Trust Calibration:** Users conflate "good sentence" with "correct logic."
*   **Passive Attractor:** It is easier to say "yes" to a fluent (but wrong) suggestion than to halt the flow and correct it.

---

## 3. Design Interventions (The Context Inventory)

### Task Object Model
**Definition:** A persistent, manipulable representation of a goal and its constraints, separate from the conversation stream.
*   **Lifecycle:** Tasks are created, suspended, resumed, and completed (unlike infinite chat logs).
*   **Reification:** Turning ephemeral tokens (words) into durable things (nodes).

### External Representations (Distributed Cognition)
**Theory:** Offloading memory to the environment.
*   **Recognition vs. Recall:** Users should *recognize* active constraints on a shelf, not *recall* them from memory.
*   **Shared Reference:** The Task Object acts as a "common ground" anchor for both human and AI.

### Governable Context
**Mechanism:** Giving users runtime control over the context window.
*   **Context Lens:** Explicitly selecting *which* constraints apply to the current turn.
*   **Permissioning:** Moving from "context implies consent" to "context requires consent."

---

## 4. Methodology & Evaluation

### Scripted Probes (Forced Violation)
**Method:** Using a standardized breakdown to measure repair behavior.
*   **Rationale:** To measure agency, we must threaten it. A perfectly compliant AI reveals nothing about the user's ability to recover control.
*   **Metrics:** Repair Time, Restatement Count, and Role Reassignment (keystrokes vs clicks).