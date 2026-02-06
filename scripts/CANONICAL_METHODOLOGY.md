# CANONICAL METHODOLOGY: Agency Collapse Classification

> **This is the authoritative methodology document. All other plans are superseded.**

---

## Core Principle

**Archetypes are NOT predefined categories.**  
**Archetypes are post-hoc labels assigned to empirically derived clusters.**

---

## Pipeline Overview

```
STEP 0: Define constructs (theoretical)
    ↓
STEP 1: Extract features (deterministic)
    ↓
STEP 2: Cluster conversations (unsupervised)
    ↓
STEP 3: Characterize clusters (descriptive statistics)
    ↓
STEP 4: Define Agency Collapse (outcome variable)
    ↓
STEP 5: Name archetypes (post-hoc labeling)
    ↓
STEP 6: LLM summarization (optional, bounded)
    ↓
STEP 7: Validation (stability + human agreement)
```

---

## STEP 0 — Define Constructs (Before Any Data)

### What We Define

| Construct | Definition |
|-----------|------------|
| **Agency Collapse** | Theoretical: user's capacity to direct interaction degrades over time |
| **Repair** | User attempts to correct AI misunderstanding |
| **Passivity** | User accepts AI output without modification |
| **Specificity** | Precision of user's stated requirements |
| **Politeness** | Markers of face-saving behavior |
| **Repetition** | Verbatim restatement of prior content |

### What We Do NOT Define Yet

- Provider Trap ❌
- Hallucination Loop ❌  
- Identity Shift ❌
- Canvas Hack ❌
- Passive Default ❌

**These names do not exist until Step 5.**

---

## STEP 1 — Feature Extraction (Deterministic)

### Feature Set

| Feature | Type | Computation |
|---------|------|-------------|
| `repair_count` | int | Count of repair markers |
| `repair_success_rate` | float | Repairs followed by agreement / total repairs |
| `constraint_count` | int | Total constraints stated |
| `constraint_types` | dict | {hard: n, soft: n, goal: n} |
| `politeness_initial` | float | Mean politeness score, turns 1-3 |
| `politeness_final` | float | Mean politeness score, final 3 turns |
| `politeness_delta` | float | final - initial |
| `frustration_score` | float | Count of frustration markers / user turns |
| `frustration_trend` | str | "increasing" / "stable" / "decreasing" |
| `passive_rate` | float | Passive turns / user turns |
| `specificity_initial` | float | Mean specificity, turns 1-3 |
| `specificity_final` | float | Mean specificity, final 3 turns |
| `specificity_delta` | float | final - initial |
| `verbatim_repeats` | int | Count of repeated text blocks |
| `total_turns` | int | Total messages |
| `mean_user_length` | float | Mean chars per user message |

### Output

```
X ∈ ℝ^(N × D)  — feature matrix, no labels
```

---

## STEP 2 — Unsupervised Clustering

### Primary Method: HDBSCAN

```python
from hdbscan import HDBSCAN

clusterer = HDBSCAN(
    min_cluster_size=10,
    min_samples=5,
    metric='euclidean',
    cluster_selection_method='eom'
)
labels = clusterer.fit_predict(X_scaled)
```

### Secondary Check: k-means

```python
from sklearn.cluster import KMeans

for k in range(4, 8):
    km = KMeans(n_clusters=k, random_state=42)
    km.fit(X_scaled)
    # Compare silhouette scores
```

### Output

- `cluster_labels`: array of cluster IDs (-1 = noise)
- `n_clusters`: number of clusters found

**At this point: NO archetypes, NO collapse labels.**

---

## STEP 3 — Cluster Characterization

### For each cluster, compute:

```python
cluster_stats = {
    'cluster_id': k,
    'n': count,
    'pct': count / total,
    'mean_repair_count': ...,
    'mean_passive_rate': ...,
    'mean_specificity_delta': ...,
    'mean_politeness_delta': ...,
    'mean_verbatim_repeats': ...,
    # z-scores relative to population
    'z_repair': ...,
    'z_passive': ...,
    ...
}
```

### Example Output Table

| Cluster | N | Repair | Passive | Spec Δ | Polite Δ | Repeats |
|---------|---|--------|---------|--------|----------|---------|
| 0 | 89 | 4.2 | 0.31 | -1.4 | -0.3 | 0.2 |
| 1 | 112 | 0.8 | 0.62 | -0.9 | +0.1 | 0.1 |
| 2 | 67 | 1.5 | 0.28 | -0.3 | -0.7 | 2.4 |
| 3 | 45 | 0.4 | 0.75 | +0.2 | +0.2 | 0.0 |
| -1 | 80 | 1.9 | 0.41 | -0.5 | -0.2 | 0.3 |

**This is pure description. No interpretation yet.**

---

## STEP 4 — Define Agency Collapse (Outcome Variable)

### Definition (Deterministic)

```python
def has_agency_collapse(features: dict) -> bool:
    """
    Agency Collapse = TRUE if ANY of these conditions:
    """
    # Condition A: Repeated failed repairs
    if features['repair_count'] >= 3 and features['repair_success_rate'] < 0.3:
        return True
    
    # Condition B: Tone degradation
    if features['politeness_delta'] < -0.5 and features['frustration_trend'] == 'increasing':
        return True
    
    # Condition C: Specificity collapse with passivity
    if features['specificity_delta'] < -1.0 and features['passive_rate'] > 0.4:
        return True
    
    return False
```

### Key Distinction

| Concept | What It Is |
|---------|------------|
| **Collapse** | An outcome variable (binary) |
| **Archetype** | A cluster pattern (categorical) |

**Collapse ≠ Archetype**

A conversation can show collapse without fitting a named archetype, and vice versa.

---

## STEP 5 — Post-hoc Archetype Naming

### Process

1. Inspect cluster signatures from Step 3
2. Identify dominant interactional pattern
3. Assign descriptive label

### Example Naming

| Cluster | Signature | Post-hoc Label |
|---------|-----------|----------------|
| 0 | High repair, low success | "Repair Failure" |
| 1 | High passivity, low repair | "Passive Acceptance" |
| 2 | High verbatim repeats | "Constraint Repetition" |
| 3 | Stable, low distress | "Healthy Interaction" |
| -1 | No clear pattern | "Mixed/Noise" |

**Names are:**
- Cluster-level (not per-instance)
- Descriptive (match the statistics)
- Not assumed in advance

---

## STEP 6 — LLM Role (Strictly Bounded)

### LLM Does NOT:
- Discover clusters
- Decide collapse
- Override rules

### LLM ONLY:
- Summarizes cluster patterns in natural language
- Checks whether post-hoc label matches statistics
- Explains borderline cases (optional)

### Example LLM Prompt

```
Given this cluster's statistics:
- Mean repair: 4.2, Success rate: 0.25
- Mean passive rate: 0.31
- Mean specificity delta: -1.4

The cluster has been labeled "Repair Failure".

Task: Write a 2-sentence description of this interaction pattern 
for the paper's Results section.
```

**LLM is assistant to analyst, not judge.**

---

## STEP 7 — Validation

### Three Separate Validations

| What | Method | Target |
|------|--------|--------|
| **Clustering stability** | Silhouette score, persistence across samples | > 0.3 |
| **Collapse agreement** | Human κ on collapse yes/no | > 0.70 |
| **Archetype label agreement** | Human κ on cluster labels | > 0.65 |

---

## What This Plan Prevents

❌ "You invented archetypes first"  
❌ "The LLM decided everything"  
❌ "Agency Collapse is vague"  
❌ "This is just qualitative labeling"  

---

## What This Plan Enables You to Claim

> "We first clustered conversations using only computable interactional features. Archetypal interaction regimes were identified post-hoc based on dominant cluster signatures. Agency Collapse was defined independently as an outcome variable and shown to concentrate unevenly across clusters."

**This sentence is bulletproof.**

---

## Implementation Files

| File | Purpose |
|------|---------|
| `scripts/features.py` | Step 1: Feature extraction |
| `scripts/cluster.py` | Steps 2-3: Clustering + characterization |
| `scripts/collapse.py` | Step 4: Collapse detection |
| `scripts/name_archetypes.py` | Step 5-6: Post-hoc naming |
| `scripts/validate.py` | Step 7: Validation metrics |

---

## Thresholds (Adjustable)

| Threshold | Default | Justification |
|-----------|---------|---------------|
| `repair_count >= 3` | 3 | Schegloff: 3+ = persistent breakdown |
| `repair_success < 0.3` | 30% | Majority failure |
| `politeness_delta < -0.5` | -0.5 | ~1 SD decline |
| `specificity_delta < -1.0` | -1.0 | 1 point on 5-point scale |
| `passive_rate > 0.4` | 40% | Near majority |
| `min_cluster_size` | 10 | HDBSCAN default |
