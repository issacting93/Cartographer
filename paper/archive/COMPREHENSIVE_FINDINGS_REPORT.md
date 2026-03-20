# Comprehensive Findings Report: The Research Program (R1-R9)

This report synthesizes the complete research arc, connecting the phenomenological findings of *Conversational Cartography* (Phase 1) with the structural diagnosis of *Agency Collapse* (Phase 2) and the proposed design interventions (Phase 3).

## 1. Executive Summary: The Research Program

We investigate why human-AI conversations fail. Our research program spans three phases:

| Phase | Study | Question | Method | Output |
|-------|-------|----------|--------|--------|
| **Phase 1** | Conversational Cartography | Do dynamics matter more than categories? | Trajectory clustering (PAD) | **83% dynamics, 17% categories**<br>Role labels do not predict experience. |
| **Phase 2** | Agency Collapse | What drives those dynamics? | Structural clustering (repair) | **50% collapse rate**<br>Repair Loops drive volatility. |
| **Phase 3** | Intervention | Can we reduce collapse? | Design Proposal (CII) | **Context Inventory Interface**<br>Externalizing state to fix repair. |

---

## 2. Theory: Why Conversations Collapse (R1-R4)

We argue that users import functional expectations from human conversation that the LLM architecture cannot fulfill, leading to structural failure.

### R1 & R2: The Broken Repair Mechanism
*   **Expectation:** Human conversation is self-righting (Schegloff et al., 1977).
*   **Reality:** LLMs lack the machinery for self-repair or structural acknowledgement.
*   **Result:** Users are forced into the dispreferred position of *other-repair*, which paradoxically adds noise to the context window (R3).

### R3: Implicit State Pathology
*   **Mechanism:** LLMs must *reconstruct* common ground from the context window each turn rather than *accumulating* it.
*   **The Trap:** Repair attempts add tokens -> dilute signal -> increase error probability -> require more repair.

### R4: Authority-Agency Decoupling
*   **Mechanism:** The interface presents high *authority* (confidence) but low *agency* (accountability/corrigibility).
*   **The Trap:** Users keep trying to correct the "expert" because social scripts say it should work, but the lack of agency means corrections never "stick."

---

## 3. Phase 1 Findings: The Phenomenological Signal (R5)

**Source:** *Conversational Cartography* (N=562)

*   **Finding 1: Dynamics > Categories.** Trajectory features (spatial/emotional movement) account for **83.3%** of cluster separation. Role labels account for only 16.7%.
*   **Finding 2: "Same Role, Different Journey".** Conversations with identical role labels show 41x-82x variance in trajectories.
*   **Finding 3: Volatility is Diagnostic.** High PAD volatility (peaks/valleys) signals breakdown, initially interpreted as "emotionality."

---

## 4. Phase 2 Findings: The Structural Diagnosis (R6)

**Source:** *Agency Collapse* (N=863)

We re-analyzed interaction through a structural lens, identifying the mechanism behind the volatility.

*   **Finding 1: High Collapse Rate.** **50.4%** of sustained conversations end in Agency Collapse.
*   **Finding 2: The Repair Loop (Cluster 0/3).**
    *   **N=258 (30% of corpus).**
    *   **Collapse Rate: 89.1%.**
    *   **Signature:** 5+ repair attempts. Once entered, escape is rare (<11%).
*   **Finding 3: The Visual Signature (Polar Layout).**
    *   Using the **Atlas Explorer's Polar Layout**, we observe that "Repair Loops" form tightening spirals.
    *   Unlike functional conversations which progress outward or linearly, collapsed conversations loop back on themselves, physically trapping the user in a "gravity well" of prior constraints.

*   **Finding 4: Authority Escalation.** Increasing use of authority-challenging language ("you're wrong", "stop") predicts collapse.

**Synthesis:** The "volatility" from Phase 1 is the surface manifestation of the "Repair Loop" from Phase 2.

---

## 5. Synthesis: The Two Mechanisms of Failure (R7)

We identify two distinct failure modes driven by the R3/R4 interaction:

1.  **Metric of Friction (Agency Tax):** The ratio of repair effort to violation.
2.  **Active Failure (The Repair Loop):** High Agency Tax. User fights the system, corrections don't persist (R3), user escalates (R4), collapse ensues.
3.  **Passive Failure (Acceptance):** User recognizes the cost of repair is too high and surrenders control, accepting hallucinated or degraded output.

---

## 6. Proposed Intervention: Context Inventory Interface (R8)

**Diagnosis:** If the problem is *Implicit State* and *Authority Decoupling*...
**Prescription:** We must *Externalize State* and *Calibrate Authority*.

**Proposed Features:**
*   **Constraint Anchors:** Pinned, visible state to fix R3 (persistence).
*   **Explicit Checkpoints:** Structural acknowledgment to fix R2 (repair termination).
*   **Authority Calibration:** Visible uncertainty to fix R4 (users stop over-trusting).

---

## 7. Conclusion (R9)

Many human-AI interaction failures attributed to "model capability" are actually **structural failures of the chat interface**. 
*   **Phase 1** proved that static roles don't explain the variance.
*   **Phase 2** identified the Repair Loop as the structural cause.
*   **Phase 3** proposes the Context Inventory Interface as the architectural solution.

This research program moves the field from *describing* interactional failures to *diagnosing* and *fixing* them at the interface level.
