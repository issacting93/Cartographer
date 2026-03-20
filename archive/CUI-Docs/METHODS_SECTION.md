# Methods Section: Agency Collapse Classification

## 3. Methods

### 3.1 Dataset

We analyzed N = 863 multi-turn conversations from the WildChat corpus [Zhao et al., 2024], selecting conversations with at least 10 messages to ensure sufficient interaction depth for trajectory analysis. Conversations were sampled from 1,220 available transcripts.

### 3.2 Feature Extraction

We extracted interactional features using a hybrid approach combining deterministic pattern matching with LLM-assisted classification [Buschek et al., 2023].

**Repair Detection.** For each user turn, an LLM (GPT-4o-mini) classified whether the message constituted a repair attempt—a user's effort to correct AI misunderstanding or redirect the conversation [Schegloff et al., 1977]. This approach captures contextual repair markers that pattern-matching alone misses.

**Specificity Scoring.** User message specificity was scored on a 1–5 scale, with 1 representing vague requests ("help me") and 5 representing precisely constrained requirements with quantified parameters. Specificity delta (Δ) was computed as the difference between mean specificity in the final three turns versus the initial three turns.

**Stance Classification.** Each user turn was classified on a five-point stance scale: (1) directive, (2) collaborative, (3) deferential, (4) passive, (5) frustrated. Stance delta captures shifts over the conversation trajectory.

**Passivity Rate.** The proportion of user turns classified as passive (stance ≥ 4), indicating reduced engagement or acceptance without modification.

**Additional Features.** Politeness was scored from −1 (rude) to +1 (polite), constraint expressions were counted using deontic markers, and verbatim repetitions were detected as a signal of frustrated reiteration.

### 3.3 Unsupervised Clustering

We clustered conversations using k-means on the standardized 8-dimensional feature space. Optimal k = 5 was selected using silhouette scores (silhouette = 0.156). Crucially, **no archetypes were predefined**; cluster labels were assigned post-hoc based on observed centroid characteristics.

This design choice follows best practices in exploratory analysis [Creswell, 2014]: archetypes emerge from data structure rather than being imposed a priori.

### 3.4 Agency Collapse Definition

Agency Collapse was defined independently of clustering as a binary outcome variable. A conversation exhibited collapse if **any** of the following conditions held:

1. **Repair Failure:** repair_count ≥ 5 (LLM-detected repair attempts exceeded threshold, indicating persistent misalignment)

2. **Tone Degradation:** stance_delta > 0.5 AND politeness_delta < −0.2 (user becoming more passive/frustrated with declining politeness)

3. **Specificity Collapse:** specificity_delta < −1.0 AND passive_rate > 0.4 (user became less specific while increasingly accepting AI outputs)

Thresholds were set based on distributional properties (approximately 1 SD from mean) and theoretical grounding in conversation analysis literature.

### 3.5 Post-Hoc Archetype Assignment

After clustering, we characterized each cluster by its mean feature vector and assigned descriptive labels based on dominant patterns:

| Cluster | N | Collapse Rate | Dominant Pattern | Label |
|---------|---|---------------|------------------|-------|
| 0 | 258 | **89.1%** | Highest repairs (7.6) | **Repair Failure (Severe)** |
| 1 | 126 | 29.4% | High passivity (0.47) | **Passive Acceptance** |
| 2 | 366 | 24.3% | Low repair, stable stance | Mixed/Healthy |
| 3 | 111 | 70.3% | Moderate repair (5.7) | **Repair Failure (Moderate)** |
| 4 | 2 | 50.0% | Outlier | Outlier |

### 3.6 Methodological Justification

This two-stage approach (unsupervised clustering → post-hoc labeling) provides several advantages over direct LLM classification:

1. **Reproducibility:** Features are computed deterministically; independent researchers can replicate cluster membership exactly.

2. **Transparency:** Archetype labels are grounded in observable cluster statistics, not LLM interpretation.

3. **Falsifiability:** The claim that "Repair Failure conversations show elevated collapse" is testable: collapse rates differ significantly across clusters (χ² test, p < 0.001).

4. **Theoretical Validity:** Agency Collapse is defined independently of archetypes, allowing us to examine the relationship between interaction patterns and collapse empirically.

---

## Key Claim

> "We first clustered conversations using only computable interactional features. Archetypal interaction regimes were identified post-hoc based on dominant cluster signatures. Agency Collapse was defined independently as an outcome variable and shown to concentrate unevenly across clusters."

---

## Statistical Summary (Full Dataset)

- **N = 863** qualified conversations
- **Overall collapse rate:** 50.4%
- **Primary collapse mechanism:** Repair Failure (47.3% of all conversations)
- **Highest-risk archetype:** Repair Failure Severe (Cluster 0) with **89.1%** collapse rate
- **Lowest-risk archetype:** Mixed/Healthy (Cluster 2) with **24.3%** collapse rate

---

## References

- Brown, P., & Levinson, S. C. (1987). *Politeness: Some universals in language usage*. Cambridge University Press.
- Buschek, D., et al. (2023). Identifying Human Intent in LLM-Assisted Interactions. *CHI '23*.
- Creswell, J. W. (2014). *Research Design: Qualitative, Quantitative, and Mixed Methods Approaches*. SAGE.
- Schegloff, E. A., Jefferson, G., & Sacks, H. (1977). The preference for self-correction in the organization of repair in conversation. *Language*, 53(2), 361–382.
- Zhao, L., et al. (2024). WildChat: 1M ChatGPT Interaction Logs in the Wild. *ICLR 2024*.
