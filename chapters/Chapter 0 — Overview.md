# Chapter 0: Overview — Interactional Cartography for Human-AI Conversation

> **Research Program | 2025–2026 | Status: Active**

---

## The Program in One Sentence

We built instruments to map what happens between humans and AI in conversation, discovered that the territory is almost entirely instrumental and structurally prone to collapse, and are now testing whether making the map visible changes the territory.

## The Throughline

| Phase | Chapter | Question | Answer |
|-------|---------|----------|--------|
| 1 (v1) | Ch. 1 | Do human-AI roles exist? | Yes, but 97% are instrumental |
| 2 (v2) | Ch. 2 | Do they replicate at scale? | Yes, with 2,817x within-role variance |
| 2 (theory) | Ch. 3 | Why do conversations fail? | Implicit State Pathology → Agency Collapse |
| 4 | Ch. 4 | Does it generalize to mental health? | Partially — human roles shift, AI doesn't |
| Cross-cutting | Ch. 5 | Are our instruments trustworthy? | Sometimes not — check them first |
| 3/Future | Ch. 6 | Does visibility help? | Open question |

## Core Concepts

**Implicit State Pathology (ISP):** Chat interfaces conflate coordination, memory, and execution into a single channel. Because LLMs rely on **unstructured state** (the context window), all three must be reconstructed every turn from context that degrades with each repair attempt.

**Agency Collapse:** The terminal state of failed repair. After 5+ repair attempts, 89.1% of conversations end in collapse. Observed in 50.3% of sustained conversations (200/398).

**The Instrumental Monopoly:** 97% of human roles in general-purpose AI conversation are purely task-oriented (Information-Seeker, Provider, Director). The social-relational quadrant of the role taxonomy is functionally empty.

**The Relational Mismatch:** Even when humans bring expressive intent (as in mental health), AI responds instrumentally. Expert-System + Advisor accounts for 70-82% of AI responses across all domains studied.

## Key Numbers (All Script-Verified)

All statistics below are computed by `scripts/compute_verified_stats.py` and stored in `data/v2_unified/reports/verified_stats.json`. No hand-transcribed numbers appear in the chapters.

| Metric | Value | Source |
|--------|-------|--------|
| Corpus size | N=2,577 (2,576 with roles) | verified_stats.json |
| Instrumental human roles | 97.0% | verified_stats.json |
| IS→ES dominant dyad | 70.0% | verified_stats.json |
| Variance ratio (IS→ES) | 2,817x | verified_stats.json |
| RF role-pair accuracy | 71.6% (16 classes, chance=6.2%) | verified_stats.json |
| Constraint violation rate | 71.5% (269/376) | verified_stats.json |
| Mean time-to-violation | 2.5 turns (median: 1) | verified_stats.json |
| Turn 0 violations | 24.5% (66/269) | verified_stats.json |
| Repair success rate | 0.74% (2/271 events) | verified_stats.json |
| Agency Collapse rate | 50.3% (200/398) | verified_stats.json |

## Methodological Commitments

These were learned the hard way (see Chapter 5):

1. **No label-derived evidence.** 30 evidence features (R² < 0.01 with role labels) for all empirical claims. 2 viz-only features for rendering. Enforced by acceptance tests.
2. **No hardcoded statistics.** All figures and claims read from verified_stats.json.
3. **Check the instrument.** When a metric gives an extreme value, test the instrument before celebrating the finding.
4. **Separate classification from dynamics.** SRT classifier for static roles; pipeline for temporal dynamics. Never mix the channels.

## Reading Order

The chapters are designed to be read sequentially, but can be entered at different points:

- **Start here if you want the findings:** Chapter 2 (scale replication) → Chapter 3 (mechanism)
- **Start here if you want the methodology:** Appendix A (Methods) → Chapter 2
- **Start here if you want the theory:** Chapter 3 (ISP) → Chapter 5 (instrument critique)
- **Start here if you want the mental health extension:** Chapter 4 (requires Ch. 2-3 context)
- **Start here if you want the design intervention:** Chapter 6 (requires Ch. 3 context)

## Repository Structure

| Directory | Contents |
|-----------|----------|
| `chapters/` | This document and all chapter narratives |
| `scripts/` | Pipeline code, verified stats computation, analysis scripts |
| `data/v2_unified/` | Canonical v2 corpus (2,577 conversations) |
| `data/atlas_canonical/` | 745 interaction graphs with constraint tracking |
| `data/mental_health/` | Single-turn (N=100) and multi-turn (N=50) MH data |
| `theory/` | ISP theory, related work, mode taxonomy v2 proposal |
| `atlas_suite/` | BLOOM Design System (5 interactive views) |
| `context_engine/` | FastAPI + React prototype for state externalization |
