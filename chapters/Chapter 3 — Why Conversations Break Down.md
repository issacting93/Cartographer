# Chapter 3: Why Conversations Break Down

> **Phase 2 (Theory) | Status: Complete**

---

## The Question

Chapter 2 quantified that 71.5% of constraints fail, repair works less than 1% of the time, and half of sustained conversations end in Agency Collapse. But *why*? Is this a model quality problem that scaling will fix, or is it something more structural?

## The Theory: Implicit State Pathology

We developed a theory rooted in Conversation Analysis (Schegloff, Jefferson, Sacks 1977), Grounding Theory (Clark & Brennan 1991), and information theory.

### The Core Problem

Chat interfaces conflate three distinct functions into a single channel:

1. **Coordination** — "What are we doing?" (task framing, turn-taking)
2. **Memory** — "What did we agree?" (constraints, context, prior decisions)
3. **Execution** — "Do the thing." (output generation)

In human conversation, these functions are supported by persistent mental models, selective attention, and proactive clarification. In LLM interaction, all three must be re-inferred from the context window every single turn.

This creates an information-theoretic trap:

```
User states constraint
    ↓
LLM violates constraint (stateless reconstruction fails)
    ↓
User adds repair text (increases context noise)
    ↓
Signal-to-noise ratio degrades
    ↓
LLM less likely to reconstruct state correctly
    ↓
Another violation
    ↓
[LOOP]
```

Each repair attempt makes the next violation more likely, because repair tokens dilute the original signal. The medium structurally resists correction.

### The Repair Inversion

Human conversation has a strong preference for self-repair — the speaker catches and fixes their own mistakes. This works because humans have introspective access to their communicative intent.

LLMs invert this entirely:
- **Almost never perform same-turn self-repair** (no introspective monitoring)
- **Never perform transition-space repair** (no awareness of potential misunderstanding)
- **Force the user into constant other-initiated other-repair** — the most face-threatening, least efficient repair type

Empirical comparison: humans work ~6x harder at maintaining shared understanding with AI than with other humans (18% repair rate in human-AI logs vs. 3% in human-human task dialogue from MultiWOZ; see `theory/implicit_state_pathology.md` for sources).

### The Authority-Agency Mismatch

The structural result:

- **High epistemic authority**: The AI presents as confident, fluent, knowledgeable
- **Zero volitional agency**: No accountability, no persistent state, no self-correction

Users keep trying to correct because social scripts (inherited from human interaction) say that a confident, articulate partner should be able to incorporate feedback. But corrections never "stick" because there's nowhere for them to persist.

This is **Bounded Personhood** — the AI is attributed the social status of a person (authority, competence) without the structural capacity (agency, memory) that makes personhood functional in interaction.

## The Evidence

### Constraint Lifecycle

From the v2 canonical analysis (N=745 graphs, 376 verified constraints):

| Stage | Rate |
|-------|------|
| Constraint stated | 100% |
| Violated | 71.5% (269/376) |
| Violated at turn 0 | 24.5% (66/269) |
| Repair attempted | 19.9% |
| Repair succeeded | 0.74% (2/271 events) |
| Agency Collapse (5+ repairs) | 50.3% (200/398 conversations) |

The 24.5% turn-0 violation rate is particularly telling. These aren't context-window problems — the AI hasn't run out of memory. It's failing to reconstruct the constraint from the very message it was just given.

### The Spiral Discovery

When we mapped conversations into polar coordinates (angle = time, radius = functional progress), a topological pattern emerged:

- **Healthy conversations**: Outward spirals. Each turn moves into new functional territory.
- **Collapsing conversations**: Inward-spiraling knots. Each turn consumes more effort but yields less progress. The conversation literally winds tighter around the same unresolved problem.

Once a conversation enters the "tight knot" regime (5+ repair attempts), there's an 89.1% collapse rate with less than 11% escape probability.

This is not subjective frustration — it's a measurable, structural phenomenon in interaction space.

### The Threshold Effect

The critical finding for design: the repair loop has a sharp threshold. Conversations that stay below 3 repair attempts mostly recover. Conversations that cross 5 attempts almost never do.

This means the intervention window is narrow. An interface that can detect early-stage repair loops and externalize the failing constraint could prevent collapse before the threshold is crossed.

## The Proposed Solution: Task-Constraint Architecture

The root cause is implicit state. The solution is making state explicit.

**Context Inventory Interface** — a prototype that externalizes the three conflated functions:

1. **Pin to Task** — Extract constraints from conversation and pin them as persistent, visible, editable items
2. **Context Lens** — Explicit scope selection (what is the AI paying attention to?)
3. **Task Shelf** — Multi-task management with independent constraint registries

### Formative Evaluation (N=20, Preliminary)

*Note: This formative study is reported in the project one-pager as "completed," but raw data has not been archived in the repository and specific numbers vary between documents (2.8/5 vs. 2.1/5 baseline control; 4.2/5 vs. 4.6/5 treatment control). The numbers below should be treated as preliminary pending data provenance verification.*

| Metric | Baseline (chat-only) | Treatment (visible constraints) |
|--------|---------------------|-------------------------------|
| User control | 2.8/5 | 4.2/5 |
| Repair attempts per violation | 3.7 | 1.2 |

The treatment group had ~3x fewer repair attempts. Not because the AI was better — the same model was used — but because users could directly edit the constraint registry instead of adding more conversational noise.

## The Answer

Conversations break down because of Implicit State Pathology: stateless systems pretending to maintain state in a medium that structurally resists correction. This isn't a model quality problem. It's an architecture problem. Bigger models with longer context windows will slow the decay but cannot eliminate it, because the fundamental mechanism — repair noise degrading signal-to-noise ratio — operates regardless of window size.

The fix is not a better model. It's a better interface.

## Key Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| ISP Theory | `theory/implicit_state_pathology.md` | Complete |
| Context Engine | `context_engine/` | FastAPI backend + React frontend |
| Constraint tracker | `scripts/atlas/constraint_tracker.py` | Deterministic state machine |
| Spiral visualizations | `atlas_suite/` (Explorer view) | Operational |

## Journal Notes

- **Date:** Mid-late 2025
- **Key insight:** Better prompting doesn't fix this — longer prompts accelerate the problem by consuming more context window. This is counterintuitive and important.
- **Most cited finding:** The 0.74% repair success rate. Reviewers find this number hard to believe until they see the constraint tracker output.
- **What carried forward:** The theory frames everything that follows. Agency Collapse became the dependent variable; Implicit State Pathology became the explanatory mechanism; externalized state became the proposed intervention. The mental health extension (Chapter 4) tests whether this framework generalizes beyond task-oriented contexts.
