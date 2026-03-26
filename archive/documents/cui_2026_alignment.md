# CUI 2026 Strategic Alignment: Cartography & Agency Collapse

## Research Approach
**Literature-grounded text analysis.** We are not conducting user studies. Instead, we build a theoretical framework from Conversation Analysis literature (grounding, repair, agency) and validate it empirically through automated analysis of 1,383 existing human-LLM conversation logs. The paper's argumentative structure is:

1. **Theory** (from literature): Grounding requires mutual evidence of understanding (Clark & Brennan). Repair is the mechanism for maintaining it (Schegloff et al.). Architectures relying on **unstructured state** structurally undermine both.
2. **Method** (Atlas pipeline): Operationalize these CA concepts as computable graph metrics — constraint outcomes, repair density, time-to-violation.
3. **Evidence** (from data): Show that the theoretical predictions hold at scale — 69% violation, 1% repair success, 1-turn median failure.

---

## 1. Core Alignment to CUI 2026 Theme

The 2026 theme is **"Conversational AI: Agency and Identities!"** — this paper addresses **agency** directly:

* **Agency:** We quantify how user agency erodes when constraints are violated and repair fails. The "Abandonment Default" (users stop trying to correct the system) is a measurable loss of conversational agency.
* **Identities (light touch):** The 14% ambiguity rate — constraints neither violated nor acknowledged — reveals that LLMs don't make their compliance state observable. Users cannot distinguish a compliant agent from a silently non-compliant one. This is an identity-legibility problem.

---

## 2. Key Deadlines & Submission Strategy

**Deadline: Thursday, April 9, 2026 (23:59 AoE)** for Short Papers, WiPs, and Provocations.

> [!IMPORTANT]
> **No Simultaneous Submission:** CUI rules prohibit submitting the same work to multiple tracks. Choose one.

### Target Track: Short Papers & WiP (Extended Abstract)

* **Goal:** Present early-stage research or late-breaking work suitable for interactive discussion.
* **Format:** 
    * **Length:** Approx. 3,000 words (including figures/tables/appendices; excluding refs).
    * **Template:** ACM Primary Article Template (LaTeX or Word). One-column for Word.
    * **Anonymization:** Doubly-anonymized is mandatory.
    * **Open Access:** Published as "Extended Abstract" (No APC charge under new ACM model).
* **Strength:** The findings are striking enough to generate discussion (69% violation, 1% repair) even without a user study.

---

## 3. CUI-Native Research Mapping

| Contribution | CUI Research Topic | Framing |
| :--- | :--- | :--- |
| **Atlas diagnostic framework** | Evaluation Methods | A CA-grounded methodology for measuring grounding failure in text-based CUIs via constraint tracking, repair density, and time-to-violation. |
| **Agency Collapse (empirical)** | Fundamental CUI Research | Quantified evidence that users abandon repair in LLM dialogue — only 5.6% of constrained conversations contain any repair attempt, and it succeeds 1% of the time. |
| **Abandonment Default pattern** | Interaction Patterns | The finding that users treat constraint violation as terminal rather than repairable — the opposite of human-human conversation norms (Schegloff et al. 1977). |
| **Design implications** | Design Principles | Argument for externalized, editable constraint state and decoupled coordination/execution channels — derived from the diagnostic findings, not yet validated. |

---

## 4. Reviewer-Centric Strategy

### What reviewers will look for (and how we address it)

| Reviewer concern | Our answer |
| :--- | :--- |
| "Is this really about CUI, not just LLM benchmarking?" | The contribution is about **conversational interaction** — grounding, repair, agency — not model accuracy. The metrics are interactional (repair density, patience), not performance metrics. |
| "Where are the participants?" | This is **secondary analysis of existing conversation logs**, not a user study. State this explicitly in the method section. No demographics or ethics approval needed, but be clear about data provenance. |
| "Are claims too strong for the evidence?" | Frame as: "These findings suggest..." / "This diagnostic framework reveals..." Not: "We prove..." The design implications are hypotheses, not validated solutions. |
| "How is repair defined?" | Ground it in CA literature: Schegloff et al. (1977) for self-correction preference, Ashktorab et al. (2019) for chatbot repair strategies. Show theoretical lineage. |
| "LLM-only extraction — is that valid?" | Disclose as limitation. Frame the 69% violation rate as a **lower bound** (Jaccard matching misses ~48.6% of constraint-violation pairs). |
| "Why should I care about these numbers?" | Compare to human-human norms: repair is natural and frequent in human conversation. Its near-absence in LLM dialogue is the anomaly that demands explanation. |

### Key framing principles

* **Foreground the conversation, not the model.** This is about what happens interactionally when grounding fails, not about whether GPT-4 is "good."
* **Theory first, data second.** The literature predicts these failures; the data confirms the prediction. This is stronger than data-first empiricism for a CUI audience.
* **Modest claims, striking data.** Let the numbers speak (69%, 1%, 1 turn) while keeping the framing appropriately preliminary.

---

## 5. Strategic Refinements (17-Day Sprint)

To address potential reviewer pushback, prioritize these pivots before the April 9 deadline:

| Pivot | Shift | Why? |
| :--- | :--- | :--- |
| **Architectural** | "Stateless" $\rightarrow$ **"Unstructured State"** | Acknowledge context window *is* state; critique its flattened, unstructured nature (Grosz & Sidner 1986). |
| **Psychological** | "Abandonment" $\rightarrow$ **"Behavioral Absence"** | Hedge psychological claims; report the *observed* lack of repair turns instead. |
| **Grounding** | "Clark & Brennan" $\rightarrow$ **"Traum & Brennan"** | Acknowledge partner modeling (Brennan 1998) and context-dependent grounding acts (Traum 1994). |
| **Methodological** | LLM Extraction $\rightarrow$ **Human Validation** | Conduct a 100-convo human spot-check to address "circularity" in extraction. |
| **Operational** | Success $\rightarrow$ **Immediate Success** | Define "Success" as compliance in the *immediately following* turn. |

---

## 6. Submission Checklist (Logistics)

| Requirement | Details | Status |
| :--- | :--- | :--- |
| **Anonymization** | Remove all author names, affiliations, and explicit project refs. | [ ] |
| **Word Count** | < 3,000 words (not including references). | [ ] |
| **Template** | ACM Primary Article Template (MS Word One-Column or LaTeX). | [ ] |
| **Artifacts** | Consider submitting the Atlas pipeline/dataset as a supplementary artifact. | [ ] |
| **Video (Opt)** | 1-minute video showing Atlas visualizations (MP4/MPEG). | [ ] |
| **Deadline** | Thursday, April 9, 2026 (AoE). | [ ] |
| **Accessibility** | Follow SIGCHI Guide (alt-text for all figures). | [ ] |
