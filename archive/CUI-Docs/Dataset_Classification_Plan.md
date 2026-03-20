# Dataset Classification Plan: N=562 Analysis
## Aligning Empirical Evidence with "Tasks, Not Turns"

---

## 1. Overview

**Current State:** 562 validated human-LLM interactions coded for:
- Role Function (R): 5-point Seeker→Director scale
- Constraint Presence (C): Binary
- Trajectory (Δ): Change over time

**Goal:** Expand classification to directly operationalize the paper's theoretical constructs, enabling stronger empirical claims about Agency Collapse and the structural bias of chat interfaces.

---

## 2. Core Theoretical Constructs to Operationalize

| Construct | Paper Definition | Classification Requirement |
|-----------|------------------|---------------------------|
| **Agency Collapse** | Specificity of constraints decreases while system control increases | Multi-turn trajectory coding |
| **Constraint Half-Life** | Turns until a stated constraint is violated | Constraint tracking per turn |
| **Restatement Friction** | Cost of re-establishing lost constraints | Restatement event coding |
| **Task-Binding** | Whether interaction has explicit task structure | Task Object presence/absence |
| **Epistemic Opacity** | User cannot know system's task state | State query attempts |

---

## 3. Proposed Multi-Layer Classification Scheme

### Layer 1: Interaction-Level Metadata

For each of 562 interactions, code:

```yaml
interaction:
  id: string
  source: WildChat | ChatbotArena | OASST
  total_turns: int
  duration_minutes: float (if available)
  domain: career | travel | code | education | creative | general | other
  task_complexity: single-goal | multi-goal | exploratory
```

**Domain Categories** (align with paper's generalizability table):
| Domain | Constraint Type | Example |
|--------|-----------------|---------|
| Career | Preferences, hard constraints | "Remote only", "Max 45 hrs" |
| Travel | Budget, dates, logistics | "$2000 budget", "Must return by Friday" |
| Code | Specs, style, architecture | "Use TypeScript", "No external deps" |
| Education | Learning goals, pacing | "Explain simply", "Test me after" |
| Creative | Style, tone, audience | "Professional tone", "500 words max" |
| General | Mixed/unclear | Q&A, chat |

### Layer 2: Turn-Level Constraint Tracking

For each turn, code:

```yaml
turn:
  turn_number: int
  speaker: user | assistant

  # Constraint Events
  constraint_stated: boolean          # New constraint introduced
  constraint_type: goal | hard | soft | preference | null
  constraint_text: string | null      # Verbatim constraint

  # Violation Events
  constraint_violated: boolean        # AI output violates prior constraint
  violated_constraint_id: string | null
  violation_type: direct | drift | implicit | null

  # Repair Events
  repair_attempted: boolean           # User tries to correct
  repair_type: restatement | reference | redirect | abandon | null
  repair_success: boolean | null

  # Agency Markers
  user_specificity: 1-5              # How specific is user input?
  user_stance: directive | collaborative | passive | reactive
  passive_acceptance: boolean         # "ok", "sure", "thanks" without pushback
```

**Violation Types:**
| Type | Definition | Example |
|------|------------|---------|
| **Direct** | Explicit contradiction | "Remote only" → AI suggests hybrid role |
| **Drift** | Gradual scope expansion | Budget creeps from $2k to $3k |
| **Implicit** | Ignores without contradicting | User said "simple" → AI gives complex answer |

**Repair Types:**
| Type | Definition | Example |
|------|------------|---------|
| **Restatement** | User re-types the constraint | "I said no on-call" |
| **Reference** | Points back to prior message | "As I mentioned in my first message..." |
| **Redirect** | Indirect correction | "Let's focus on remote options instead" |
| **Abandon** | Accepts violation | "Ok, tell me more about that one" |

### Layer 3: Trajectory Classification

Computed from turn-level data:

```yaml
trajectory:
  # Agency Collapse Metrics
  initial_specificity: float          # Mean specificity turns 1-3
  final_specificity: float            # Mean specificity final 3 turns
  specificity_delta: float            # Change over time
  collapse_detected: boolean          # Δ < -1.0 threshold

  # Constraint Maintenance
  constraints_stated: int             # Total unique constraints
  constraints_violated: int           # How many were violated
  constraint_half_life: float         # Median turns to first violation
  restatement_count: int              # Total restatements
  restatement_loops: int              # Constraint restated 2+ times

  # Outcome
  task_completed: boolean | unclear
  user_satisfaction_proxy: positive | neutral | negative | unknown
```

### Layer 4: Archetype Assignment

Map each interaction to one of five archetypes:

| Archetype | Criteria | Signature Pattern |
|-----------|----------|-------------------|
| **Provider Trap** | High initial specificity → rapid decline; AI takes control | "Sure, I can help with X. First, tell me about Y, Z, W..." |
| **Hallucination Loop** | Violation → correction → new error → correction... | 3+ repair attempts in sequence |
| **Identity Shift** | Tone degrades from polite to curt | "Please" → "Just" → "No." |
| **Canvas Hack** | User copy-pastes context repeatedly | Same constraint text appears 3+ times verbatim |
| **Passive Default** | No constraints ever stated; acceptance throughout | specificity < 2 throughout |

**Archetype Assignment Rules:**
```python
def assign_archetype(interaction):
    if restatement_loops >= 3 and all_repairs_fail:
        return "Hallucination Loop"
    elif verbatim_repeats >= 3:
        return "Canvas Hack"
    elif initial_specificity >= 4 and collapse_detected:
        return "Provider Trap"
    elif has_tone_degradation():
        return "Identity Shift"
    elif max_specificity < 2:
        return "Passive Default"
    else:
        return "Mixed/Other"
```

---

## 4. New Derived Metrics

### 4.1 Agency Collapse Index (ACI)

A composite score measuring degree of collapse:

```
ACI = (Specificity_Δ × -1) + (Restatement_Count × 0.5) + (Violation_Acceptance_Rate × 2)

Where:
- Specificity_Δ = final_specificity - initial_specificity (negative = collapse)
- Restatement_Count = number of times user restates constraints
- Violation_Acceptance_Rate = violations accepted without repair / total violations
```

**Interpretation:**
| ACI Score | Interpretation |
|-----------|---------------|
| < 0 | Net agency gain (rare) |
| 0-2 | Stable interaction |
| 2-4 | Moderate collapse |
| > 4 | Severe collapse |

### 4.2 Constraint Durability Score

How well constraints survive:

```
Durability = (Constraints_Honored / Constraints_Stated) × (1 / Restatement_Rate)
```

### 4.3 Repair Efficiency

```
Repair_Efficiency = Successful_Repairs / Total_Repair_Attempts
```

---

## 5. Annotation Protocol

### 5.1 Annotator Training

1. **Calibration Set:** 30 interactions annotated by all raters
2. **Discussion:** Resolve disagreements, refine definitions
3. **Reliability Check:** κ ≥ 0.70 required before proceeding

### 5.2 Annotation Workflow

```
Phase 1: Metadata (1 annotator)
├── Domain classification
├── Task complexity
└── Total turns

Phase 2: Turn-Level (2 annotators)
├── Constraint events
├── Violation events
├── Repair events
└── Agency markers

Phase 3: Trajectory (computed)
├── Aggregate metrics
├── Collapse detection
└── Half-life calculation

Phase 4: Archetype (2 annotators + tiebreaker)
├── Pattern matching
├── Majority vote
└── Confidence score
```

### 5.3 Inter-Rater Reliability Targets

| Coding Dimension | Target κ |
|------------------|----------|
| Domain | ≥ 0.80 |
| Constraint Presence | ≥ 0.85 |
| Violation Detection | ≥ 0.75 |
| Repair Type | ≥ 0.70 |
| Archetype | ≥ 0.65 |

---

## 6. Analysis Plan

### 6.1 Descriptive Statistics

| Question | Analysis |
|----------|----------|
| What % of interactions show Agency Collapse? | ACI distribution |
| What is median Constraint Half-Life? | Survival analysis |
| Which archetypes are most common? | Frequency table |
| Does domain affect collapse rate? | Cross-tabulation |

### 6.2 Hypothesis Tests

**H1:** Constraint Half-Life is shorter for chat-only interfaces
- *Method:* Compare half-life across sources (if interface metadata available)

**H2:** Restatement Friction predicts task abandonment
- *Method:* Logistic regression: P(abandon) ~ restatement_count + ...

**H3:** The five archetypes have distinct agency trajectories
- *Method:* ANOVA on ACI scores by archetype

**H4:** Provider Trap is the dominant collapse pattern
- *Method:* Archetype frequency analysis

### 6.3 Visualizations for Paper

1. **Sankey Diagram:** Constraint flow (stated → honored/violated → repaired/abandoned)
2. **Survival Curve:** Constraint half-life across domains
3. **Trajectory Heatmap:** Specificity over turns by archetype
4. **Archetype Pie Chart:** Distribution of collapse patterns

---

## 7. Strengthening Paper Claims

### Current Claim → Enhanced Evidence

| Paper Claim | Current Evidence | Enhanced with New Classification |
|-------------|------------------|----------------------------------|
| "72% cluster in passive consumption" | Role function coding | ACI distribution + Passive Default archetype rate |
| "Constraint Half-Life = 4.7 turns" | Rough estimate | Precise survival analysis with confidence intervals |
| "23% contain restatement loops" | Qualitative observation | Exact count + loop length distribution |
| "Five archetypes of agency loss" | Qualitative categories | Quantified prevalence + signature metrics |
| "Provider Trap is most common (32%)" | Estimate | Archetype classification with κ reliability |

### New Claims Enabled

1. **Agency Collapse Index** provides a standardized, replicable measure
2. **Constraint Durability** varies significantly by domain (travel > code > career?)
3. **Repair Efficiency** predicts user satisfaction proxy
4. **Canvas Hack** users show highest engagement but lowest efficiency

---

## 8. Implementation Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Week 1** | Finalize codebook | Annotation guide with examples |
| **Week 2** | Calibration | 30-interaction training set |
| **Week 3-4** | Annotation | 562 interactions coded |
| **Week 5** | Reliability | κ scores, disagreement resolution |
| **Week 6** | Analysis | Statistics, visualizations |
| **Week 7** | Integration | Updated paper Section 4 |

---

## 9. Codebook Quick Reference

### Constraint Types
- **Goal:** What must be achieved ("Find a senior role")
- **Hard:** Non-negotiable requirement ("Remote only")
- **Soft:** Flexible preference ("Prefer tech sector")
- **Preference:** Nice-to-have ("Good equity would be great")

### User Stance
- **Directive:** Giving clear instructions
- **Collaborative:** Working together
- **Passive:** Accepting without input
- **Reactive:** Only responding to prompts

### Specificity Scale (1-5)
1. Vague/empty ("ok", "sure")
2. General ("help me with jobs")
3. Moderate ("I want a remote engineering job")
4. Specific ("Senior engineer, remote, max 45 hrs, tech sector")
5. Highly specific (Detailed requirements with priorities)

---

## 10. Expected Outcomes

After reclassification, the paper's empirical section will feature:

1. **Precise prevalence rates** for Agency Collapse (with CI)
2. **Domain-specific Constraint Half-Life** values
3. **Validated archetype taxonomy** with inter-rater reliability
4. **Agency Collapse Index** as a reusable metric for future research
5. **Predictive model** linking collapse to task abandonment

This transforms Section 4 from descriptive observation to rigorous empirical analysis, strengthening the foundation for the design response (CII) and evaluation claims.
