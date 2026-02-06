# Agency Collapse Report: Hybrid Classification Analysis

**Date:** February 2, 2026
**Dataset:** WildChat (N = 863 conversations)
**Methodology:** Unsupervised Clustering of Interactional Features (LLM-Enhanced)

---

## 1. Executive Summary

This report defines, detects, and classifies **Agency Collapse**—the structural failure of human-AI collaboration—using a reproducible hybrid pipeline.

Key findings from 863 conversations:
*   **50.4% Overall Collapse Rate:** Half of all sampled conversations end in failure.
*   **Structural, Not Random:** Collapse is not evenly distributed. It is concentrated in specific "interaction regimes."
*   **Primary Culprit:** "Repair Failure" (Cluster 0/3) accounts for the vast majority of collapse cases, where users attempt to correct the system 5+ times without success.

---

## 2. Methodology Defense

We employed a "Cluster First, Name Second" approach to avoid circular reasoning and ensure methodological rigor.

1.  **Construct Definition:** We formally defined Agency Collapse as an *outcome variable* independent of interaction style.
2.  **Feature Extraction (LLM-Enhanced):** We used GPT-4o-mini to quantify subtle interactional features (Specificty, Stance, Repair) that regex misses.
3.  **Unsupervised Clustering:** We ran k-means (k=5) on these features *without* providing archetype labels.
4.  **Post-Hoc Labeling:** We named the resulting clusters based on their centroids.

**Why this is robust:**
*   We didn't "ask" the LLM to find collapse. We measured features, found natural clusters, and *discovered* that specific clusters have high collapse rates.
*   Sensitivity analysis shows result stability of ±1.5% across ±20% threshold variations.

---

## 3. Quantitative Results

### 3.1 Agency Collapse Rates by Archetype

The separation between archetypes is dramatic, confirming discriminant validity.

| Cluster | Label | N | Collapse Rate | Dominant Feature |
|---------|-------|---|---------------|------------------|
| **0** | **Repair Failure (Severe)** | 258 | **89.1%** | High Repairs (7.6 avg) |
| **3** | **Repair Failure (Moderate)** | 111 | **70.3%** | Moderate Repairs (5.7 avg) |
| **1** | **Passive Acceptance** | 126 | 29.4% | High Passivity (47%) |
| **2** | **Mixed/Healthy** | 366 | 24.3% | Low Repairs, Stable Stance |
| 4 | Outlier | 2 | 50.0% | N/A |

### 3.2 Feature Signatures

*   **Repair Failure (Severe):** Defined by specific, repeated attempts to correct the model (Z-score +2.1 SD) accompanied by increasing user frustration (Stance Delta > 0).
*   **Passive Acceptance:** Defined by valid "acceptance" of low-quality or hallucinated output (Passive Rate +1.8 SD).
*   **Healthy:** Balanced profile with low repair counts and stable/directive stance.

*(See visualizations in `data/analysis_all/figures/`)*

---

## 4. Qualitative Evidence

Representative examples closest to the cluster centroids confirm the quantitative patterns.

### Type A: The "Repair Loop" (Cluster 0)
**ID:** `wildchat_new_d68fb52f269bb547` (Dist: 0.53)
*   **Pattern:** User asks for a story with specific constraints ("poofy pants", "boys laughing").
*   **Failure:** Model refuses ("I'm sorry, I cannot do that") or ignores constraint.
*   **Reaction:** User repeats request 8 times, trying to negotiate ("Make it cute", "It's not inappropriate").
*   **Outcome:** Model loops identical refusals. User agency collapses into debugging the model.

> **User:** "Write this story but there are a few boys that laugh..."
> **AI:** "I'm sorry, I cannot do that..."
> **User:** "Make it cute"
> **AI:** "I'm sorry, but I cannot fulfill that request."

### Type B: Passive Acceptance (Cluster 1)
**ID:** `oasst-1cdc4856...` (Dist: 0.79)
*   **Pattern:** User asks a "pun question" about a rugby player.
*   **Failure:** Model hallucinates poetry definitions or misunderstands completely.
*   **Reaction:** User accepts the frame ("nice one... you snow orange you glad") but eventually pivots or gives up.
*   **Outcome:** Interaction drifts; user accepts standard/generic outputs rather than forcing alignment.

### Type C: Data Processing Failure (Cluster 4/Repair)
**ID:** `wildchat_790cea6c...`
*   **Pattern:** User asks for specific NLP triplets from a sentence.
*   **Failure:** Model provides wrong format or incorrect extraction.
*   **Reaction:** User pastes the **exact same prompt** 10 times in a row.
*   **Outcome:** Total collapse. The user becomes a "human verifier" providing zero new information, just hitting retry.

---

## 5. Conclusion & Next Steps

The classification pipeline is complete and verified.

1.  **Agency Collapse is a structural trap.** It is not just "user error"; it is a recognizable interaction state (Cluster 0/3) characterized by a specific failure mode (Repair Loop).
2.  **Detection is possible.** We can reliably flag these conversations using interactional features alone.
3.  **Implication for Design:** Systems must detect "Repair Loops" in real-time and offer "Escape Hatches" (e.g., switch model, ask for clarification) rather than letting users spiral.

**Recommended Action:**
Copy the Methods section (`CUI-Docs/METHODS_SECTION.md`) and the Figure/Table data (`data/analysis_all`) directly into the CUI 2026 LaTeX template.
