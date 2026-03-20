# The Structural Trap of Implicit State: A Theory of Agency Collapse in Human–AI Grounding

> **Foundational Theory Document**  
> *How Implicit State Pathology in conversational interfaces leads to inevitable grounding failure and Agency Collapse*

---

## Executive Summary

The rapid integration of large language models into daily productivity has exposed a profound structural rift: while contemporary systems are more linguistically capable than ever, they remain architecturally incapable of maintaining the shared understanding (grounding) that prevents communication breakdown. 

This document establishes that the current failure mode of human–AI dialogue is not merely a deficit in model performance but a consequence of **Implicit State Pathology**—a structural flaw in interface design that inevitably leads to **Agency Collapse**. By examining conversational repair, information-theoretic degradation, and topological evidence of interactional spirals, we provide a framework for understanding and mitigating the breakdown of intersubjectivity in human-AI interaction.

**Key Claims:**
1. LLMs structurally invert human preference for self-repair, forcing users into constant other-repair
2. Context windows create information-theoretic decay (signal degradation, noise accumulation)
3. Agency Collapse is a measurable topological phenomenon (inward spirals vs. outward progress)
4. Task-Constraint Architecture (TCA) with externalized state can prevent collapse

---

## Table of Contents

1. [Evolution of the Social Actor Paradigm](#1-evolution-of-the-social-actor-paradigm)
2. [Fragility of Persona Projection](#2-fragility-of-persona-projection)
3. [Conversational Repair Mechanics](#3-conversational-repair-mechanics)
4. [Information-Theoretic Failure of Grounding](#4-information-theoretic-failure-of-grounding)
5. [Agency Collapse: Definition and Signatures](#5-agency-collapse-definition-and-signatures)
6. [Topological Proof: The Spiral Discovery](#6-topological-proof-the-spiral-discovery)
7. [Prescriptive Framework: Externalizing State](#7-prescriptive-framework-externalizing-state)
8. [Broader Implications](#8-broader-implications)
9. [Summary Tables](#9-summary-tables)

---

## 1. Evolution of the Social Actor Paradigm

### CASA: Computers Are Social Actors

The foundation of modern HCI rests on the **"Computers Are Social Actors" (CASA)** paradigm (Reeves & Nass, 1996). Core insight: humans unthinkingly apply social heuristics to computers triggered by minimal cues (natural language, interactivity, task execution).

### Three Eras of CASA

| Paradigm | Era | Triggering Cues | Social Response Status |
|----------|-----|-----------------|----------------------|
| **Early CASA** | 1990s | Natural language output, simple interactivity | Mindless application of human social rules |
| **Habituated CASA** | 2010s | Desktop GUIs, Cloud services | Transition to machine-specific scripts; decreased anthropomorphism |
| **Reactivated CASA** | 2020s | Generative AI, simulated empathy, persona projection | Intensified social response; fragile relational projections |

**Key Finding:** A 2023 replication study showed original CASA effects have **diminished** for desktop computers (30 years of habituation), but **LLMs have reactivated and intensified** CASA by simulating behaviors associated with human intimacy and emotional labor.

---

## 2. Fragility of Persona Projection

### Unwarranted Trust

LLMs trigger "unwarranted trust" through linguistic mirroring. This trust is bifurcated:
- **Human-trust constructs:** Competence, benevolence, integrity
- **Technology-trust constructs:** Functionality, helpfulness, reliability

Research shows social perception is driven by **"humanness" of voice and style** rather than physical embodiment.

### The Chatbot Companion Paradox

Tension between:
- **Knowledge:** "It is a machine"
- **Feeling:** "It seems human"

The **uncanny valley** doesn't suppress moral concern—it may heighten protective impulses when the agent's "struggle" feels real, even knowing it's simulated.

**Implication:** The social frame is a delicate equilibrium, easily disrupted when model output contradicts the projected persona.

---

## 3. Conversational Repair Mechanics

### Human Preference Structure (Schegloff, Jefferson, Sacks, 1977)

**Repair** = practices to address problems in speaking, hearing, understanding. It is the **"self-righting mechanism"** of social interaction, essential for **intersubjectivity** (mutual belief in understanding).

**Strong preference for self-repair:**
1. **Same-turn self-repair** — Speaker catches own mistake mid-turn
2. **Transition-space repair** — Speaker fixes it between turns
3. **Other-initiated self-repair (OISR)** — Recipient signals problem, speaker fixes it
4. **Other-initiated other-repair** — Recipient corrects (rare, face-threatening)

**Efficiency:** Self-repairs mostly succeed within same turn or transition space.

### The Structural Inversion in AI Interaction

**Critical Problem:** LLMs structurally invert this preference structure.

- **LLMs lack introspective capability** to identify trouble sources as they generate
- **Almost never perform same-turn self-repair**
- **Burden falls entirely on user** → forced into constant other-initiated other-repair

### Empirical Evidence

| Interaction Type | Repair Rate | Reformulation Rate |
|-----------------|-------------|-------------------|
| **Human-to-Human** (MultiWOZ) | 3.0% | 4.0% |
| **Human-to-AI** (Averaged Logs) | 18.0% | 5.0% |

**User works ~6x harder** to maintain intersubjectivity than in human conversation.

**Violates "least collaborative effort" principle** → Effort skewed so heavily toward user that "collaborative" nature dissolves → frustration → withdrawal.

---

## 4. Information-Theoretic Failure of Grounding

### Grounding Defined

**Grounding** = process by which parties coordinate content and process, building **"common ground"** (mutual knowledge, beliefs, assumptions).

Successful grounding requires both parties believe their partners understood them **to a criterion sufficient for the current task**.

### Initiative Deficit in LLMs

**Key Asymmetry:** LLMs are trained to *follow instructions*, not to *clarify*.

**Behavioral Patterns:**
- 3x less likely to initiate clarification than humans
- 16x less likely to provide follow-up requests
- **Over-respond** in ~45% of turns (verbose answers to every possible interpretation)
- **Over-acknowledge** with generic "I understand" without verifying common ground

### Implicit State Pathology: The Architectural Root

**Traditional Dialogue Systems:** Maintained explicit **Dialogue State Tracking (DST)** — internal representation of goals, constraints, current understanding.

**LLMs:** **Stateless**. No persistent state representation. Must **re-infer entire context** from context window at every turn.

#### Information-Theoretic Problem

As conversation progresses:

1. **Context Density** ↑ — Each turn adds data volume
2. **Signal Degradation** ↓ — Original intent becomes smaller fraction of total context
3. **Noise Accumulation** ↑ — Repairs, apologies, clarifications add noise
4. **Reconstruction Loss** ↑ — Transformers have finite attention, prioritize recent tokens

**Result:** Original constraints are frequently lost or contradicted.

### The Repair Loop Trap

```
User states constraint
    ↓
Model violates constraint
    ↓
User adds repair text (increases context noise)
    ↓
Signal-to-noise ratio degrades
    ↓
Model less likely to reconstruct state correctly
    ↓
Model makes another mistake
    ↓
[LOOP]
```

**Better prompting doesn't fix this** — longer prompts accelerate the problem by consuming more context window.

### Comparison Table

| Feature | Human-Human Grounding | Human-AI Grounding (Implicit State) |
|---------|---------------------|----------------------------------|
| **State Retention** | Persistent, cumulative mental models | Re-inferred each turn from context window |
| **Clarification** | Proactive and frequent | Rare; prioritizes instruction-following |
| **Signal/Noise** | Balanced through pruning and summary | Degrading; noise grows with repair attempts |
| **Context Handling** | Selective attention to relevant history | Lossy attention over scrolling window |

---

## 5. Agency Collapse: Definition and Signatures

### Definition

**Agency Collapse** = Pathological degradation state where the user's capacity to direct the interaction effectively disappears because the system can no longer maintain stable grounding of user intent.

**Not** a binary failure (system crash), but a **progressive** failure of interactional health.

### Behavioral Signatures

1. **Repeated Failed Repairs**
   - User issues correction → AI fails to incorporate it next turn
   - Probability of next turn being another failed repair increases dramatically
   
2. **Grounding Failure Cascade**
   - Baseline P(grounding failure) = 0.12
   - After one misunderstanding: P(failure) = 0.30
   - **Cascading degradation**

3. **Tone Degradation**
   - Polite, conversational language → terse, command-like structures
   - User realizes social persona is failing

4. **Specificity Collapse**
   - AI provides generic, "safe" responses
   - User instructions become redundant ("shouting through noise")

5. **Session Restart Rate**
   - 10.7% of sessions restarted (source: WildChat logs)
   - Indicates total breakdown of shared agency

---

## 6. Topological Proof: The Spiral Discovery

### Interactional Cartography Method

Map conversations into **polar layout:**
- **Angle (θ)** = time
- **Radius (r)** = functional progress / task space exploration

### Patterns Discovered

**Healthy Interactions:**
- **Outward spiral** — as time passes, conversation moves into new functional territory
- Common ground maintained and used as foundation for progress

**Agency Collapse Interactions:**
- **Tight, inward-spiraling knots** — recursive cycle
- Each turn consumes more time but yields less functional progress
- **"The knot"** = visible representation of Repair Loop

### Significance

**Topological proof** that agency collapse is not subjective frustration but a **measurable, structural phenomenon** in interaction space.

**Tool:** The "Atlas Suite" serves as a "microscope" revealing pathogenic effects of implicit state management.

---

## 7. Prescriptive Framework: Externalizing State

### Core Principle

**Root cause identified:** Implicit State Pathology  
**Solution path:** Transition to **Externalized State**

**Current "chat bubble" interface** is fundamentally mismatched with requirements of stable, complex grounding.

### Task-Constraint Architecture (TCA)

**Design framework** that externalizes hidden state, making model's "understanding" visible and editable.

**Analogy:** Creates equivalent of **"visual co-presence"** in computational common ground (Clark & Brennan, 1991).

Visual co-presence reduces grounding costs because it allows:
- Deictic reference (pointing)
- Constant feedback on partner's focus

### TCA Component Comparison

| Component | Implicit Mode (Current) | Externalized Mode (Proposed) |
|-----------|------------------------|----------------------------|
| **Role Declaration** | Inferred from dialogue flow | Persistent, declared "mandate" |
| **Constraint Management** | Scattered in history | Persistent "Constraint Registry" (pinned) |
| **Task Scope** | Implicit and ambiguous | Explicit "Task Inventory" with status |
| **Common Ground** | Reconstructed turn-by-turn | Persisted, visible, user-editable |

### Actionable Resources for Repair

**Key Benefit:** Provides user with actionable repair mechanisms.

**Example Scenario:**

**Traditional Chat:**
```
AI: [Generates Python code]
User: "I told you not to use Python." 
[Adds turn to context → increases noise]
```

**TCA Interface:**
```
User sees: Constraint Registry
- [Active] "No Python" ❌ [Missing!]
User action: Adds "No Python" to registry directly
[Repairs without adding conversational noise]
```

**Result:** Maintains signal-to-noise ratio, prevents spiral into collapse.

### Alignment with User Preferences

Users prefer strategies that **specify the trouble source** rather than generic "I don't understand" responses.

Exposing chatbot's understanding model allows:
- **Effective self-repair** — User can correct before AI generates large incorrect response
- **Direct state editing** — Reduces conversational overhead

---

## 8. Broader Implications

### AI Alignment as UI Architecture Problem

**Shift:** From purely "model behavior" problem to **"UI architecture" problem.

Most alignment research focuses on internal rewards/goals matching human values. **Necessary but insufficient** if interface structurally prone to grounding failure.

### Misalignment as Technical Debt

Current interfaces lack state representations needed for grounding that makes human communication self-correcting.

**Interactional Technical Debt:** Each turn without explicit grounding increases risk of **referential misalignment** (system and user talking about different things while believing they agree).

### High-Stakes Domains

**Concern:** Scientific research, engineering, political discourse

If scientific agent automates experiment design based on:
- Misunderstood constraint buried in context window
- Resulting data may be invalid or dangerous

**Agency collapse = epistemic failure** undermining AI reliability as collaborative partner.

### The Problem of "We" and Shared Agency

Many social activities involve **shared agency** — acting unit becomes a "we," individuals "inhabit actions of the other."

**For "we" to form between human and AI:**
- Requires continuous, high-fidelity coordination of goals and practices
- High session restart rate (10.7%) indicates **failure to form shared agency**
- Users view LLMs as temperamental tools requiring frequent resets

---

## 9. Summary Tables

### Interactional Asymmetries

| Metric | Human-Human Interaction | Human-AI Interaction (LLMs) | Significance |
|--------|------------------------|----------------------------|--------------|
| **Repair Preference** | Strong preference for self-repair | Forced reliance on other-repair | Increases user burden and face-threat |
| **Clarification Frequency** | High (ongoing proactive checks) | Low (3x less likely) | Leads to referential misalignment |
| **Follow-up Requests** | Frequent (bidirectional initiative) | Very Low (16x less likely) | Stunts development of common ground |
| **Response Volume** | Efficient (least collaborative effort) | High (45% over-responding) | Increases context noise and signal loss |
| **Failure Resolution** | Collaborative repair and continuity | Session restarts (10.7%) | Indicates total breakdown of shared agency |

### CASA Evolution

| Paradigm | Era | Triggering Cues | Social Response Status |
|----------|-----|-----------------|----------------------|
| **Early CASA** | 1990s | NL output, interactivity | Mindless social rules |
| **Habituated CASA** | 2010s | Desktop GUIs, cloud | Machine-specific scripts, decreased anthropomorphism |
| **Reactivated CASA** | 2020s | Generative AI, simulated empathy | Intensified response, fragile projections |

---

## Conclusion

The analysis of human–AI interaction through CASA, Conversation Analysis, and Grounding Theory reveals a profound **structural trap**:

**The reliance on implicit state and context window as memory proxy** has created an environment where:
- Grounding is lossy
- Repair is inverted  
- Collapse is inevitable for complex tasks

**The "Repair Loop"** and its topological proof (inward-spiraling cartographies) suggest we have reached the **limits of the simple "chat bubble" interface**.

### The Path Forward

**Task-Constraint Architecture (TCA)** that prioritizes externalization of state:
- Make common ground visible
- Provide tools to manage constraints explicitly
- Transform interaction from fragile projection → robust collaboration

**This requires:**
- Reconsidering LLM training — move from pure instruction-following toward **"proactive grounding"** model
- Valuing clarification and follow-up as much as task execution
- Building interfaces that support natural "self-righting" mechanisms of dialogue

**Only by addressing Implicit State Pathology can we prevent Agency Collapse** and ensure AI remains reliable, understandable, and under human direction.

---

## References

### Foundational Works

- **Reeves, B., & Nass, C.** (1996). *The Media Equation: How People Treat Computers, Television, and New Media Like Real People and Places*. Cambridge University Press.

- **Schegloff, E. A., Jefferson, G., & Sacks, H.** (1977). The Preference for Self-Correction in the Organization of Repair in Conversation. *Language*, 53(2), 361-382.

- **Clark, H. H., & Brennan, S. E.** (1991). Grounding in Communication. In L. B. Resnick, J. M. Levine, & S. D. Teasley (Eds.), *Perspectives on Socially Shared Cognition* (pp. 127-149). American Psychological Association.

### Related Research

See [`related_work.md`](related_work.md) for comprehensive literature review linking to:
- Mixed-initiative interaction
- Repair as measurable phenomenon
- Prompting burden and limits
- State externalization and inspectable interfaces

---

*This document serves as the theoretical foundation for the Cartography project's empirical work on measuring and preventing Agency Collapse in human-AI interaction.*
