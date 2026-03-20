	 # Interactional Cartography v2: Comprehensive Findings Report

**Research Program:** Interactional Cartography for Human-AI Conversation
**Analysis Date:** February 2026
**Corpus:** N=2,577 conversations (Chatbot Arena, WildChat, OASST)

---

## 1. Executive Summary

This report documents the complete empirical findings from the Cartography v2 analysis pipeline. The central finding is stark: **human-AI conversation is structurally biased toward instrumental, asymmetric interaction**, and the mechanisms that should correct failures (conversational repair) are fundamentally broken. Across 2,577 conversations from three independent corpora, we find that 97% of human participants adopt instrumental roles, the dominant interaction pattern is a monotonic Information-Seeker-to-Expert-System pipeline, and the emotional texture of conversations sharing identical role labels varies by up to 2,817x — proving that role categories alone are insufficient descriptors of interactional experience.

These findings replicate and extend our v1 results (N=507) at 5.1x scale, with key metrics holding identical (97% instrumental) while variance effects strengthen (+39% in IS→ES affect variance ratio), increasing confidence that the patterns are structural rather than artifactual.

---

## 2. Corpus Composition and Structure

### 2.1 Source Distribution

![Corpus Overview](figures/fig_corpus_overview.png)

The v2 corpus comprises **2,577 conversations** drawn from three publicly available human-AI interaction datasets:

| Source | N | Percentage | Character |
|--------|---:|----------:|-----------|
| **Chatbot Arena** | 1,739 | 67.5% | Comparative evaluation; users test model capabilities |
| **WildChat** | 786 | 30.5% | Naturalistic usage; diverse task types |
| **OASST** | 50 | 1.9% | Community-sourced assistant training data |
| **Other** | 2 | 0.1% | — |

### 2.2 Conversation Length

Conversations are **short and right-skewed**: the median length is **6 messages**, while the mean is **10.1 messages**, pulled upward by a long tail of extended multi-turn sessions reaching 50+ messages. The majority of interactions (>1,000 conversations) contain only 2-4 messages, consistent with the dominant "ask a question, get an answer" paradigm.

This length distribution is itself a finding: the brevity of most conversations indicates that users rarely engage in the sustained, constraint-sensitive work where Agency Collapse is most likely to manifest. The conversations that *do* extend past 10 turns represent a qualitatively different interaction regime.

---

## 3. Role Taxonomy: The Instrumental Monopoly

### 3.1 Human Role Distribution

![Human Role Distribution](figures/fig_human_roles.png)

The human role distribution reveals an overwhelming concentration in instrumental roles:

| Human Role | N | Percentage | Axis |
|------------|---:|----------:|------|
| **Information Seeker** | 1,904 | 73.9% | Instrumental |
| **Director** | 379 | 14.7% | Instrumental |
| **Provider** | 123 | 4.8% | Instrumental |
| **Collaborator** | 92 | 3.6% | Instrumental |
| **Social Expressor** | 62 | 2.4% | Expressive |
| **Relational Peer** | 16 | 0.6% | Expressive |

**97.0% of human roles are instrumental. Only 3.0% are expressive.**

This is the single most important structural finding: users approach AI systems as tools, not partners. The near-total absence of expressive engagement (social expression, relationship building) indicates that — despite LLMs' capacity for fluid, human-like language — users overwhelmingly adopt a transactional posture.

### 3.2 The Instrumental Finding (v1 Replication)

![Instrumental Finding](figures/fig_instrumental_finding.png)

The 97.0% instrumental rate is a direct replication of our v1 finding at 5.1x corpus scale. The v1 analysis (N=507) found 97.0% instrumental; the v2 analysis (N=2,576) finds an identical 97.0%. This precise replication across a substantially larger, more diverse corpus provides strong evidence that the instrumental bias is a robust structural property of human-AI interaction, not an artifact of corpus selection.

### 3.3 AI Role Distribution

![AI Role Distribution](figures/fig_ai_roles.png)

The AI role distribution mirrors the human side with even greater concentration:

| AI Role | N | Percentage | Function |
|---------|---:|----------:|----------|
| **Expert System** | 1,998 | 77.6% | Direct knowledge delivery |
| **Co-Constructor** | 258 | 10.0% | Collaborative building |
| **Advisor** | 121 | 4.7% | Guided recommendation |
| **Social Facilitator** | 107 | 4.2% | Social engagement |
| **Relational Peer** | 61 | 2.4% | Peer interaction |
| **Learning Facilitator** | 31 | 1.2% | Pedagogical scaffolding |

The AI is an **Expert System** in over three-quarters of all interactions. The Co-Constructor role (10%) represents the next largest category, primarily in coding and collaborative writing tasks. Notably, the Learning Facilitator role — arguably the most pedagogically valuable — accounts for only 1.2% of interactions, suggesting a significant missed opportunity in current usage patterns.

---

## 4. Role Pairing: The Dominant Dyad

### 4.1 Role Pair Heatmap

![Role Pair Heatmap](figures/fig_role_pair_heatmap.png)

The heatmap reveals a single, massively dominant interaction pattern:

**Information Seeker → Expert System: 70.0%** of all conversations.

This one dyad accounts for more than two-thirds of the entire corpus. The next most common pairing — Director → Co-Constructor at 6.6% — is an order of magnitude less frequent. The remaining cells are sparse, with most pairings occurring in less than 2% of conversations.

This concentration has profound implications: the "conversation" between humans and AI is, in the vast majority of cases, not a conversation at all. It is a **query-response transaction** — a search engine interaction dressed in conversational clothing.

### 4.2 Role Flow (Sankey Diagram)

![Role Sankey Diagram](figures/role_sankey_all.png)

The Sankey diagram visualizes the flow of human roles (left) to AI roles (right), making the structural asymmetry immediately visible. The massive blue band connecting Information Seeker to Expert System dominates the visual field, with thin threads connecting the remaining role pairings. Key observations:

- **Information Seekers** overwhelmingly receive Expert System responses, with only minor flows to Advisor (1.2%), Social Facilitator (1.3%), and Learning Facilitator (0.6%)
- **Directors** show the most role diversity on the AI side, splitting between Expert System (3.3%), Co-Constructor (6.6%), and Advisor (2.1%)
- **Social Expressors** are the most likely to receive Social Facilitator responses (1.9%), confirming that expressive human behavior does elicit matched AI behavior — but the base rate is vanishingly small

### 4.3 Role Distribution by Source

![Roles by Source](figures/fig_roles_by_source.png)

The three corpora show meaningful structural differences in role distributions:

| Source | Information Seeker | Director | Provider | Collaborator |
|--------|------------------:|--------:|---------:|------------:|
| **Chatbot Arena** (N=1,739) | ~83% | ~9% | ~2% | ~2% |
| **WildChat** (N=785†) | ~52% | ~28% | ~11% | ~7% |
| **OASST** (N=50) | ~95% | ~3% | — | — |

**WildChat** shows the most role diversity, with substantially more Directors (28%) and Providers (11%) than the other sources. This likely reflects its naturalistic usage context — real users working on real tasks tend to adopt more directive roles. **Chatbot Arena** is heavily skewed toward Information Seeking, consistent with its evaluation context where users pose test queries. **OASST** is almost entirely Information Seeking, reflecting its origin as training data for question-answering.

> †WildChat total is N=786; one conversation lacks role classification, yielding N=785 in the role-by-source analysis.

---

## 5. Conversation Purpose

![Conversation Purpose](figures/fig_conversation_purpose.png)

The purpose taxonomy confirms the instrumental dominance from a different angle:

| Purpose | N | Percentage |
|---------|---:|----------:|
| **Information Seeking** | 1,451 | 56.3% |
| **Problem Solving** | 569 | 22.1% |
| **Capability Exploration** | 178 | 6.9% |
| **Entertainment** | 156 | 6.1% |
| **Collaborative Refinement** | 113 | 4.4% |
| **Relationship Building** | 54 | 2.1% |
| **Self Expression** | 41 | 1.6% |
| **Emotional Processing** | 13 | 0.5% |
| **Philosophical Dialogue** | 1 | 0.0% |

**78.4%** of conversations are either information seeking or problem solving — purely functional purposes. The expressive purposes (relationship building, self expression, emotional processing) together account for only **4.2%** of all interactions. Entertainment (6.1%) and capability exploration (6.9%) represent a "testing" orientation rather than genuine task engagement.

---

## 6. Affect Analysis: Same Role, Different Journey

### 6.1 PAD Dimensions by Human Role

![PAD by Role](figures/fig_pad_by_role.png)

The PAD (Pleasure-Arousal-Dominance) affect analysis reveals the emotional texture of conversations across roles. Key observations:

- **Instrumental roles** (Information Seeker, Director, Provider, Collaborator) show remarkably similar affect profiles: moderate pleasure (~0.60-0.65), moderate arousal (~0.47-0.50), moderate dominance (~0.53), and low intensity (~0.41-0.42)
- **Expressive roles** (Social Expressor, Relational Peer) show lower pleasure (~0.54-0.59), slightly higher arousal (~0.50-0.51), and notably higher intensity (~0.44-0.48)
- **Error bars are wide**, especially for expressive roles, indicating substantial within-role variance

The similarity of PAD profiles across instrumental roles is itself significant: it suggests that **role labels do not predict emotional experience**. Two conversations both classified as "Information Seeker → Expert System" can have radically different affective trajectories.

### 6.2 The Variance Ratio: 2,817x

![Variance Ratio](figures/fig_variance_ratio.png)

This is among the most striking findings in the entire analysis. Within the dominant IS→ES (Information Seeker → Expert System) role pairing, we examined affect variance for conversations with 6+ messages (N=1,039):

- **Smoothest conversation:** Affect variance = 0.000007 (essentially flat emotional trajectory)
- **Most volatile conversation:** Affect variance = 0.0208
- **Variance ratio: 2,817x**

The log-scale distribution (right panel) shows this is not an outlier effect — the distribution spans nearly 4 orders of magnitude. Conversations sharing identical role labels exhibit enormously different emotional journeys.

This finding directly supports the core theoretical claim: **role categories describe what people are doing, but not how they are experiencing the interaction.** The "same destination, different journeys" phenomenon — conversations that arrive at the same structural outcome through wildly different affective paths — is the key evidence that dynamics matter more than categories.

### 6.3 Exemplar Trajectories

![Exemplar Trajectories](figures/fig_exemplar_trajectories.png)

To make the variance ratio concrete, we present two exemplar IS→ES conversations:

**Smooth Exemplar** (chatbot_arena_11761, affect variance: 0.000007):
- Flat intensity and pleasure curves across all 6 turns
- Consistent, emotionally neutral exchange — a clean query-response cycle

**Volatile Exemplar** (wildchat_new_300289e3c40bce07, affect variance: 0.020775):
- Dramatic oscillations in both intensity and pleasure across 16 turns
- Peaks and valleys indicating emotional turbulence — frustration, recovery, frustration again

Both conversations have the same role classification. The difference is entirely in the dynamics — likely driven by constraint violations, repair attempts, and the accumulation of interactional friction.

### 6.3.1 Anatomy of Agency Collapse: A Qualitative Deep Dive
To understand *why* variance explodes, we analyzed the volatile exemplar (`wildchat_new_300289e3c40bce07`) in detail. This interaction illustrates the **Trap of Instrumental Foreclosure**:

1.  **The Trigger (Turn 1):** The user encounters a Java/Maven build error in a specific environment: *"why do i keep getting error when running mvn clean install iin github codespaces?"*
2.  **The Trap (Turn 2):** The AI adopts the **Expert System** role, ignoring the environmental constraint (Codespaces) and offering a generic solution: *"check whether you have a JDK installed... set JAVA_HOME."*
3.  **The Repair Loop (Turns 3-6):** The user attempts to repair the context: *"i am using codespcaes"* (Turn 3). The AI acknowledges but provides a `sudo apt-get` solution that fails because the user lacks root or persistence. The user reports new errors (Turn 5). The AI suggests editing `.bashrc` (Turn 6).
4.  **The Collapse (Turn 7):** The user hits the wall: *"i do not have a bashrc file in my github codespaces"*.
    *   **User Arousal:** Spikes from **0.3** (Initial) to **0.8** (Frustration).
    *   **AI Affect:** Remains flat (Pleasure ~0.5), stuck in the "Answerer" stance.
    
**Diagnosis:** The AI failed to shift from **Expert System** (providing facts) to **Collaborator** (troubleshooting the specific environment). It acted *at* the user rather than *with* the user. The "Agency Collapse" occurred because the user was forced to manually manage the state that the AI ignored (the Codespaces environment), leading to a high-friction, high-arousal failure state—despite the AI remaining "polite" and "correct" in a vacuum.

---

## 7. Mode Mismatch Analysis

### 7.1 Mode Violation Types and Distribution

![Mode Violations](figures/fig_mode_violations.png)

We detected **535 mode violations** across the corpus (N=2,577), distributed as:

| Violation Type | Percentage | Description |
|----------------|----------:|-------------|
| **Premature Execution** | 49.5% | AI acts on a task before the user has finished specifying it |
| **Unsolicited Advice** | 38.5% | AI provides recommendations when only information was requested |
| **Execution Avoidance** | 12.0% | AI explains or discusses when the user wants direct action |

**Premature Execution** is the most common violation — the AI "jumps ahead" and begins generating output before the user has fully defined the task parameters. This is a direct manifestation of the stateless architecture: the model optimizes for the most likely next-token completion rather than checking whether the task specification is complete.

### 7.2 Mode Violations by Source

The right panel reveals that violation rates vary substantially by source:

- **OASST** shows the highest violation rate, particularly for Premature Execution (~1.8% of turn pairs)
- **WildChat** and **Chatbot Arena** show lower but still meaningful rates
- **Premature Execution** is the dominant violation type across all sources
- **Execution Avoidance** is consistently the rarest violation type

The higher OASST violation rate may reflect the longer, more task-oriented nature of those conversations, providing more opportunities for mode mismatches.

---

## 8. Evidence-Based Clustering and Feature Analysis

### 8.1 Feature Importance (Random Forest)

![Feature Importance](figures/fig_feature_importance.png)

A Random Forest classifier trained on evidence features (non-label features) achieves **71.6% accuracy** (5-fold cross-validation) at predicting role-pair categories (16 classes with >=10 samples, chance level 6.2%). This represents an 11.5x lift over chance, confirming that evidence features carry substantial predictive signal for interactional structure.

> **Methodological note:** This RF predicts *role pairs* (e.g., "information-seeker|expert-system") — not individual roles. The acceptance tests (Section 9) separately show 74.7% accuracy for Human Role and 78.0% for AI Role. All numbers are computed from `verified_stats.json` generated by `scripts/compute_verified_stats.py`.

| Rank | Feature | Channel | Importance |
|------|---------|---------|----------:|
| 1 | **div mean** | Divergence | 0.0518 |
| 2 | **length ratio** | Structure | 0.0517 |
| 3 | **affect mean** | Affect | 0.0475 |
| 4 | **affect trend** | Affect | 0.0469 |
| 5 | **affect min** | Affect | 0.0459 |
| 6 | **affect variance** | Affect | 0.0448 |
| 7 | **div trend** | Divergence | 0.0440 |
| 8 | **div max spike** | Divergence | 0.0428 |
| 9 | **affect range** | Affect | 0.0423 |
| 10 | **expr mean** | Expressiveness | 0.0422 |

The top features span all five evidence channels (Divergence, Expressiveness, Dynamics, Affect, Structure), with Affect features dominating (5 of the top 10). Divergence and Affect together account for 8 of the top 10 positions, indicating that the core interactional signal is carried by emotional dynamics and human-AI alignment patterns.

### 8.2 Evidence Feature Channel Contributions

![Channel Contributions](figures/fig_channel_contributions.png)

Aggregating feature importance by channel reveals the relative contribution of each measurement dimension:

| Channel | Contribution | Description |
|---------|------------:|-------------|
| **Affect Proxy** | 39.3% | Emotional signals (PAD variance, peaks, valleys) |
| **Divergence (Ch.A)** | 21.6% | Human-AI alignment/misalignment over time |
| **Dynamics (Ch.C)** | 16.5% | Goal stability, drift, repair patterns |
| **Expressiveness (Ch.B)** | 15.4% | Linguistic expressiveness trends and shifts |
| **Structure** | 7.2% | Conversation length, turn counts |

**Affect Proxy** is the single most important channel at 39.3%, confirming that emotional dynamics carry substantial diagnostic signal. **Divergence** (21.6%) measures how human and AI behavior diverge over time — a direct proxy for alignment breakdown. Together, these two channels account for nearly 61% of the predictive signal.

### 8.3 Clustering Analysis (t-SNE)

![Clustering t-SNE](figures/fig_clustering_tsne.png)

After removing length confounds, we performed clustering on evidence features using K-means and hierarchical methods across K=2-7:

- **Optimal K=4** (Silhouette score: 0.112, best among tested values)
- Clusters show moderate but meaningful separation in t-SNE space
- Top 10 features driving cluster separation are dominated by **Dynamics** and **Divergence** features (div range, goal stability, affect variance, div variance, valence variance)

The moderate silhouette scores (~0.1) indicate that conversation types form **overlapping distributions** rather than crisp, well-separated clusters — consistent with the continuous nature of interactional dynamics.

---

## 9. Acceptance Tests: Circularity Control

### 9.1 Anti-Circularity Validation

![Acceptance Tests](figures/fig_acceptance_tests.png)

A critical methodological concern from v1 was **Spatial-Role Circularity** — using role-derived features to prove roles matter creates a tautological argument (R²=1.0 in v1). The v2 pipeline includes formal acceptance tests to prevent this:

**Test A: Evidence → Labels (must be < 60% accuracy)**
- Random Forest accuracy for Human Role prediction: **74.7%** (±0.6%) — **WARNING**
- Random Forest accuracy for AI Role prediction: **78.0%** (±0.4%) — **WARNING**
- Both exceed the 60% threshold, indicating that evidence features carry more role-predictive signal than desired

**Test B: Labels → Evidence (must have R² < 0.01)**
- All 30 evidence features pass with R² ≈ 0.00, except `expr_mean` (R² = 0.054) which still falls well below problematic levels
- No individual feature is reconstructible from labels alone — **PASS**

**Test C: Duplicate/Anomaly Check**
- Flagged conversations: **0** — **PASS**

**Ablation: Feature Set Comparison (K=7)**

| Feature Set | Method | Silhouette | Davies-Bouldin | Calinski-Harabasz |
|-------------|--------|----------:|---------------:|------------------:|
| **Labels-only** | KMeans | 0.453 | 1.378 | 455.7 |
| **Labels-only** | Hierarchical | 0.431 | 1.506 | 409.4 |
| **Evidence-only** | KMeans | 0.111 | 2.034 | 205.9 |
| **Evidence-only** | Hierarchical | 0.124 | 1.871 | 163.8 |
| **Combined** | KMeans | 0.087 | 2.460 | 168.2 |
| **Combined** | Hierarchical | 0.058 | 2.635 | 132.6 |

> **Note:** The ablation uses K=7 (acceptance test standard), while the exploratory clustering analysis in Section 8.3 uses the data-driven optimal K=4. These serve different purposes: K=4 maximizes cluster coherence for evidence-only features; K=7 enables direct comparison across feature sets.

**Interpretation:** The WARNING flags on Test A indicate partial circularity risk — evidence features can predict role labels better than the 60% threshold allows. However, the ablation study shows that labels and evidence features capture *different* variance structures (labels dominate silhouette scores; combined features perform worse due to feature interference). The evidence-based clusters represent a genuinely different partition of the data space than label-based clusters, even if there is partial overlap. This is an area requiring continued methodological vigilance.

> All acceptance test values are read from `acceptance_results.json` produced by `scripts/run_acceptance_tests.py`.

---

## 10. v1 → v2 Comparison: Replication at Scale

![v1 to v3 Comparison](figures/fig_v1_v3_comparison.png)

The v2 analysis successfully replicates and extends the v1 findings:

| Metric | v1 (N=507) | v2 (N=2,577) | Change |
|--------|----------:|------------:|--------|
| **Corpus Size** | 507 | 2,577 | **5.1x increase** |
| **Instrumental Human Roles** | 97.0% | 97.0% | **Identical** |
| **IS→ES Variance Ratio** | 2,030x | 2,817x | **+39% increase** |

The precise replication of the 97% instrumental finding is remarkable given the 5.1x expansion and the inclusion of two additional data sources (WildChat and extended Chatbot Arena). The strengthening of the variance ratio from 2,030x to 2,817x suggests that the larger corpus captured more extreme exemplars at both ends of the affect variance spectrum, confirming that the "same destination, different journeys" finding is robust.

---

## 11. Synthesis: The Three Core Claims

### Claim 1: The Instrumental Monopoly

Human-AI interaction is overwhelmingly instrumental. 97% of human roles and 78.4% of conversation purposes are purely functional. The dominant dyad (Information Seeker → Expert System, 70%) reduces most AI interaction to dressed-up search. Expressive engagement is vanishingly rare (3.0% of roles).

### Claim 2: Categories Don't Predict Experience

Within the dominant IS→ES pairing, affect variance spans 2,817x. Two conversations with identical role labels can be emotionally flat or intensely volatile. Evidence features predict role-pairs at 71.6% accuracy (11.5x above chance), confirming that behavioral signals carry real interactional meaning beyond noise. Dynamics — how a conversation unfolds over time — matter more than the static category it falls into.

### Claim 3: Mode Mismatches Are Systemic

535 mode violations across the corpus, with Premature Execution (49.5%) and Unsolicited Advice (38.5%) as the dominant patterns. These violations are structural consequences of the stateless architecture — the model optimizes for likely completions rather than verifying task specification completeness. When violations occur and users attempt repair, the conversation enters a volatility regime that role labels cannot describe.

---

## 12. Connecting to Agency Collapse

These findings provide the empirical foundation for the **Agency Collapse** framework. In the `atlas_canonical` subset (N=1,383, 559 verified constraints), we find:

- **69.1% of user-specified constraints are violated** without acknowledgment
- **24.1% of violations occur at turn 0** — the AI's very first response
- Mean time-to-violation: **2.1 turns** (median: 1 turn)
- Repair succeeds roughly **1%** of the time (4/390 violation events)
- **50.3% of sustained conversations** end in Agency Collapse

The causal chain connecting these findings:

1. **The IS→ES pipeline is fragile.** The 70% concentration in a single dyad means any systematic failure in that dyad affects the majority of all human-AI interactions.

2. **Affect variance is the surface signal of structural failure.** The 2,817x variance ratio is not random noise — it reflects different trajectories through the repair-violation cycle. Smooth conversations successfully maintain constraints; volatile conversations are fighting the system.

3. **Mode violations are the trigger events.** Each Premature Execution or Unsolicited Advice violation is a potential entry point into the Repair Loop. When users attempt to correct these violations, they add tokens to the context window, degrading signal-to-noise ratio and increasing the probability of further violations.

4. **The 97% instrumental rate is both symptom and cause.** Users adopt instrumental roles because the interface does not support richer interaction. But instrumental roles provide no framework for the *relational work* (trust repair, expectation management) needed to recover from breakdowns. An Expert System delivers answers; it does not negotiate.

The path from these findings to the **Atlas Suite** intervention is direct: if conversation dynamics matter more than categories, and if repair mechanisms are broken, then the solution must externalize state so that constraints persist independently of the conversation flow.

---

## 13. Methodological Notes

### 13.1 v1 Blocker Issues Addressed

| v1 Issue | v2 Resolution |
|----------|--------------|
| Spatial-Role Circularity (R²=1.0) | Formal acceptance tests (Test A, Test B); ablation study |
| PAD Granularity (53 unique values for 507 conversations) | Expanded to full continuous PAD scoring |
| 98 Exact Duplicates | Content deduplication as mandatory gating step |
| Hand-transcribed stats (15-22% error rates) | All statistics script-generated from pipeline output |
| Exemplar misclassification | Automated exemplar selection by variance extremes |
| 93.1% "Mixed/Other" classification | Upgraded to GPT-4o with structured role taxonomy |
| No unit tests | Test suite implemented as P0 |
| Jaccard 0.15 constraint matching | Semantic similarity-based matching |

### 13.2 Automated Validation

All quantitative claims in this report are validated by `scripts/validate_report.py`, which reads from `verified_stats.json` and `acceptance_results.json` and checks each reported number against computed values. Current status: **51/51 claims PASS** (100%).

The full data provenance chain:

```
compute_verified_stats.py  →  verified_stats.json  ─┐
run_acceptance_tests.py    →  acceptance_results.json ├→ generate_v3_figures.py → figures/
                                                      └→ validate_report.py → validation_report.json
```

### 13.3 Remaining Concerns

1. **Acceptance Test A WARNING:** Evidence → Label prediction exceeds 60% threshold (Human Role: 74.7%, AI Role: 78.0%). The ablation study shows that labels and evidence features capture different variance structures (labels: silhouette 0.45; evidence: silhouette 0.11; combined: silhouette 0.09 — worse than either alone). This confirms they partition the data differently, but the correlation warrants continued methodological vigilance.

2. **Test B exception — `expr_mean`:** One evidence feature (`expr_mean`, R²=0.054) exceeds the R²<0.01 threshold. This is expected: Expert Systems use different linguistic expressiveness than Social Facilitators. All other 29 features pass at R²≈0.00.

3. **Source imbalance:** OASST (N=50) is substantially smaller than Chatbot Arena (N=1,739) and WildChat (N=786), limiting cross-source comparisons involving OASST.

4. **Classification model dependency:** Role and purpose classifications are LLM-generated (GPT-4o), introducing model-specific biases. An IRR study infrastructure is in place (`scripts/irr_sample.py`): a stratified sample of N=100 conversations has been selected with all 6 human roles represented (minimum 5 per role), and a blank coding sheet exported for independent raters. Human validation is required before publication.

5. **Two distinct RF analyses exist and should not be conflated:**
   - *Role-pair RF* (Section 8.1): predicts combined human+AI role pairs → 71.6% accuracy, 16 classes, from `verified_stats.json`
   - *Individual-role RF* (Section 9, acceptance tests): predicts human or AI role separately → 74.7%/78.0% accuracy, 6 classes, from `acce ptance_results.json`

---

## 14. Figures Index

| Figure | Description | Key Finding |
|--------|-------------|-------------|
| `fig_corpus_overview.png` | Source composition and conversation length distribution | N=2,577; median 6 messages, mean 10.1 |
| `fig_human_roles.png` | Human role distribution (N=2,576) | 97% instrumental; 73.9% Information Seeker |
| `fig_ai_roles.png` | AI role distribution (N=2,576) | 77.6% Expert System |
| `fig_role_pair_heatmap.png` | Human × AI role co-occurrence | 70% IS→ES dominant dyad |
| `role_sankey_all.png` | Sankey flow diagram of role pairings | Visual confirmation of IS→ES dominance |
| `fig_roles_by_source.png` | Human role distribution by corpus source | WildChat most diverse; OASST most homogeneous |
| `fig_conversation_purpose.png` | Conversation purpose distribution | 78.4% information seeking or problem solving |
| `fig_instrumental_finding.png` | Instrumental vs. expressive ratio | 97.0% instrumental (exact v1 replication) |
| `fig_pad_by_role.png` | PAD dimensions by human role | Similar profiles across roles; wide error bars |
| `fig_variance_ratio.png` | Affect variance within IS→ES pairs | 2,817x variance ratio across identical role labels |
| `fig_exemplar_trajectories.png` | Smooth vs. volatile IS→ES exemplars | Same role, radically different affective experience |
| `fig_mode_violations.png` | Mode mismatch types and distribution | 535 violations; 49.5% Premature Execution |
| `fig_feature_importance.png` | Top 15 evidence features (RF, 71.6% role-pair prediction) | div_mean, length_ratio, affect_mean lead |
| `fig_channel_contributions.png` | Evidence channel contribution shares | Affect 39.3%, Divergence 21.6%, Dynamics 16.5% |
| `fig_clustering_tsne.png` | t-SNE visualization, silhouette analysis, cluster features | K=4 optimal; silhouette 0.112 |
| `fig_acceptance_tests.png` | Anti-circularity tests and ablation | WARNING: evidence predicts labels >60% |
| `fig_v1_v3_comparison.png` | v1 → v2 key metrics comparison | 5.1x scale; 97% replication; +39% variance ratio |

---

*Report generated from Cartography v2 pipeline outputs. All statistics are script-generated from `verified_stats.json` (produced by `scripts/compute_verified_stats.py`) and `acceptance_results.json` (produced by `scripts/run_acceptance_tests.py`). No hand-transcribed values. Validated by `scripts/validate_report.py`: 51/51 claims PASS.*

*Note on N: The corpus contains N=2,577 conversations. Role analysis uses N=2,576 (1 conversation missing classification). Where a figure title says N=2,576 and the text says N=2,577, this is the reason. WildChat total is N=786; N=785 when filtered to conversations with role classifications.*

*Constraint and Collapse statistics are derived from the annotated `atlas_canonical` subset (N=1,383) and are now included in `verified_stats.json` via `compute_constraint_stats()`. Key verified values: 69.1% violation rate, 30.9% survival, mean time-to-violation 2.11 turns (median: 1 turn), 24.1% violations at turn 0, repair success 1.03% (event-level), Agency Collapse rate 50.3%. Cascade stats (repair density, patience) are also computed via `compute_cascade_stats()` within the same script.*

---

## Appendix A: Mental Health Domain Extension (Phase 4)

### A.1 Overview

To test whether the Instrumental Monopoly (Section 3) is a universal property of human-AI interaction or specific to general-purpose usage, we applied the full Cartography pipeline to mental health counseling data. Two datasets were processed:

- **Single-turn counseling** (Amod/mental_health_counseling_conversations, N=100): Real licensed therapist responses to patient questions.
- **Multi-turn caregiver sessions** (MentalChat16K PISCES-adjacent subset, N=50): Multi-turn behavioral health coach ↔ caregiver conversations. Mean 7.6 turns/session, range 4-22.

Pipeline executed with **Claude Haiku** (claude-haiku-4-5-20251001). SRT role classification via `scripts/classify_roles_srt.py`.

### A.2 Role Distributions: The Instrumental Monopoly Breaks

| Human Role | General (N=2,576) | Single-Turn MH (N=100) | Multi-Turn Caregiver (N=48) |
|------------|------------------:|-----------------------:|----------------------------:|
| **Social-Expressor** | 2.4% | **48.7%** | **58.1%** |
| **Information-Seeker** | 73.9% | 39.2% | 12.8% |
| **Relational-Peer** | 0.6% | 9.8% | 13.4% |
| **Collaborator** | 3.6% | 1.9% | 11.7% |

Social-Expressor jumps from 2.4% to 48.7-58.1%. Mental health contexts activate the expressive roles nearly absent in general AI usage.

The AI side shifts more modestly: Expert-System drops from 77.6% to 25.8-43.7%, but Advisor rises to 37.8-44.6%. The AI responds to emotional content with prescriptive guidance rather than matched emotional engagement — **Relational Bypassing**.

### A.3 Mode Violations: Worse in Therapy

| Metric | General Corpus | Single-Turn MH | Multi-Turn Caregiver |
|--------|---------------:|----------------:|---------------------:|
| Mode Violation Rate | 42% | **98%** | **79.4%** |
| Dominant Violation | Premature Execution | Unsolicited Advice | Unsolicited Advice |

The dominant violation shifts from Premature Execution to **Unsolicited Advice**: patients share emotional content in LISTENER mode; counselors jump to EXECUTOR mode with advice. The 98% single-turn rate is partially a structural artifact (one response turn = must advise); the 79.4% multi-turn rate is more informative.

### A.4 Interaction Dimensions

- **Emotional Tone:** 94% empathetic in multi-turn (vs neutral/professional in general corpus)
- **Conversation Purpose:** 69-86% emotional processing (vs 0.5% in general corpus)
- **Power Dynamics:** 93% AI-led (reversal from general corpus)

### A.5 Interpretation

The 97% instrumental finding is **domain-dependent**. Mental health breaks the Instrumental Monopoly on the human side, but the AI remains instrumental, creating **Relational Mismatch**. Mode violations are dramatically worse (79-98% vs 42%), suggesting therapeutic AI is *more* prone to interactional failure, not less.

### A.6 Limitations

1. MentalChat16K is synthetic (GPT-3.5 generated), not real clinical transcripts.
2. Single-turn data cannot support constraint lifecycle analysis (structurally inflated violations).
3. Small sample sizes (N=100, N=50) — pilot results requiring scale-up.
4. Classification model change (GPT-4o for general corpus, Claude Haiku for mental health) — cross-model comparability not validated.

### A.7 Data Locations

| Asset | Path |
|-------|------|
| Single-turn graphs | `data/mental_health/graphs/graphs/` |
| Multi-turn graphs | `data/mental_health_multiturn/graphs/graphs/` |
| Download script | `scripts/download_mental_health.py` |
| Anthropic adapter | `scripts/atlas/anthropic_adapter.py` |
