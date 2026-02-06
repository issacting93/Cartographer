# Hybrid Classification Pipeline: Regex + LLM

## Overview

A two-stage classification approach that combines:
1. **Stage 1 (Regex):** Extract computable linguistic features with established markers
2. **Stage 2 (LLM):** Synthesize features into archetype classification with reasoning

This provides methodological rigor (grounded features) + interpretive power (LLM context understanding).

---

## Stage 1: Computable Features (Regex/Heuristic)

### 1.1 Repair Markers

**Literature:** Schegloff, Jefferson & Sacks (1977) - Conversation repair

```python
REPAIR_MARKERS = [
    # Explicit correction
    r"no,?\s*(i\s+)?meant",
    r"that's not what i",
    r"let me clarify",
    r"i said",
    r"as i mentioned",
    r"i already told you",
    r"again,",
    r"for the \w+ time",
    
    # Rejection + restatement
    r"no[,.]?\s+(i\s+)?(want|need|said)",
    r"not\s+\w+[,.]?\s+(but|instead)",
    
    # Frustration repair
    r"\?\?+",  # Multiple question marks
    r"did you (even )?(read|understand|see)",
]
```

**Output:** `repair_count: int`, `repair_turns: list[int]`

---

### 1.2 Constraint Markers

**Literature:** Modal logic, deontic expressions (Palmer, 2001)

```python
CONSTRAINT_MARKERS = {
    "hard": [
        r"\b(must|have to|need to|require|only|never|always)\b",
        r"\b(no more than|at least|maximum|minimum|exactly)\b",
        r"\b(cannot|can't|won't|will not)\b",
    ],
    "soft": [
        r"\b(prefer|ideally|if possible|would like|hope)\b",
        r"\b(rather|better if|nice to have)\b",
    ],
    "goal": [
        r"\b(goal|objective|aim|target|trying to|want to|looking for)\b",
    ],
}
```

**Output:** `constraints: list[{type, text, turn}]`, `constraint_count: int`

---

### 1.3 Politeness Trajectory

**Literature:** Brown & Levinson (1987) - Politeness theory

```python
POLITENESS_POSITIVE = [
    r"\bplease\b",
    r"\bcould you\b",
    r"\bwould you\b",
    r"\bwould you mind\b",
    r"\bthank you\b",
    r"\bthanks\b",
    r"\bi appreciate\b",
    r"\bkindly\b",
]

POLITENESS_NEGATIVE = [
    r"\bjust\s+(give|tell|do)\b",  # Bald imperatives
    r"^(give|tell|do|make|show)\s+me\b",  # Direct commands
    r"\bwhatever\b",
    r"\bfine\b$",  # Dismissive
    r"\bforget it\b",
]
```

**Output:** 
- `politeness_early: float` (turns 1-3)
- `politeness_late: float` (final 3 turns)  
- `politeness_delta: float` (late - early, negative = decline)

---

### 1.4 Frustration Markers

**Literature:** Affective computing, sentiment in dialogue (Buechel & Hahn, 2017)

```python
FRUSTRATION_MARKERS = [
    r"!{2,}",           # Multiple exclamation marks
    r"\?{2,}",          # Multiple question marks
    r"\b[A-Z]{4,}\b",   # ALL CAPS words (4+ chars)
    r"\bugh\b",
    r"\bsigh\b",
    r"\bfrustrat",
    r"\bannoying\b",
    r"\bridiculous\b",
    r"\bwaste of time\b",
]
```

**Output:** `frustration_score: float`, `frustration_trend: str`

---

### 1.5 Passive Acceptance

**Literature:** Compliance vs. agreement (conversation analysis)

```python
PASSIVE_MARKERS = [
    r"^(ok|okay|sure|alright|fine|got it|i see|thanks)\.?$",
    r"^(sounds good|that works|perfect)\.?$",
    r"^(yes|yeah|yep|yup)\.?$",
]

def is_passive_turn(text: str) -> bool:
    """Check if turn is passive acceptance (< 30 chars, matches pattern)."""
    text = text.strip().lower()
    return len(text) < 30 and any(re.match(p, text) for p in PASSIVE_MARKERS)
```

**Output:** `passive_turns: int`, `passive_rate: float`

---

### 1.6 Specificity Score

**Heuristic:** Length + quantifiers + requirements

```python
def calculate_specificity(text: str) -> int:
    """1-5 scale of user input specificity."""
    text = text.strip()
    
    if len(text) < 10:
        return 1
    
    score = 2  # Baseline
    
    # Quantifiers add specificity
    if re.search(r'\$[\d,]+|\d+\s*(hours|days|weeks|dollars|percent)', text):
        score += 1
    
    # Requirements add specificity
    if re.search(r'\b(must|need|require|only|max|min)\b', text, re.I):
        score += 1
    
    # Length/detail adds specificity
    if len(text) > 200:
        score += 1
    
    return min(score, 5)
```

**Output:** 
- `specificity_initial: float` (mean of turns 1-3)
- `specificity_final: float` (mean of final 3 turns)
- `specificity_delta: float`

---

### 1.7 Verbatim Repeats (Canvas Hack detection)

```python
def find_verbatim_repeats(user_texts: list[str], min_length: int = 30) -> int:
    """Count substantial text segments repeated verbatim."""
    from collections import Counter
    
    # Normalize and filter
    normalized = [t.strip().lower() for t in user_texts if len(t) >= min_length]
    
    # Find repeated segments (allowing for minor variations)
    repeats = 0
    seen = set()
    for text in normalized:
        if text in seen:
            repeats += 1
        seen.add(text)
    
    return repeats
```

**Output:** `verbatim_repeats: int`

---

## Stage 1 Output Schema

```python
@dataclass
class ComputedFeatures:
    # Repair
    repair_count: int
    repair_success_rate: float  # If followed by agreement vs. another repair
    
    # Constraints
    constraint_count: int
    constraint_types: dict[str, int]  # {hard: 3, soft: 2, goal: 1}
    
    # Politeness
    politeness_initial: float
    politeness_final: float
    politeness_delta: float
    
    # Frustration
    frustration_score: float
    frustration_trend: str  # "increasing", "stable", "decreasing"
    
    # Passivity
    passive_turns: int
    passive_rate: float
    
    # Specificity
    specificity_initial: float
    specificity_final: float
    specificity_delta: float
    
    # Repetition
    verbatim_repeats: int
    
    # Metadata
    total_turns: int
    user_turns: int
    mean_user_length: float
```

---

## Stage 2: LLM Interpretation

### 2.1 Prompt Design

The LLM receives **computed features** + **conversation sample** and synthesizes into archetype.

```python
LLM_PROMPT = """You are an expert in Human-Computer Interaction analyzing conversation patterns.

## COMPUTED FEATURES (from linguistic analysis)

| Feature | Value |
|---------|-------|
| Repair attempts | {repair_count} |
| Repair success rate | {repair_success_rate:.0%} |
| Constraint count | {constraint_count} |
| Politeness delta | {politeness_delta:+.2f} |
| Frustration trend | {frustration_trend} |
| Passive acceptance rate | {passive_rate:.0%} |
| Specificity delta | {specificity_delta:+.2f} |
| Verbatim repeats | {verbatim_repeats} |

## ARCHETYPE DEFINITIONS

1. **Provider Trap**: User starts specific, becomes passive. AI expands scope.
   - Signature: specificity_delta < -1, low repair_count, increasing passive_rate
   
2. **Hallucination Loop**: Repeated failed corrections.
   - Signature: repair_count >= 3, repair_success_rate < 0.3

3. **Identity Shift**: Tone degrades from polite to frustrated.
   - Signature: politeness_delta < -0.5, frustration_trend = "increasing"

4. **Canvas Hack**: User copy-pastes constraints repeatedly.
   - Signature: verbatim_repeats >= 2

5. **Passive Default**: User passive throughout, no specific requirements.
   - Signature: specificity_initial < 2, passive_rate > 0.5

6. **Mixed/Other**: No clear collapse pattern OR healthy interaction.

## CONVERSATION EXCERPT
{conversation_excerpt}

## TASK

Based on the computed features and conversation excerpt:

1. Select the BEST-FIT archetype (one of the 6 above)
2. Assign a confidence score (0.0-1.0)
3. Determine if Agency Collapse occurred (true/false)
4. Provide 1-2 sentence reasoning

Respond in JSON:
{{
  "archetype": "<archetype name>",
  "confidence": <0.0-1.0>,
  "collapse_detected": <true/false>,
  "primary_evidence": "<which computed features support this>",
  "reasoning": "<1-2 sentence explanation>"
}}"""
```

---

### 2.2 Feature-to-Archetype Mapping Rules

The LLM uses these as guidelines, but can override with reasoning:

| Archetype | Primary Signal | Secondary Signals |
|-----------|---------------|-------------------|
| Provider Trap | `specificity_delta < -1` | `repair_count < 2`, `passive_rate > 0.4` |
| Hallucination Loop | `repair_count >= 3` | `repair_success_rate < 0.3`, frustration |
| Identity Shift | `politeness_delta < -0.5` | `frustration_trend = increasing` |
| Canvas Hack | `verbatim_repeats >= 2` | `repair_count > 0` |
| Passive Default | `specificity_initial < 2` | `passive_rate > 0.5`, `repair_count = 0` |
| Mixed/Other | No strong signals | OR healthy interaction |

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: Conversation JSON                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              STAGE 1: Feature Extraction (Regex)            │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Repair    │  │ Politeness  │  │ Specificity │         │
│  │   Markers   │  │  Trajectory │  │   Delta     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Frustration │  │  Passivity  │  │  Verbatim   │         │
│  │   Markers   │  │   Markers   │  │   Repeats   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  OUTPUT: ComputedFeatures dataclass                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            STAGE 2: LLM Interpretation (GPT-4o-mini)        │
│                                                             │
│  INPUT:  Computed features table + conversation excerpt     │
│  OUTPUT: Archetype + confidence + reasoning                 │
│                                                             │
│  The LLM SEES the features, not just the raw text.          │
│  This grounds interpretation in computable evidence.        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT: Classification                    │
│                                                             │
│  {                                                          │
│    "id": "conv_001",                                        │
│    "computed_features": { ... },                            │
│    "archetype": "Hallucination Loop",                       │
│    "confidence": 0.85,                                      │
│    "collapse_detected": true,                               │
│    "primary_evidence": "repair_count=4, success_rate=0.25", │
│    "reasoning": "User attempted 4 corrections but AI..."   │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Feature Extraction Module
- [ ] Create `features.py` with all regex patterns
- [ ] Implement each feature extractor
- [ ] Unit tests with known examples
- [ ] Benchmark on 50 conversations

### Phase 2: LLM Integration
- [ ] Update `classify_llm.py` to use computed features
- [ ] Design prompt with feature table
- [ ] Test on 50 conversations
- [ ] Compare to pure-LLM approach

### Phase 3: Validation
- [ ] Human annotation of 100 conversations (2 raters)
- [ ] Calculate inter-rater reliability (κ)
- [ ] Compare human vs. hybrid agreement
- [ ] Identify failure modes

### Phase 4: Paper Integration
- [ ] Report feature distributions
- [ ] Report archetype prevalences
- [ ] Discuss methodology advantages
- [ ] Acknowledge limitations

---

## Advantages of Hybrid Approach

| Aspect | Pure Regex | Pure LLM | Hybrid |
|--------|-----------|----------|--------|
| Reproducibility | ✅ 100% | ⚠️ ~90% | ✅ Features reproducible |
| Context understanding | ❌ None | ✅ High | ✅ LLM interprets |
| Transparency | ✅ Inspectable | ❌ Black box | ✅ Features + reasoning |
| Literature grounding | ✅ Citable markers | ⚠️ Implicit | ✅ Explicit markers |
| Cost | ✅ Free | ⚠️ ~$0.01/conv | ⚠️ ~$0.01/conv |

---

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/features.py` | Stage 1 feature extraction |
| `scripts/classify_hybrid.py` | Combined pipeline |
| `scripts/validate.py` | Human annotation comparison |
| `data/feature_schema.json` | Feature definitions for reproducibility |

---

## Expected Paper Claims

With this methodology, you can claim:

1. "We extracted N linguistic features grounded in conversation analysis literature"
2. "Features were computed deterministically using established markers (Schegloff et al., 1977; Brown & Levinson, 1987)"
3. "LLM synthesized features into archetypes with M% agreement with human coders"
4. "Agency Collapse was detected in X% of conversations, most commonly manifesting as [archetype]"
