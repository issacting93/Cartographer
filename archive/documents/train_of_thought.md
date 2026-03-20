# Refined R1-R9: Theoretically Grounded Framework

---

## R1 — People treat AI as a social actor, but the mechanism requires updating

**Claim:** Human–AI conversation triggers social-cognitive machinery, but CASA alone is insufficient.

**Theoretical Ground:**
- **CASA** (Nass & Reeves, 1996): People apply social rules to computers "mindlessly" when minimal social cues are present.
- **But:** A 2023 replication study in *Nature Scientific Reports* found CASA may only work for emergent technology—participants no longer interact with desktop computers as if they are human.
- **The update:** LLMs *reactivate* CASA because they provide richer social cues than prior systems. Recent work shows GenAI systems simulate behaviors typically associated with human intimacy, empathy, and emotional care, triggering social and relational cues that foster unwarranted trust.

**Your theoretical position:**
-   Roles are *interactional projections*, not AI properties.
-   The projection is **fragile**—it requires ongoing maintenance through the grounding process.
-   When grounding fails repeatedly, the social frame collapses.

**Key citations:**
-   Nass, C., Steuer, J., & Tauber, E. R. (1994). Computers are social actors. *CHI '94*
-   Reeves, B., & Nass, C. (1996). *The Media Equation*
-   de Melo et al. (2023). The CASA theory no longer applies to desktop computers. *Scientific Reports*

---

## R2 — Repair is the mechanism; collapse is the failure mode

**Pivoting from "role taxonomies" to "interactional health"**

**Theoretical Ground:**
Conversational repair is the process people use to detect and resolve problems of speaking, hearing, and understanding. Through repair, participants in social interaction display how they establish and maintain communication.

**Key insight from CA:**
-   Repair is a "self-righting mechanism" in conversation (Schegloff, Jefferson, & Sacks, 1977).
-   Participants in conversation seek to correct the trouble source by initiating and preferring self repair.
-   Human-human repair has a *preference structure*: self-repair is preferred over other-repair.

**The problem in human-AI:**
-   LLMs cannot *self-repair* in the CA sense—they lack awareness of their own trouble sources.
-   Users must initiate *other-repair* (corrections), but the system doesn't "hear" them structurally.
-   This inverts the natural preference structure.

**Your key definition:**
-   **Agency Collapse:** A failure state where the user's capacity to direct the interaction degrades *because repair mechanisms structurally fail*.
-   **Signatures:** Repeated failed repairs, tone degradation, specificity collapse.

**Key citations:**
-   Schegloff, E. A., Jefferson, G., & Sacks, H. (1977). The preference for self-correction in the organization of repair in conversation. *Language, 53*(2), 361-382
-   Schegloff, E. A. (1992). Repair after next turn: The last structurally provided defense of intersubjectivity in conversation. *American Journal of Sociology, 97*(5), 1295-1345

---

## R3 — Grounding fails because state is implicit

**Connecting repair failure to architectural cause**

**Theoretical Ground:**
Clark & Brennan's (1991) grounding theory: Grounding comprises the collection of "mutual knowledge, mutual beliefs, and mutual assumptions" that is essential for communication. Successful grounding requires parties to coordinate both the content and process.

**The grounding criterion:**
The contributor and partners mutually believe that the partners have understood what the contributor meant to a criterion sufficient for current purposes.

**Why LLMs fail at grounding:**
1.  LLMs are stateless by design—they don't remember anything between turns unless explicitly told to.
2.  The context window is the memory. Managing conversation context is the hidden backbone of effective Conversational AI.
3.  Common ground must be *re-inferred* each turn from the scrolling context window.
4.  As conversation grows, signal-to-noise ratio degrades.

**Your mechanism:**
-   Human-human: Common ground is *accumulated* and *maintained* through grounding acts.
-   Human-AI: Common ground must be *reconstructed* each turn from implicit context.
-   Reconstruction is lossy $\rightarrow$ drift is structural.

**Key citations:**
-   Clark, H. H., & Brennan, S. E. (1991). Grounding in communication. In *Perspectives on Socially Shared Cognition*
-   Clark, H. H., & Schaefer, E. F. (1989). Contributing to discourse. *Cognitive Science, 13*, 259-294

---
**Connecting to prior HCI work:**
-   Both breakdowns and current recovery processes decrease peoples' satisfaction, trust, and willingness to use the chatbot.
-   Your contribution: Quantifying this at scale and identifying the structural trap.

---

## R7 — Mechanism: Implicit State Pathology

**Why the Repair Loop happens**

**The argument (explicit causal chain):**
1.  **Architectural fact:** Conversational interfaces have no explicit state representation.
2.  **Processing constraint:** The model must re-infer task, constraints, and common ground from context each turn.
3.  **Information-theoretic problem:** As conversation grows, the "signal" (original intent, constraints) gets buried in "noise" (repair attempts, restatements).
4.  **The trap:** User adds *more* text to fix it $\rightarrow$ adds *more* noise $\rightarrow$ model loses signal $\rightarrow$ user adds *more* text.

**Your term:** *Implicit State Pathology*—relying on the context window to hold state that should be explicit and persistent.

**Connecting to dialogue systems literature:**
-   Dialogue State Tracking (DST) research shows that LLMs have significant limitations—once input exceeds the context window, older content is truncated or discarded.
-   Contemporary conversational models tend to rely predominantly on recent dialogue history when formulating responses. This predisposes them to produce content that may contradict earlier parts of the dialogue.

**This explains why:**
-   Better prompting doesn't fix the problem (it adds more text).
-   Users can't "learn" their way out (the interface provides no feedback on state).
-   The problem gets worse, not better, over time.

---

## R8 — Design Implication: Externalize the State

**Prescriptive framework**

**Claim:** If implicit state causes drift, then externalizing state should reduce it.

**Proposed: Task-Constraint Architecture (TCA)**

| Implicit (Current) | Externalized (Proposed) |
| :--- | :--- |
| Role inferred from context | Role declared as mode/mandate |
| Constraints scattered in history | Constraint registry (pinned, inspectable) |
| Task scope ambiguous | Task inventory with shelving/lensing |
| Common ground reconstructed | Common ground persisted and visible |

**Theoretical support:**
-   Clark & Brennan (1991) note that grounding costs vary by medium—visual co-presence reduces effort.
-   Making state visible creates the equivalent of "visual co-presence" for computational common ground.
-   Repair strategies that aid with self-repair, by exposing the chatbot's understanding model, were generally ranked highly—they provide actionable resources for the user to resolve the breakdown.

**Status:** This is a *design conjecture*, not yet validated empirically.

---

## R9 — Limitations and Broader Contribution

**What you're NOT claiming:**
-   That your feature set captures all relevant dimensions.
-   That state externalization will definitely solve collapse (it's a hypothesis).
-   That this extends to multi-session or organizational context (future work).

**What you ARE claiming:**
-   Repair mechanisms from CA apply to human-AI interaction, but are structurally impaired.
-   Agency Collapse is a widespread, identifiable failure mode (50% of conversations).
-   The "Repair Loop" is a structural trap with near-zero escape probability.
-   Implicit state is a plausible mechanism explaining why repair fails.
-   Interactional Cartography is a viable diagnostic method.

**Broader contribution for CHI:**

> "Misalignment is not only a model behavior problem—it is a UI architecture problem. Current conversational interfaces lack the state representations needed for the grounding process that makes human communication self-correcting."

---

## R10 — The Visual Proof: Polar Layouts & Repair Loops

**The "Spiral" Discovery:**
*   **Observation:** When mapped in a clockwise polar layout (Time=Angle, Radius=Function), "Repair Loop" conversations form tight, inward-spiraling knots.
*   **Contrast:** Healthy conversations spiral *outward* (exploring new territory).
*   **Significance:** This provides **topological proof** of Agency Collapse. It is not just a statistical correlation; it is a visible structural trap in the interaction space.
*   **Atlas Suite:** The tool that makes this visible (Explorer, Global View) is the "microscope" that allowed us to see the pathogen (Implicit State Pathology).