# Chapter 2: Building the Taxonomy from Data

> **Phase 2 (v2) | N=2,577 | Status: Complete**

---

## The Question

Chapter 1 proved roles exist at N=507. But that corpus was small, the methodology was compromised (six audit failures), and the taxonomy was theoretically derived, not empirically validated. Could we scale up by 5x, fix the methodology, and confirm whether the same patterns held — or if they were artifacts of a small, noisy dataset?

## What We Built

A 7-stage computational pipeline that transforms raw conversations into annotated interaction graphs:

1. **Move Classifier** — Tags each turn with one of 13 communicative act types (ASSERT, REQUEST, SUGGEST, CONSTRAIN, REPAIR, etc.). Hybrid architecture: regex patterns catch unambiguous cases, LLM fallback handles ambiguity.
2. **Mode Detector** — Classifies each turn's interaction mode: LISTENER (providing context), ADVISOR (seeking evaluation), EXECUTOR (requesting deliverable).
3. **Constraint Tracker** — Deterministic state machine that identifies user constraints, tracks whether the AI respects or violates them, and monitors repair attempts.
4. **Graph Builder** — Constructs a NetworkX MultiDiGraph where nodes are turns, moves, and constraints; edges encode violations, repairs, and mode transitions.
5. **Metrics Computer** — Computes 8 CUI diagnostic metrics per conversation (constraint survival, repair success, mode alignment, affect volatility, etc.).
6. **Visualization** — Generates polar trajectory plots and 3D terrain maps.
7. **Export** — Packages everything into standardized JSON for downstream analysis.

The role classification runs separately via SRT (Social Role Theory) classifier: each conversation is classified into one of the 12 roles from Chapter 1, plus 8 interaction dimensions (emotional tone, interaction pattern, conversation purpose, etc.). This two-track architecture — pipeline for dynamics, SRT for statics — was a deliberate design decision to prevent the circularity that killed v1.

### The Evidence Architecture

After the v1 circularity disaster, we established a hard rule:

- **30 evidence features** — Derived from text, computed independently of role labels. R² < 0.01 with labels. Used for all empirical claims.
- **2 viz-only features** — Role-derived spatial coordinates. Used only for terrain positioning. Never cited as evidence.

This separation is enforced by acceptance tests (A/B/C) that must PASS before any quantitative claim enters the paper.

## What We Found at Scale

### The Instrumental Monopoly Confirmed

| Metric | v1 (N=507) | v2 (N=2,577) |
|--------|-----------|-------------|
| Instrumental human roles | 98.8% | 97.0% |
| IS→ES dominant dyad | ~65% | 70.0% |
| Expert-System AI responses | 64.8% | 77.6% |

The finding replicated. At 5x scale across three independent datasets (WildChat, Chatbot Arena, OASST), 97% of humans approach AI as information-seekers, providers, or directors. Only 3% venture into expressive territory.

The IS→ES dyad (Information-Seeker to Expert-System) accounts for 70% of all conversations. The entire social-relational quadrant of the taxonomy — Collaborator, Social-Expressor, Relational-Peer on the human side; Co-Constructor, Social-Facilitator, Relational-Peer on the AI side — is functionally empty.

### The Variance Ratio Scaled Up

In v1, we found 2,030x variance in emotional trajectories within the same role pair. In v2, with better affect measurement (503 unique PAD values vs. 53), this became **2,817x**.

The finding didn't attenuate with scale — it got stronger. Two people who both ask "How do I sort a list in Python?" (same role pair: IS→ES) can have emotional experiences that differ by nearly three orders of magnitude. One has a smooth, flat affect trajectory. The other has volatile spikes, repair attempts, frustration.

Role labels describe the destination. They completely miss the journey.

### Constraint Failure

*Note: These empirical results are the evidentiary foundation for the Implicit State Pathology theory developed in Chapter 3.*

The constraint tracker revealed the mechanism behind the variance:

- **71.5% of user constraints are violated** (269/376 verified constraints)
- **Mean time-to-violation: 2.5 turns** (median: 1 turn)
- **24.5% fail at turn 0** — the very first AI response ignores what the user asked
- **Repair success rate: 0.74%** (2/271 repair events)
- **Agency Collapse: 50.3%** of sustained conversations (200/398)

This is the structural mechanism. Users set constraints. The AI violates them almost immediately. Users try to repair. Repair almost never works. After 5+ repair attempts, 89.1% of conversations end in collapse.

### The Random Forest Sanity Check

To verify the taxonomy had real discriminative power, we trained a Random Forest classifier on the 16 role-pair classes using only the 30 evidence features (no role-derived features).

**Accuracy: 71.6%** (chance = 6.2%, 16 classes).

The features that mattered most for classification came from the Affect channel (39.3%), Divergence (21.6%), Dynamics (16.5%), and Expressiveness (15.4%). Structure contributed only 7.2%.

This confirmed that role pairs produce genuinely different conversational signatures — the taxonomy is capturing something real, not just projecting labels onto noise. But 71.6% is also honest: nearly 30% of conversations don't cleanly fit their assigned role pair. The taxonomy compresses reality; it doesn't define it.

## What We Built to See It

The **Atlas Suite** (BLOOM Design System) — four interactive web views:

- **Findings Dashboard** — Aggregate KPIs, role distributions, constraint survival
- **Atlas Global View** — Force-directed meta-graph of all 745 canonical conversations, clustered by structural similarity
- **Cartography Explorer** — Single-conversation deep dive with graph topology, affective trajectory, repair loops
- **Side-by-Side Comparison** — Direct structural comparison of two conversations

The suite makes visible what the chat interface hides: the 97% instrumental concentration, the constraint decay, the repair spiral topology. It turns the diagnosis into an instrument.

## The Answer

The taxonomy replicates at scale. The instrumental monopoly is real and stable across datasets. The variance within role pairs is even larger than we thought. And the mechanism is clear: constraint violation → failed repair → agency collapse.

The question that emerged: is this a universal property of human-AI interaction, or is it specific to the task-oriented contexts that dominate these corpora?

## Key Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| v2 corpus | `data/atlas_canonical/` | N=745 graphs |
| Pipeline | `scripts/atlas/run_pipeline.py` | 7-stage, hybrid regex+LLM |
| SRT classifier | `scripts/classify_roles_srt.py` | 12-role taxonomy |
| Verified stats | `data/v2_unified/reports/verified_stats.json` | 60/60 claims validated |
| Atlas Suite | `atlas_suite/` | 4 views operational |
| Acceptance tests | `scripts/run_acceptance_tests.py` | A/B/C PASS |

## Journal Notes

- **Date:** Late 2025 – Early 2026
- **Key methodological lesson:** Separate your evidence channel from your classification channel, and test the separation formally. The acceptance test framework (A/B/C) caught several near-misses where label-derived features were creeping into empirical claims.
- **Biggest surprise:** The variance ratio getting *larger* at scale. We expected it to regress toward the mean. It didn't.
- **What carried forward:** The pipeline, the constraint tracker, the evidence architecture, and the question: does the instrumental monopoly hold outside task-oriented contexts?
