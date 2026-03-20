# Chapter 6: Making the Invisible Visible — The Atlas Suite and What Comes Next

> **Phase 3 + Future Work | Status: Partially Complete**

---

## The Question

We've shown that roles exist (Chapter 1), that they're instrumentally concentrated (Chapter 2), that conversations structurally collapse (Chapter 3), that the pattern changes in mental health (Chapter 4), and that our own instruments can be as biased as our data (Chapter 5). All of this is diagnostic. The prescriptive question remains:

**What happens when people can see the map?**

Does showing users their roles change anything? Does it activate the foreclosed relational modes? Does it reduce Agency Collapse? Does it matter differently in mental health contexts where the stakes are higher?

## What We've Built So Far

### The Atlas Suite

Five interactive web views that externalize the implicit state of human-AI interaction:

**Findings Dashboard** — Aggregate view. The 97% instrumental concentration, the 70% IS→ES dominance, the 535 mode violations, the constraint survival curve. This is where the "shape of the problem" becomes navigable data rather than hidden state.

**Atlas Global View** — A force-directed meta-graph clustering all 745 canonical conversations by structural similarity. The visual pattern is immediate: a tight central cluster of smooth IS→ES transactions, surrounded by scattered volatile outliers. The emptiness of the map is the finding.

**Cartography Explorer** — Single-conversation deep dive. This is where the 2,817x variance becomes tangible. You can compare the flat trajectory of a clean Q&A exchange against the inward-spiraling knots of a conversation in repair collapse. The constraint tracker shows exactly where violations occur, when repair attempts begin, and why they fail.

**Side-by-Side Comparison** — Direct structural comparison of two conversations with identical role labels but different journeys. The "same destination, different journey" finding ceases to be an abstract statistic and becomes a visible structural difference.

**Mental Health Lab** — A domain-specific extension. It replaces the standard "AI Robot" iconography with "Practitioner" symbols (support agent) and renames "AI Role" to "Practitioner Role." This visual intervention serves to distinguish human-to-human care data from human-to-AI interaction, acknowledging the agency of the human counselor that the standard dashboard would otherwise erase.

### The Context Inventory Interface

A prototype that externalizes the three conflated functions (coordination, memory, execution) into separate, persistent, editable UI elements:

- **Pin to Task** — Extract constraints from conversation text and pin them as persistent items. The AI can reference them; the user can edit them.
- **Context Lens** — Explicit scope selection. The user can see (and modify) what the AI is "paying attention to."
- **Task Shelf** — Multi-task management with independent constraint registries.

### Formative Results (N=20, Preliminary)

*Note: Raw study data has not been archived in the repository. Numbers vary between documents (2.8/5 vs. 2.1/5 baseline control in different drafts). These results should be treated as preliminary pending data provenance verification and archival.*

The initial evaluation showed promising signal:

| Metric | Baseline | Treatment | Delta |
|--------|----------|-----------|-------|
| Perceived control | 2.8/5 | 4.2/5 | +50% |
| Repair attempts per violation | 3.7 | 1.2 | -68% |

The treatment didn't make the AI better — same model, same capabilities. It made the *interaction* better by giving users direct access to the constraint state. Instead of typing "I already told you not to use Python" (adding noise to the context), they could check the constraint registry and see it was missing, then add it directly.

## What Comes Next

### RQ2c: The Visibility Study

The formal evaluation:

- **Design:** Within-subjects comparison (N=20+), standard chat baseline vs. Atlas-augmented interface
- **H1:** Visibility of role assignments and constraint state increases perceived user agency
- **H2:** Externalizing constraint state reduces repair loop frequency
- **H3:** Making the "Instrumental Corridor" visible enables users to deliberately shift toward more expressive or co-constructive modes
- **Metrics:** Perceived agency (Likert), repair attempts per violation, role diversity index, constraint survival rate

This is the test of the prescriptive thesis. If externalized state doesn't reduce Agency Collapse, the theory is incomplete.

### RQ2a at Scale: Full PISCES Dataset

The Phase 4 pilot processed 50 of 423 available multi-turn PISCES sessions. Scaling to the full dataset would give us:
- Enough power to compute reliable constraint dynamics in therapeutic contexts
- A large enough sample to validate the v2 mode taxonomy against human annotations
- Multi-session analysis (some caregivers have multiple sessions) — do roles evolve across sessions?

### Human Baselines: Phase 5

The missing comparison. Every finding so far is about human-AI interaction. But is the 97% instrumental concentration specific to AI, or does it also appear in text-based human-human conversation?

**Planned:** Apply the pipeline to DailyDialog or similar human-human corpora. If human-human text conversations also show high instrumental concentration, the finding is about the *medium* (text chat), not about *AI specifically*. If human-human shows richer role distributions, the finding is about AI interface design.

This is the control condition the research is missing.

### Mode Taxonomy v2 Implementation

The 6-stance taxonomy (DIRECTING, CONSULTING, DISCLOSING, EXPLORING, DELEGATING, ACCOMPANYING) needs to be built into the pipeline alongside v1 — not replacing it, but running in parallel on the same data. Validation requires:

1. Human annotation IRR study (N=100 from general + N=50 from mental health)
2. Comparison of v1 vs. v2 agreement with human coders
3. If v2 improves agreement, promote to default

### Real-Time Intervention

The long-term vision: extending the Atlas Suite from a post-hoc diagnostic tool to a real-time overlay that detects volatility spikes and role rigidity during live conversations, intervening before Agency Collapse occurs.

The constraint tracker already operates at the single-turn level. The technical challenge is making it fast enough for real-time and designing interventions that help without being intrusive.

## The Throughline

| Phase | Question | Answer |
|-------|----------|--------|
| 1 (Ch. 1) | Do roles exist? | Yes, but 97% are instrumental |
| 2 (Ch. 2) | Do they replicate at scale? | Yes, with 2,817x variance |
| 2 (Ch. 3) | Why do conversations fail? | Implicit State Pathology → Agency Collapse |
| 4 (Ch. 4) | Does it generalize to mental health? | Partially — roles shift, AI doesn't |
| 5 (Ch. 5) | Are our instruments trustworthy? | Sometimes not — check them first |
| 3/Future (Ch. 6) | Does visibility help? | Open question |

The research program started with a descriptive question (what's on the map?) and has progressed through explanatory (why do conversations break?) to prescriptive (can we fix it?). The diagnostic instruments are built. The theory is established. The next phase tests whether the diagnosis leads to a cure.

## Key Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Atlas Suite | `atlas_suite/` | 5 views operational (port 8001): Dashboard, Global, Explorer, Side-by-Side, Mental Health Lab |
| Context Engine | `context_engine/` | FastAPI + React prototype |
| PISCES full dataset | MentalChat16K (HuggingFace) | 423 sessions available, 50 processed |
| Mode taxonomy v2 | `theory/mode_taxonomy_v2.md` | Proposed, not implemented |
| ISP theory | `theory/implicit_state_pathology.md` | Complete |

## Journal Notes

- **Date:** February 2026 (ongoing)
- **Biggest open risk:** The visibility study (RQ2c) is the load-bearing test. If making state visible doesn't help, the prescriptive thesis fails and we're left with a powerful diagnostic tool but no intervention.
- **Most exciting possibility:** If visibility activates the foreclosed relational modes (H3), it would mean the instrumental monopoly isn't about what people *want* from AI — it's about what the interface *allows* them to want. That would reframe the entire human-AI relationship literature.
- **Methodological priority:** Human baselines (Phase 5). Without a human-human comparison, we can't distinguish "AI problem" from "text chat problem."
