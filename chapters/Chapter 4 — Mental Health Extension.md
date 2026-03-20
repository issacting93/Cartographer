# Chapter 4: Mental Health — Where the Framework Breaks (and Learns)

> **Phase 4 | N=150 (100 single-turn + 50 multi-turn) | Status: Complete**

---

## The Question

The 97% instrumental monopoly was a striking finding — but it came from general-purpose AI conversations (coding help, information retrieval, content generation). Mental health counseling is fundamentally different: people come to be *heard*, not to get deliverables. Would the instrumental monopoly survive domain transfer? Would constraint dynamics even apply?

## What We Did

Applied the full Cartography pipeline to two mental health counseling datasets:

- **Single-turn counseling** (Amod/mental_health_counseling_conversations, N=100): Real licensed therapist responses to patient questions. One question, one answer. No multi-turn dynamics.
- **Multi-turn caregiver sessions** (MentalChat16K PISCES subset, N=50): Behavioral health coach conversations with caregivers dealing with Alzheimer's, hospice, and end-of-life care. Mean 7.6 turns per session.

### Technical Adaptation

The pipeline was built for OpenAI. We needed Claude. Built an Anthropic-to-OpenAI adapter (`anthropic_adapter.py`) that wraps Anthropic's SDK to match the OpenAI `client.chat.completions.create()` interface. This let us run the entire 7-stage pipeline and SRT classifier with Claude Haiku without changing any pipeline code.

Pipeline ran with `claude-haiku-4-5-20251001` for all LLM classification steps.

## What We Found

### The Instrumental Monopoly Breaks — Partially

| Metric | General (N=2,577) | Single-Turn MH (N=100) | Multi-Turn Caregiver (N=50 Pilot) |
|--------|-------------------|------------------------|----------------------------|
| Dominant human role | Information-Seeker (73.9%*) | **Information-Seeker (50.3%)** / Social-Expressor (45.8%) | Social-Expressor (~58%) |
| Dominant AI role | Expert-System (77.6%*) | **Advisor (65.5%)** | Advisor (~44%) |
| Expressive human roles | 3.0% | 48.1% (Soc-Exp + Rel-Peer) | 69.8% |
| Emotional tone | 56% neutral | 63% supportive, 29% empathetic | 94% empathetic |
| Conversation purpose | 56.3% info-seeking | 28% Emotional Processing, 31% Advisory | 86% emotional processing |

*\*General corpus standalone rates (IS = 1,904/2,576; ES = 1,998/2,576). The IS→ES dyad rate is 70.0% — a related but distinct metric measuring paired co-occurrence.*

*Note: All 100 single-turn conversations were processed through the pipeline and SRT classifier. The role distribution percentages for single-turn are based on a stratified subsample of N=39 that received detailed role coding; the full N=100 was used for affect, emotional tone, and purpose metrics.*

The human side transformed significantly. In mental health, **Social-Expressor (45.8%)** rivals the standard Information-Seeker role. Patients lead with emotional sharing and distress. The relational territory that was empty in the general corpus is populated here.

The AI side shifted dramatically, but not to "Peer" or "Facilitator." **Expert-System usage collapsed from 77.6% (general) to 11.3% (MH single-turn)** — replaced almost entirely by **Advisor (65.5%)**. The AI stops being an encyclopedia and becomes a "fixer," responding to emotional distress with prescriptive guidance rather than sustained accompaniment. Expert-System + Advisor combined accounts for 76.8% of AI responses in MH single-turn (vs. 82.2% in general corpus), confirming the **Relational Mismatch**: even when the domain shifts, the AI's response repertoire remains instrumental.

### The 98% Mode Violation Rate — A Finding That Wasn't

This was the most important result of Phase 4, and it was almost a disaster.

When we ran the mode detector on mental health data, it reported a **98% mode violation rate**. Single-turn counseling: 98%. Multi-turn: 79.4%. Both dramatically worse than the general corpus (42%).

At first this looked like a damning finding — therapeutic AI is *even worse* at mode-matching than general AI. We almost reported it that way.

Then we looked at what the detector was actually doing:

**Step 1:** Patient writes: *"I've been feeling worthless and I barely sleep and I do nothing but think about how I shouldn't be here."*

The regex fires on `"I have"`, `"I'm dealing with"` patterns. Result: **LISTENER** — "the user is providing information, not asking for output."

But that's wrong. The patient IS asking for help. The disclosure IS the request.

**Step 2:** Counselor writes 400+ words of validation, psychoeducation, and coping strategies.

The detector sees `text_len > 300` and classifies: **EXECUTOR** — "producing a deliverable."

But a therapeutic response isn't a deliverable. It's a relational act.

**Step 3:** LISTENER + EXECUTOR = **UNSOLICITED_ADVICE** violation.

The system reports the counselor violated the patient's mode preference. In reality, responding to emotional disclosure with support is literally the counselor's job.

### Root Cause: The Taxonomy Was Wrong

The v1 mode taxonomy (LISTENER / ADVISOR / EXECUTOR) assumes all human communication is task-oriented. You're either providing context, requesting evaluation, or ordering a deliverable. This is reasonable for software development and content generation. It is catastrophically wrong for emotional communication.

The taxonomy has no category for:
- **Emotional disclosure as a bid for support** (not "providing context")
- **Therapeutic response as a relational act** (not "producing a deliverable")
- **Venting** (not context-setting)
- **Thinking aloud** (not requesting advice)
- **Social chat** (not in any of the three modes)

The 98% violation rate was not a finding about therapeutic AI. It was a finding about the taxonomy's blind spots. **The instrument was as instrumentally biased as the interactions it was built to measure.**

### The Structural Limitation of Single-Turn Data

A separate methodological finding: single-turn counseling data is structurally incapable of showing mode dynamics. If the patient gets one message and the counselor gets one response, the counselor *must* respond substantively — there is no option to "just listen" first. Mode violations become structurally inevitable regardless of quality.

Multi-turn data is essential for meaningful mode/constraint analysis. Single-turn data can only assess role distributions and affect.

## What We Learned

### Three findings that survived

1. **The Instrumental Monopoly is domain-dependent.** 97% instrumental is a property of general-purpose AI use, not a universal property of human-AI interaction. Mental health activates the Social-Expressor role that is nearly absent (2.4%) in the general corpus.

2. **The Relational Mismatch is real.** Even when humans bring expressive intent, the AI responds instrumentally. Expert-System + Advisor = 70-82% across all domains. The AI's response repertoire doesn't shift to match the human's.

3. **Affect profile differs.** Patient Pleasure: 0.48 (vs ~0.60-0.65 in general). Lower pleasure reflects the distressed nature of help-seeking. This is not a flaw — it's the appropriate emotional register for the context.

### One finding that died

4. **~~Mode violations are worse in therapy (98%)~~** — This was a taxonomy failure. The violations were artifacts of applying task-oriented mode categories to emotional communication. The actual clinical violation (counselor skipping emotional acknowledgment and jumping straight to strategies — "Bypassing") requires a different taxonomy to detect.

### One caveat to flag

5. **MentalChat16K (PISCES subset) is synthetic data** generated by GPT-3.5. The cross-model comparability between GPT-3.5-generated counseling and Claude-classified counseling is not validated. The single-turn Amod data uses real therapist responses, but the multi-turn data should be treated as a pilot, not a definitive analysis.

## The Taxonomy v2 Proposal

The failure of the mode taxonomy in mental health led to a complete redesign proposal. Instead of 3 task-oriented modes, we proposed **6 interaction stances**:

| v1 Mode | v2 Stance(s) | What Changes |
|---------|-------------|-------------|
| LISTENER | DISCLOSING + DIRECTING | "I feel worthless" (disclosing) is no longer conflated with "Here are the requirements" (directing) |
| ADVISOR | CONSULTING + EXPLORING | "Should I use React?" (consulting) is distinct from "What would a world without JavaScript look like?" (exploring) |
| EXECUTOR | DELEGATING + DIRECTING | "Write a poem" (delegating) is distinct from "Write a poem about loss, no rhyming, 12 lines" (directing) |
| *(new)* | ACCOMPANYING | Social/phatic interaction (greetings, small talk) had no representation |

With corresponding AI stances: EXECUTING, ADVISING, WITNESSING, DIVERGING, SCAFFOLDING, MATCHING.

And new violation types that capture real therapeutic failures: **BYPASSING** (skipping emotional acknowledgment), **PREMATURE_CLOSURE** (converging when exploring), **DEFLECTING** (avoiding emotional content), **TRIVIALIZING** (treating serious content casually).

The full proposal is in `theory/mode_taxonomy_v2.md`. It has not yet been implemented.

## What This Means for the Research

The mode violation numbers in the paper (Section 7) are weaker than originally reported. But the core findings — roles, constraints, variance, collapse — all survive because they don't depend on the mode taxonomy. The mode analysis was one of seven pipeline stages. The other six are unaffected.

Ironically, the taxonomy failure is itself evidence for the thesis. The instruments we build to measure human-AI interaction are as instrumentally biased as the interactions themselves. If even our *researchers' tools* can't see emotional communication, no wonder the AI can't either.

The honest story — "we found a domain where our framework breaks, diagnosed why, and proposed a fix" — is better research than the 98% headline would have been.

## Key Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Single-turn data | `data/mental_health/` | N=100, pipeline + SRT complete |
| Multi-turn data | `data/mental_health_multiturn/` | N=50, pipeline + SRT complete |
| Anthropic adapter | `scripts/atlas/anthropic_adapter.py` | Async + sync |
| Download script | `scripts/download_mental_health.py` | Amod dataset |
| Mode taxonomy v2 | `theory/mode_taxonomy_v2.md` | Proposed, not implemented |
| Comparative analysis | `scripts/analysis/analyze_mental_health.py` | Complete |

## Journal Notes

- **Date:** February 2026
- **Key methodological lesson:** When your instrument gives you a dramatic finding (98% violation rate), check the instrument before celebrating the finding. The dramatic number was a diagnostic of the tool, not the domain.
- **Biggest surprise:** How cleanly the role distributions inverted. 73.9% Information-Seeker in general → 48.7% Social-Expressor in mental health. The taxonomy works — it just measures different things in different contexts.
- **Most important learning:** Emotional disclosure has no mode in the v1 taxonomy. "I feel worthless" and "The project requirements are..." both get classified as LISTENER. This is a category error that any domain extension will hit. The v2 taxonomy must be implemented before scaling further.
- **What carries forward:** The domain-dependent instrumental monopoly finding. The Relational Mismatch concept. The taxonomy v2 proposal. And the meta-lesson: test your instruments on the hardest case first.
