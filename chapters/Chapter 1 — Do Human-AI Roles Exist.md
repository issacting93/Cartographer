# Chapter 1: Do Human-AI Roles Exist?

> **Phase 1 (v1) | N=507 (deduplicated from 625) | Status: Complete**

---

## The Question

When you talk to ChatGPT, Claude, or any AI — what's actually happening between you? Not technically, but *relationally*. Are you a customer? A collaborator? A boss giving orders? A student? And what is the AI to you — a tool, an advisor, a companion, a servant?

Nobody had mapped this systematically. The CASA paradigm (Computers Are Social Actors, Reeves & Nass 1996) tells us that humans unthinkingly apply social heuristics to machines triggered by minimal cues — linguistic fluency, interactivity, task execution. But CASA predates LLMs by decades. Modern conversational AI is orders of magnitude more fluent than the systems Nass studied. The social heuristics should fire *harder*. But does that produce stable, classifiable roles?

## What We Did

Took 625 conversations from three public datasets (reduced to 507 after SHA-256 deduplication) (WildChat, Chatbot Arena, OASST) and classified them using a **12-role taxonomy** grounded in Social Role Theory (Parsons, Bales, Eagly):

**Human Roles (6):**
- Information-Seeker, Provider, Director, Collaborator, Social-Expressor, Relational-Peer

**AI Roles (6):**
- Expert-System, Advisor, Co-Constructor, Learning-Facilitator, Social-Facilitator, Relational-Peer

Each role is positioned along two axes: **Instrumental ↔ Expressive** (task-oriented vs relationship-oriented) and **Authority Level** (high, equal, low).
	
Built a 3D terrain visualization — X-axis for functional↔social orientation, Y-axis for aligned↔divergent structure, Z-axis for emotional intensity.

## What We Found

**Yes, roles exist.** Users unconsciously assign social roles to AI, triggered by linguistic fluency and responsiveness. Not because AI is sentient, but because social heuristics don't check for sentience before firing.

**98.8% of human roles are purely instrumental.** Provider, Director, Information-Seeker. Only 1.2% were expressive (Social-Expressor, Relational-Peer). The entire social-relational quadrant of the map was empty. People approach AI as tools, not partners.

**"Same destination, different journeys."** This was the breakthrough finding. Conversations with identical role labels (e.g., Information-Seeker → Expert-System) showed **2,030x variance** in their emotional trajectories. Two people asking the same type of question had wildly different emotional experiences. Role labels describe where conversations end up, but completely miss *how they get there*.

**The map was mostly empty.** 84.4% of conversations clustered in one quadrant (Functional-Aligned). Co-construction, facilitation, play, creative exploration — all nearly absent. Not because they're impossible, but because they're **foreclosed by design**.

## What Went Wrong — and Why It Mattered

An internal audit revealed six methodological failures that nearly invalidated Phase 1: spatial-role circularity (R²=1.0 from using role-derived features as evidence), coarse PAD granularity (53 unique values), 98 undetected duplicates, 15-22% hand-transcription error rates, a misclassified flagship exemplar, and zero unit tests. The full pattern of instrument-bias failures across the research program is documented in Chapter 5.

These failures forced the methodological upgrades that made v2 possible:

- **Strict feature separation:** 30 evidence features (text-derived, R² < 0.01 with labels) for all empirical claims. 2 viz-only features (role-derived) for rendering only.
- **SHA-256 deduplication:** Canonical corpus of 507 (down from 625).
- **Improved affect proxy:** 503 unique values (up from 53).
- **Automated exemplar selection** by variance extremes.
- **Formal acceptance tests (A/B/C)** gating all quantitative claims.

## The Answer

Yes, human-AI roles exist. They emerge predictably from interaction, are classifiable with reasonable reliability, and have measurable affective consequences. But the roles are almost entirely instrumental, the relational territory is empty, and the same role labels mask enormous experiential diversity.

The finding that mattered wasn't what roles exist — it was what was *missing*.

## Key Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| v1 corpus | `data/v1_canonical/` | N=507 (deduplicated) |
| 12-role taxonomy | `"So...What are we..?".md` §RQ1b | Stable |
| Acceptance tests | `scripts/run_acceptance_tests.py` | 3/3 PASS (with warnings) |
| 3D terrain viz | `atlas_suite/` | Operational |

## Journal Notes

- **Date started:** ~2025
- **Date completed:** Early 2026
- **Key methodological lesson:** Never use label-derived features as evidence for label importance. Separate your evidence channel from your classification channel. Test this separation formally.
- **Biggest surprise:** The 2,030x variance ratio. We expected role labels to explain more. They don't.
- **What carried forward to v2:** The 12-role taxonomy, the evidence feature architecture, the acceptance test framework, and the core finding that 97% of interaction is instrumental.
