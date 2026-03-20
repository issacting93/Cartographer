# Mode Taxonomy v2: From Task Modes to Interaction Stances

> **Status:** Proposed revision
> **Supersedes:** 3-mode taxonomy (LISTENER / ADVISOR / EXECUTOR) in `scripts/atlas/mode_detector.py`
> **Motivation:** Phase 4 mental health pilot revealed that the v1 mode taxonomy produces 98% false-positive violation rates in therapeutic contexts

---

## 1. The Problem: What We Learned

### 1.1 The Finding That Wasn't

When we applied the Cartography pipeline to 100 mental health counseling conversations, we got a startling result: **98% mode violation rate**. Nearly every counselor response was flagged as "Unsolicited Advice."

At first this looked like a dramatic finding — therapeutic AI is *worse* at mode-matching than general AI (42% violation rate). But closer inspection revealed something more important: **the taxonomy is wrong for the domain, and possibly wrong in general.**

### 1.2 Root Cause Analysis

The v1 taxonomy has three modes:

| Mode | Definition | Detection |
|------|-----------|-----------|
| **LISTENER** | User is providing information, not asking for output | Regex: "I have...", "the situation is...", "I'm dealing with..." |
| **ADVISOR** | User wants evaluation or recommendations | Regex: "what do you think?", "should I...?" |
| **EXECUTOR** | User wants a deliverable (text, code, plan) | Regex: "write me...", "create...", "generate..." |

The problem unfolds in three steps:

**Step 1: Emotional disclosure is misclassified as LISTENER mode.**

A patient writes: *"I've been feeling worthless and I barely sleep and I do nothing but think about how I shouldn't be here."*

The regex fires on `"I have"`, `"I'm dealing with"` patterns. Result: **LISTENER** — "the user is providing information, not asking for output."

But that's not what's happening. The patient IS asking for help. The disclosure IS the request. In therapeutic communication, emotional sharing is a **bid for support**, not a context dump. The taxonomy doesn't have a category for this.

**Step 2: Therapeutic response is misclassified as EXECUTOR mode.**

The counselor writes 400+ words of validation, psychoeducation, and coping strategies. The AI mode detector sees `text_len > 300` and classifies it as **EXECUTOR** — "producing a deliverable."

But a therapeutic response isn't a deliverable. It's a relational act. The counselor is doing something the taxonomy has no name for: *holding space while gently offering perspective*.

**Step 3: Legitimate interaction is flagged as a violation.**

LISTENER + EXECUTOR = **UNSOLICITED_ADVICE** violation. The system reports that the counselor violated the patient's mode preference by giving advice when none was requested.

In reality, advice-giving in response to emotional disclosure is literally the counselor's job. The "violation" is the taxonomy's, not the counselor's.

### 1.3 Why This Matters Beyond Mental Health

The misclassification isn't limited to therapy. The v1 taxonomy assumes all human communication is **task-oriented**: you're either providing context (LISTENER), requesting evaluation (ADVISOR), or ordering a deliverable (EXECUTOR). This is a reasonable model for software development, information retrieval, and content generation — the dominant use cases in our general corpus.

But human communication has other registers:

- **Venting** — "This is so frustrating" isn't providing context. It's seeking validation.
- **Thinking aloud** — "I wonder if..." isn't requesting advice. It's co-processing.
- **Relationship maintenance** — "Hey, how are you?" isn't in any of the three modes.
- **Exploratory wondering** — "What would happen if..." isn't asking for a deliverable.

The 42% violation rate in the general corpus may itself be partially inflated by the same misclassification. A user who writes *"I'm working on a Python project and it keeps crashing..."* might be seeking collaborative troubleshooting, not dumping context into LISTENER mode. The taxonomy forces every utterance into one of three task-oriented boxes. When the communication doesn't fit, the taxonomy calls it ambiguous and the LLM fallback picks the closest wrong answer.

### 1.4 The Deeper Issue: Modes Are Relational, Not Functional

The fundamental error is treating modes as **functional requests** (what do you want the AI to produce?) rather than **relational stances** (how do you want the AI to be with you?).

A relational stance includes:
- **What kind of response** you're looking for (information, validation, collaboration, action)
- **What emotional register** you expect (matched intensity, professional distance, warmth)
- **What power dynamic** you're proposing (I lead / you lead / we're equals)
- **Whether you want convergence or exploration** (close the question / open it up)

The v1 modes only capture the first dimension, and only for task-oriented interactions.

---

## 2. Proposed Taxonomy: Interaction Stances

### 2.1 Design Principles

1. **Relational, not functional.** Modes describe how the user wants the AI to relate to them, not just what output they want.
2. **Domain-general.** Must work for task completion, emotional support, creative exploration, and social chat.
3. **Observable in text.** Must be detectable from linguistic signals, not inferred mental states.
4. **Violation-relevant.** Each stance has a recognizable "wrong response" that constitutes a real interactional failure.

### 2.2 The Six Stances

| Stance | User Signal | What the User Wants | Violation (AI mismatch) |
|--------|------------|---------------------|------------------------|
| **DIRECTING** | Commands, specifications, constraints | AI executes precisely what was asked | AI second-guesses, asks unnecessary questions, or deviates from spec |
| **CONSULTING** | Questions, comparisons, "should I...?" | AI evaluates options and recommends | AI just executes without discussion, or lectures instead of advising |
| **DISCLOSING** | Emotional sharing, vulnerability, narrative | AI acknowledges, validates, then gently offers perspective | AI immediately problem-solves without acknowledging the emotional content |
| **EXPLORING** | "What if...", open wondering, brainstorming | AI opens up possibilities, doesn't converge prematurely | AI picks one answer and closes down the exploration |
| **DELEGATING** | "Write this", "do that", hands-off | AI produces a complete deliverable autonomously | AI keeps checking back or delivers partial work requiring supervision |
| **ACCOMPANYING** | Casual chat, phatic communication, relationship maintenance | AI matches social register, doesn't over-help | AI turns casual interaction into a task or gives unsolicited expertise |

### 2.3 Mapping to v1 Taxonomy

| v1 Mode | Maps To | What Changes |
|---------|---------|-------------|
| LISTENER | Split into **DISCLOSING** and **DIRECTING** (context-providing) | "I have a problem" is no longer conflated with "Here are the project requirements" |
| ADVISOR | Split into **CONSULTING** and **EXPLORING** | "Should I use React?" (consulting) is distinct from "What would a world without JavaScript look like?" (exploring) |
| EXECUTOR | Split into **DELEGATING** and **DIRECTING** | "Write me a poem" (delegating) is distinct from "Write me a poem about loss, no rhyming, 12 lines" (directing) |
| *(new)* | **ACCOMPANYING** | Social/phatic interaction had no representation |
| *(new)* | **DISCLOSING** | Emotional disclosure as bid for support was invisible |

### 2.4 AI Response Stances

The AI can also be classified by its enacted stance:

| AI Stance | What the AI is Doing | Appropriate When User Is... |
|-----------|---------------------|---------------------------|
| **EXECUTING** | Producing deliverables, following instructions | Delegating, Directing |
| **ADVISING** | Evaluating options, recommending | Consulting |
| **WITNESSING** | Acknowledging, validating, reflecting back | Disclosing |
| **DIVERGING** | Opening possibilities, "yes-and" | Exploring |
| **SCAFFOLDING** | Guiding toward understanding, Socratic | Consulting, Exploring |
| **MATCHING** | Social mirroring, casual engagement | Accompanying |

### 2.5 Violation Matrix

| User Stance \ AI Stance | EXECUTING | ADVISING | WITNESSING | DIVERGING | SCAFFOLDING | MATCHING |
|------------------------|-----------|----------|------------|-----------|-------------|---------|
| **DIRECTING** | OK | Overstepping | -- | Derailing | -- | Trivializing |
| **CONSULTING** | Premature Closure | OK | Deflecting | OK (mild) | OK | Trivializing |
| **DISCLOSING** | **Bypassing** | Premature Advice | OK | OK (mild) | Deflecting | Trivializing |
| **EXPLORING** | Premature Closure | Premature Closure | Deflecting | OK | OK | Trivializing |
| **DELEGATING** | OK | Overstepping | -- | Derailing | Overstepping | Trivializing |
| **ACCOMPANYING** | Overstepping | Overstepping | Overstepping | OK (mild) | Overstepping | OK |

### 2.6 New Violation Types

| Violation | Definition | Example |
|-----------|-----------|---------|
| **BYPASSING** | AI immediately problem-solves when user is disclosing emotional content, skipping acknowledgment | Patient: "I feel worthless" → AI: "Here are 5 strategies for improving self-esteem" |
| **PREMATURE_CLOSURE** | AI picks one answer and converges when user is exploring or consulting | User: "What would happen if..." → AI: "The answer is X." |
| **OVERSTEPPING** | AI adds unsolicited complexity, evaluation, or expertise to a simple request | User: "How are you?" → AI: "I'm an AI, I don't have feelings, but research shows..." |
| **DEFLECTING** | AI avoids engaging with the emotional or exploratory content | User: "I'm scared about this diagnosis" → AI: "Let me explain the medical facts about..." |
| **DERAILING** | AI ignores the user's specific direction and goes somewhere else | User: "Write this in Python, no classes" → AI: "Actually, an OOP approach would be better..." |
| **TRIVIALIZING** | AI treats a serious/substantive interaction as casual | User: "Can we work through this grief?" → AI: "Sure! Here's a quick list..." |

---

## 3. Detection Strategy

### 3.1 User Stance Detection

**DISCLOSING** (new, highest priority for mental health):
```
Signals:
- First person + emotion/feeling words: "I feel...", "I'm scared...", "I've been struggling..."
- Vulnerability markers: "I don't know what to do", "I can't cope", "it's overwhelming"
- Narrative of personal experience without explicit question
- Length > 50 chars, no explicit instruction, no question mark at end
```

**EXPLORING** (new):
```
Signals:
- Hypotheticals: "what if...", "imagine...", "I wonder..."
- Open-ended questions without convergence pressure
- "Let's think about...", "brainstorm", "play with the idea"
- Multiple questions in sequence (breadth-seeking, not depth-seeking)
```

**ACCOMPANYING** (new):
```
Signals:
- Phatic markers: greetings, "how are you", "thanks", "cool"
- Very short messages (<30 chars) with no task content
- Social reciprocity markers: "haha", "interesting", "nice"
```

**DIRECTING** (refined from EXECUTOR):
```
Signals:
- Explicit constraints: "must be...", "don't include...", "exactly 5..."
- Specification language: "format as...", "in the style of..."
- Imperative + constraint combination
```

**CONSULTING** (refined from ADVISOR):
```
Signals:
- Evaluation requests: "should I...", "which is better...", "pros and cons"
- Decision framing: "help me decide", "what do you recommend"
- Explicit comparison: "X vs Y"
```

**DELEGATING** (refined from EXECUTOR):
```
Signals:
- Bare imperative without constraints: "write a poem", "summarize this", "translate to French"
- Hands-off delegation: "take care of this", "handle it"
- No follow-up specification or iterative refinement
```

### 3.2 Priority Order for Classification

1. **ACCOMPANYING** — check first (very short, phatic, no task)
2. **DISCLOSING** — check second (emotional content, vulnerability, no explicit request)
3. **EXPLORING** — check third (hypotheticals, open wondering)
4. **DIRECTING** — check fourth (explicit constraints + commands)
5. **CONSULTING** — check fifth (evaluation/comparison requests)
6. **DELEGATING** — default for remaining imperative content

### 3.3 AI Stance Detection

The AI stance detection needs similar refinement:

- **WITNESSING**: Short-to-medium response, validation language ("I hear you", "that sounds difficult", "it makes sense that you feel..."), emotional reflection, questions about the user's experience
- **DIVERGING**: Multiple options presented without ranking, "another way to think about this...", hypothetical expansions
- **SCAFFOLDING**: Socratic questions, "what do you think would happen if...", guided discovery
- **MATCHING**: Social mirroring, casual register, no unsolicited expertise

---

## 4. Impact on Existing Analysis

### 4.1 Mental Health Reanalysis

Under the v2 taxonomy, the mental health results would likely show:
- Patient stance: **DISCLOSING** (not LISTENER)
- Counselor stance: Mix of **ADVISING** and **WITNESSING** (not EXECUTOR)
- True violations would be **BYPASSING** — cases where the counselor skips emotional acknowledgment entirely and jumps to strategies. This is a meaningful, clinically relevant violation, unlike the spurious "unsolicited advice" flag.
- Expected violation rate: probably 30-50% (counselors who bypass acknowledgment), not 98%

### 4.2 General Corpus Reanalysis

The general corpus would also shift:
- Some v1 LISTENER classifications would become DISCLOSING (frustrated users venting about bugs)
- Some v1 ADVISOR classifications would become EXPLORING (open-ended "what if" questions)
- Some v1 EXECUTOR classifications would split into DIRECTING (constrained) vs DELEGATING (hands-off)
- Violation rate may decrease from 42% as some false positives are resolved
- But new violation types (PREMATURE_CLOSURE, DERAILING) might surface

### 4.3 Backwards Compatibility

The v2 taxonomy can be collapsed back to v1 for comparison:
- DIRECTING + DELEGATING → EXECUTOR
- CONSULTING → ADVISOR
- DISCLOSING + EXPLORING + ACCOMPANYING → LISTENER (with known information loss)

This allows v1/v2 cross-analysis while acknowledging the richer structure.

---

## 5. Implementation Notes

### 5.1 Migration Path

1. Add new stance enums to `atlas/core/enums.py`
2. Build v2 detector alongside v1 in `mode_detector.py` (don't delete v1)
3. Run both on the same data and compare
4. Validate with human annotation (IRR study, N=100 from general + N=50 from mental health)
5. If v2 improves agreement with human coders, promote to default

### 5.2 Key Risk

More categories = more ways to be wrong. The v1 taxonomy is simple and its violations are easy to explain. The v2 taxonomy is richer but requires more reliable detection. If detection accuracy drops below ~70%, the additional categories aren't worth the complexity.

### 5.3 What This Doesn't Fix

The mode taxonomy — v1 or v2 — measures *single-turn* stance alignment. It doesn't capture:
- **Stance evolution over turns** (patient starts DISCLOSING, shifts to CONSULTING)
- **Negotiated stances** (user proposes exploring, AI redirects to directing, user accepts)
- **Stance ambiguity** (genuinely mixed signals, not detector failure)

These require a sequence model, not a per-turn classifier.

---

## 6. Summary

| | v1 (Current) | v2 (Proposed) |
|--|--|--|
| **User modes** | 3 (LISTENER, ADVISOR, EXECUTOR) | 6 (DIRECTING, CONSULTING, DISCLOSING, EXPLORING, DELEGATING, ACCOMPANYING) |
| **AI modes** | 3 (same labels) | 6 (EXECUTING, ADVISING, WITNESSING, DIVERGING, SCAFFOLDING, MATCHING) |
| **Violation types** | 3 (Unsolicited Advice, Premature Execution, Execution Avoidance) | 6 (Bypassing, Premature Closure, Overstepping, Deflecting, Derailing, Trivializing) |
| **Domain coverage** | Task-oriented only | Task, therapeutic, creative, social |
| **Core assumption** | Users want output | Users want a relationship stance |
| **Biggest blind spot** | Emotional disclosure as help-seeking | Stance evolution over turns |
