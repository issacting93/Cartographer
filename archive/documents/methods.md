# Methods Inventory

Complete inventory of classification, analysis, and visualization methods across Cartography v1 (role mapping) and v2 (constraint/repair analysis). All file paths verified against source.

---

## 1. Classification Methods

### 1.1 LLM-Based Classification

#### v1 — Role & Dimension Classification

| # | Method | Model | File | Output |
|---|--------|-------|------|--------|
| 1 | 8-Dimension Classifier | GPT-4o-mini | `classifier/classifier-openai.py` | 8 categorical dimensions: interactionPattern, powerDynamics, emotionalTone, engagementStyle, knowledgeExchange, conversationPurpose, topicDepth, turnTaking |
| 2 | Social Role Theory Classifier | GPT-4o (default), GPT-5.2 (production run) | `classifier/classifier-openai-social-role-theory.py` | 12-role taxonomy with probability distributions. Human: information-seeker, provider, director, collaborator, social-expressor, relational-peer. AI: expert-system, learning-facilitator, advisor, co-constructor, social-facilitator, relational-peer |
| 3 | Claude Classifier | Claude Sonnet 4 (`claude-sonnet-4-20250514`) | `classifier/classifier-v1.1.py` | 8 dimensions + early 6-role taxonomy (seeker, learner, director, collaborator, sharer, challenger) + windowed temporal classification |
| 4 | Local LLM Classifier | Llama 2 (default; supports any Ollama model) | `classifier/classifier-ollama.py` | Same taxonomy as #1 (cost-effective local alternative) |
| 5 | HuggingFace Classifier | Transformer models | `classifier/classifier-huggingface.py` | Same taxonomy as #1 (lightweight alternative) |
| 6 | Few-Shot Classifiers | GPT-4o-mini, Qwen 2.5:7b | `classifier/classifier-openai-fewshot.py`, `classifier/classifier-ollama-fewshot.py` | Same taxonomy with example-guided prompts for improved accuracy |
| 7 | Reduced Role Classifier | GPT-4o-mini | `classifier/classifier-openai-reduced-roles.py` | Simplified 3+3 taxonomy. Human: information-seeker, social-expressor, co-constructor. AI: facilitator, expert-system, relational-peer |
| 8 | PAD Scoring | GPT-4o-mini | `scripts/generate-pad-with-llm-direct.py` | Per-message Pleasure, Arousal, Dominance scores (-1 to +1) + emotional intensity (0 to 1). Processes in batches maintaining conversational context |

#### v2 — Structural & Behavioural Classification

| # | Method | Model | File | Output |
|---|--------|-------|------|--------|
| 9 | Move Classifier (Hybrid) | GPT-4o-mini + regex | `scripts/atlas/move_classifier.py` | 13-move taxonomy across 4 categories. **Constraint lifecycle:** PROPOSE_CONSTRAINT, ACCEPT_CONSTRAINT, VIOLATE_CONSTRAINT, RATIFY_CONSTRAINT. **Repair:** REPAIR_INITIATE, REPAIR_EXECUTE, ABANDON_CONSTRAINT. **Task:** STATE_GOAL, TASK_SHIFT, GENERATE_OUTPUT. **Interactional:** REQUEST_CLARIFICATION, PROVIDE_INFORMATION, PASSIVE_ACCEPT. Validated: κ=0.78, N=434 |
| 10 | Task-First Classifier | GPT-4o-mini | `scripts/atlas/pipeline/classify_task_first.py` | 5 stability states: Task Maintained, Constraint Drift, Agency Collapse, Task Shift, No Constraints. Includes constraint quality filter (rejects aspirational/meta-goal constraints), smart truncation, hash-based caching |
| 11 | Archetype Classifier | GPT-4o-mini | `scripts/atlas/pipeline/classify_llm.py` | 6 archetypes: Provider Trap, Hallucination Loop, Identity Shift, Canvas Hack, Passive Default, Mixed/Other. Returns archetype + confidence + collapse_detected + specificity_trend |
| 12 | Dataset Classifier (4-Layer) | GPT-4o-mini | `scripts/atlas/pipeline/classify_dataset.py` | Layer 1: Metadata (source, domain, complexity). Layer 2: Turn-level coding (constraint/violation/repair events). Layer 3: Trajectory metrics (specificity trajectory, ACI score). Layer 4: Archetype assignment based on trajectory patterns |
| 13 | LLM Feature Extraction | GPT-4o-mini | `scripts/atlas/pipeline/features_llm.py` | Per-turn scoring: specificity (1-5), stance (1-5: directive→frustrated), politeness (-1 to +1), repair detection (boolean). Derived: passive_rate (turns with stance ≥ 4) |

### 1.2 Rule-Based / Regex Classification

| # | Method | File | Output |
|---|--------|------|--------|
| 14 | Mode Detector | `scripts/atlas/mode_detector.py` | **User mode** (regex): LISTENER, ADVISOR, EXECUTOR, AMBIGUOUS. **AI mode** (structural): by response length, code blocks, evaluative language. **Mode violations:** UNSOLICITED_ADVICE (user=LISTENER, AI advises), PREMATURE_EXECUTION (user=ADVISOR, AI generates), EXECUTION_AVOIDANCE (user=EXECUTOR, AI questions) |
| 15 | Constraint Tracker (FSM) | `scripts/atlas/constraint_tracker.py` | Deterministic state machine: STATED → ACTIVE → {VIOLATED, REPAIRED, ABANDONED, SURVIVED}. Hardness classification: hard (`must`, `require`), soft (`prefer`, `ideally`), goal (`want to`, `looking for`). Matching via Jaccard similarity |
| 16 | Agency Collapse Detector | `scripts/atlas/pipeline/collapse.py` | 3 conditions (any triggers collapse): **A** — repair failure (≥3 repairs, success <30%). **B** — tone degradation (politeness Δ < -0.5). **C** — specificity collapse (Δ < -1.0 + passive rate > 40%). Returns: boolean + confidence + conditions met |
| 17 | Regex Feature Extraction | `scripts/atlas/pipeline/features.py` | Deterministic per-conversation features: repair_count, repair_success_rate, constraint_count (hard/soft/goal), politeness (initial/final/delta, Brown & Levinson patterns), frustration (score/trend, `!{2,}`, `\b[A-Z]{4,}\b`), passive_rate (`^(ok|sure|thanks)\.?$`), specificity (1-5), verbatim_repeats (30+ char) |
| 18 | Evidence Feature Extraction | `scripts/evidence_features.py` (v1) | 30 leak-proof features (all R² < 0.01 with classification labels) across 4 channels: **Affect** (11 features, 37.3% importance): enriched emotional intensity, 503 unique values. **Expressiveness** (7, 21.5%): functional-social orientation. **Linguistic Divergence** (5, 17.7%): paired-turn cosine similarity. **Interaction Dynamics** (8, 15.4%): corrections, constraints, hedging, goal drift. + Structure (1, 8.1%): conversation length |
| 19 | Quadrant Classification | various coordinate scripts (v1) | Rule-based spatial positioning. X: Functional↔Social (132 unique values). Y: Aligned↔Divergent (216 unique values). 360 unique (X,Y) positions. 4 quadrants: Functional-Aligned, Functional-Divergent, Social-Aligned, Social-Divergent |

### 1.3 ML / Unsupervised Methods

| # | Method | Library | File | Details |
|---|--------|---------|------|---------|
| 20 | K-Means | sklearn | `scripts/cluster-paths-proper.py` (v1) | Optimal k via silhouette score (tested k=2-15). Features: trajectory + classification features. Produces 7 validated clusters |
| 21 | Hierarchical Agglomerative | sklearn | `scripts/cluster-paths-proper.py` (v1) | Alternative to K-means, used in acceptance tests for robustness |
| 22 | DBSCAN | sklearn | `scripts/cluster-paths-proper.py` (v1) | Density-based, eps=0.5, min_samples=3. Handles noise points (cluster -1) |
| 23 | HDBSCAN | hdbscan | `scripts/atlas/pipeline/cluster.py` (v2) | Primary v2 clustering. min_cluster_size=10, min_samples=5, Euclidean distance |
| 24 | K-Means (v2) | sklearn | `scripts/atlas/pipeline/cluster.py` (v2) | Robustness check for HDBSCAN. k=3-10, silhouette-optimized, n_init=10 |
| 25 | Random Forest | sklearn | `scripts/cluster-paths-proper.py` (v1) | Feature importance analysis via n_estimators=100 + 5-fold cross-validation. Not a classifier per se — used to identify which evidence features best separate clusters |
| 26 | t-SNE | sklearn | `scripts/cluster-paths-proper.py` (v1) | Dimensionality reduction (high-D → 2D). perplexity=30, n_iter=1000. Used for cluster separation visualization only |

### 1.4 Statistical Validation

| # | Method | File | Purpose |
|---|--------|------|---------|
| 27 | Mann-Whitney U | `scripts/analysis/scientific_analysis.py` (v2) | Non-parametric comparison: healthy vs collapsed conversations |
| 28 | Independent t-Test | `scripts/analysis/scientific_analysis.py` (v2) | Parametric reference for same comparison |
| 29 | Spearman / Pearson Correlation | `scripts/analysis/scientific_analysis.py` (v2) | Repair count vs PAD volatility relationship |
| 30 | Cohen's d | `scripts/analysis/scientific_analysis.py` (v2) | Effect size for collapse vs non-collapse |
| 31 | Silhouette / Davies-Bouldin / Calinski-Harabasz | `scripts/cluster-paths-proper.py` (v1) | Cluster quality validation. Silhouette: -1 to 1. D-B: lower = better. C-H: variance ratio |

---

## 2. Visualization Methods

### 2.1 3D Visualizations

| # | Type | Library | File | Description |
|---|------|---------|------|-------------|
| 1 | Interactive Terrain | Three.js + WebGL | `src/components/ThreeScene.tsx` (v1) | Heightmap terrain mesh with pole markers (user vs assistant), dashed path lines (Line2), contour lines at minor/major/index levels, drop lines, distance lines. Post-processing: UnrealBloomPass glow. Controls: OrbitControls (isometric), raycasting hover/click. Custom TerrainFresnelShader |
| 2 | 3D Scatter | Matplotlib Axes3D | `scripts/create-3d-dataset-visualization.py` (v1) | 3-panel subplot comparing datasets (OASST, WildChat, Chatbot Arena). Color-coded by source. X-Y-Z spatial distribution |

### 2.2 Static Charts (Python)

| # | Type | Library | File | Description |
|---|------|---------|------|-------------|
| 3 | Density Heatmap | Matplotlib + scipy KDE | `scripts/render-density-map-538.py` (v1) | Gaussian kernel density estimation via `scipy.stats.gaussian_kde`. Grid-based with scatter overlay |
| 4 | Scatter Plots | Matplotlib | multiple scripts (v1) | Variants: color by intensity (Z-axis), source dataset, cluster assignment, role label |
| 5 | Role Distribution Bars | Matplotlib | `scripts/generate_v5_visualizations.py` (v1) | Human and AI role frequency bar charts |
| 6 | Feature Histograms | Matplotlib | `scripts/generate_v5_visualizations.py` (v1) | Evidence feature distributions per channel (Affect, Expressiveness, Divergence, Dynamics) |
| 7 | Pie Charts | Matplotlib | `scripts/generate_v5_visualizations.py` (v1) | Source breakdown (Arena, WildChat, OASST) |
| 8 | Pipeline Funnel | Matplotlib | `scripts/generate_v5_visualizations.py` (v1) | Horizontal bar chart showing pipeline stages: raw → validated → deduped → canonical |
| 9 | Variance Ellipses | Matplotlib patches | `scripts/visualize-dataset-comparison.py` (v1) | Mean position markers + standard deviation ellipses per dataset for cross-dataset comparison |
| 10 | Survival Rate Distribution | Matplotlib + KDE | `scripts/atlas/generate_visualizations.py` (v2) | Histogram + kernel density of constraint survival rates |
| 11 | Context Cliff | Matplotlib | `scripts/atlas/generate_visualizations.py` (v2) | Bar chart + cumulative line showing when violations occur (turn distribution) |
| 12 | Agency Tax Bars | Matplotlib | `scripts/atlas/generate_visualizations.py` (v2) | Dual bar charts: drift velocity and agency tax by stability class |
| 13 | Agency Tax Scatter | Matplotlib | `scripts/atlas/generate_visualizations.py` (v2) | Scatter plot: agency tax vs drift velocity, colored by stability class |
| 14 | Agency Tax Map | Matplotlib | `scripts/atlas/generate_visualizations.py` (v2) | Bubble scatter comparing task architectures (bubble size = N) |
| 15 | Drift Risk Heatmap | Seaborn | `scripts/atlas/generate_visualizations.py` (v2) | Architecture × constraint hardness heatmap (YlOrRd colormap) |
| 16 | Mode Violations | Matplotlib | `scripts/atlas/generate_visualizations.py` (v2) | Donut chart (violation type proportions) + stacked bar (by stability class) |
| 17 | Constraint Lifecycle | Matplotlib | `scripts/atlas/generate_visualizations.py` (v2) | Horizontal bar chart showing STATED → ACTIVE → VIOLATED/SURVIVED/ABANDONED flow |
| 18 | Radar Signatures | Matplotlib polar | `scripts/atlas/generate_visualizations.py` (v2) | Polar plot comparing architecture metrics (half-life, survival, repair rate, etc.) |
| 19 | Friction Heatmap | Seaborn | `scripts/atlas/generate_friction_heatmap.py` (v2) | Constraint outcome × mode violation type correlation matrix (row-normalized %) |
| 20 | Collapse Rate Bars | Matplotlib + Seaborn | `scripts/atlas/analysis/plot_results.py` (v2) | Archetype collapse rates with 95% CI error bars (Wald interval). Paper-quality (300 DPI) |
| 21 | Archetype Radar | Matplotlib polar | `scripts/atlas/analysis/plot_results.py` (v2) | Normalized feature signatures per archetype |
| 22 | Violin Plot | Seaborn | `scripts/analysis/scientific_analysis.py` (v2) | PAD volatility distribution: healthy vs collapsed conversations |
| 23 | Regression Plot | Matplotlib | `scripts/analysis/scientific_analysis.py` (v2) | Repair count vs PAD volatility with regression line |
| 24 | Box Plot | Seaborn | `scripts/analysis/scientific_analysis.py` (v2) | Mean emotional intensity comparison (healthy vs collapsed) |
| 25 | t-SNE Scatter | Matplotlib | `scripts/cluster-paths-proper.py` (v1) | 2D projection of high-dimensional feature space, colored by cluster assignment |

### 2.3 Interactive / Web Visualizations

| # | Type | Library | File | Description |
|---|------|---------|------|-------------|
| 26 | Force-Directed Role Network | D3.js | `src/components/visualizations/RoleNetworkGraph.tsx` (v1) | Nodes: human/AI roles (sized by count). Links: conversation flows (weighted). Forces: link, charge, center, collision, same-type repulsion, X-axis human/AI separation. Interactive: hover tooltips, drag, force parameter controls |
| 27 | Role Sankey Diagram | D3.js + d3-sankey | `src/components/visualizations/RoleSankeyDiagram.tsx` (v1) | Human Role → AI Role flows. Node width proportional to total connections, link width proportional to conversation count. Color-coded by source role. Also: Python version in `scripts/generate-sankey-roles.py` |
| 28 | PAD Timeline | React | `src/pages/PADTimelinePage.tsx` (v1) | Per-turn Pleasure/Arousal/Dominance trajectory over conversation length |
| 29 | Terrain Grid | React | `src/components/TerrainGrid.tsx` (v1) | 2D grid overlay with quadrant boundaries and axis labels (Functional↔Social, Structured↔Emergent) |
| 30 | Comparative Diagnostics | D3.js | `public/comparative_diagnostics.html` (v2) | Interactive scatter: X = repair count (structural), Y = PAD volatility (phenomenological). Per-conversation data export |
| 31 | Task Analytics Scatter | Recharts (React) | `frontend/src/pages/TaskAnalytics.tsx` (v2) | X: total turns, Y: violation count. Color-coded by stability class. Click-to-select with side panel detail |
| 32 | Task Analytics Sankey | Recharts (React) | `frontend/src/pages/TaskAnalytics.tsx` (v2) | Task stability flow: Total → Violations/Clean → Repaired/Abandoned → Drift/Collapse/Maintained |
| 33 | Annotation Tool | React | `frontend/src/pages/AnnotationTool.tsx` (v2) | Turn navigator (circular buttons), constraint tracker, trajectory metrics grid, archetype selection, ACI visualization |

### 2.4 Dashboards

| # | Name | Stack | File | Description |
|---|------|-------|------|-------------|
| 34 | Atlas Dashboard | D3.js / HTML | `public/atlas_suite/dashboard.html` (v2) | Corpus-level metrics overview |
| 35 | Atlas Explorer | D3.js / HTML | `public/atlas_suite/explorer.html` (v2) | Single conversation deep-dive with graph rendering |
| 36 | Atlas Compare | D3.js / HTML | `public/atlas_suite/compare.html` (v2) | Side-by-side conversation comparison |
| 37 | Atlas Global View | D3.js / HTML | `public/atlas_suite/global_view.html` (v2) | Corpus-wide distribution and pattern overview |
| 38 | Cartography Dashboard | HTML / JS | `public/cartography_dashboard.html` (v2) | Main research dashboard |
| 39 | Scientific Report | HTML | `public/scientific_report/index.html` (v2) | Statistical analysis report with embedded figures |
| 40 | Cluster Dashboard | React | `src/pages/ClusterDashboardPage.tsx` (v1) | Multi-panel cluster analysis with interactive filters |
| 41 | Role Dashboard | React | `src/pages/RoleDashboardPage.tsx` (v1) | Role distribution panels with statistical summaries |
| 42 | Insights Dashboard | React | `src/pages/InsightsDashboardPage.tsx` (v1) | Cross-cutting insights across roles, clusters, and trajectories |

---

## 3. Summary

**Classification & Analysis: 31 methods**
- 13 LLM-based (conversation classification, role assignment, move detection, feature extraction)
- 6 rule-based / regex (mode detection, constraint tracking, collapse detection, feature extraction)
- 7 ML / unsupervised (4 clustering algorithms, Random Forest importance, t-SNE reduction)
- 5 statistical tests (hypothesis testing, correlation, effect size, cluster validation)

**Visualization: 42 methods**
- 2 3D (Three.js terrain, Matplotlib scatter)
- 23 static Python charts (Matplotlib, Seaborn)
- 8 interactive web (D3.js, Recharts, React)
- 9 dashboards (D3.js/HTML, React)

**LLM Models Used:**
- GPT-4o-mini (primary, most classifiers)
- GPT-4o (Social Role Theory default)
- GPT-5.2 (Social Role Theory production run)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Qwen 2.5:7b (few-shot, reduced-roles via Ollama)
- Llama 2 (general Ollama classifier)

**Visualization Libraries:**
- Python: Matplotlib, Seaborn, SciPy (KDE)
- JavaScript: Three.js (WebGL 3D), D3.js (network/flow), Recharts (React charts)
- Framework: React + Vite + Tailwind

**Taxonomy Evolution:**
1. Early 6-role (v1.1): seeker, learner, director, collaborator, sharer, challenger
2. Reduced 3+3 (v1): information-seeker, social-expressor, co-constructor / facilitator, expert-system, relational-peer
3. Final 12-role (v1, Social Role Theory): 6 human + 6 AI roles with instrumental/expressive × authority dimensions
4. 13-move taxonomy (v2): constraint lifecycle + repair + task + interactional acts

---

## 4. What We Did: Established Research Questions

### RQ1 — Do Human-AI Roles Exist? (Established: Yes)

**Answer:** Yes — through social projection (CASA paradigm), but not like human roles. Linguistic fluency, responsiveness, and norm adherence trigger social heuristics that lead users to project expectations, competence, and intent onto the system.

**Methods used:**

| What | Methods (from §1–§2) | Key Finding |
|------|----------------------|-------------|
| Corpus construction | SHA-256 deduplication (#3 blocker fix), language detection, validation gates | N=507 canonical from 2,198 raw (WildChat, Chatbot Arena, OASST) |
| Role classification | #2 Social Role Theory Classifier (GPT-4o/5.2), 12-role taxonomy | 97.0% instrumental human roles; only 1.2% Learning-Facilitator AI roles |
| Leak-proof feature architecture | #18 Evidence Feature Extraction (30 features, R² < 0.01 with labels) | 4 channels: Affect (37.3%), Expressiveness (21.5%), Divergence (17.7%), Dynamics (15.4%), Structure (8.1%) |
| Cluster analysis | #20 K-Means, #21 Hierarchical, #22 DBSCAN, #25 Random Forest importance | 7 validated clusters; trajectory features most discriminative |
| Acceptance testing | #31 Silhouette/Davies-Bouldin/Calinski-Harabasz + Tests A/B/C | Evidence features: silhouette 0.10–0.11. Labels: 0.21–0.29. Evidence captures within-label variation, not better clustering |
| Spatial mapping | #19 Quadrant Classification, #1 Interactive Terrain (Three.js) | 84.4% in Functional-Aligned quadrant. Social-relational territory nearly empty |
| Role flow visualization | #26 Force-Directed Network, #27 Role Sankey Diagram | All 3 major human roles converge on Expert-System → "relational foreclosure" |

### RQ1a — How Do Human-AI Roles Compare to Human-Human? (Established)

**Answer:** Similar role schemas but with authority-agency mismatch and 2,030× trajectory variance within identical role labels.

**Methods used:**

| What | Methods (from §1–§2) | Key Finding |
|------|----------------------|-------------|
| Within-label variance analysis | #18 Evidence Features + automated exemplar selection (`scripts/select_exemplars.py`) | 2,030× variance ratio in IS→ES pairs (N=67, ≥6 messages). Same role label, wildly different emotional trajectories |
| Affect trajectory comparison | #8 PAD Scoring (per-message P/A/D), #18 affect_variance feature | Affective volatility (trajectory shape, not average) is the #1 discriminative signal |
| Cross-dataset comparison | #9 Variance Ellipses, #2 3D Scatter, #3 Density Heatmap | OASST (curated for quality) had narrowest relational range — "Curation Paradox" |
| Authority-agency analysis | #18 Dynamics channel (hedge_assert_ratio, repair_rate, goal_drift) | AI presents high authority (confident, fluent) but has zero agency (no accountability, no persistent state) |
| Sensitivity analysis | `sensitivity-analysis.json` (±20% threshold stability) | Role distributions stable under perturbation |

### RQ1b — How Do We Categorize and Describe These Roles? (In Progress)

**Answer:** 12-role taxonomy exists but needs refinement. Taxonomy evolved through 4 iterations; current version captures instrumental roles well but expressive quadrant remains underpopulated.

**Methods used so far:**

| What | Methods (from §1–§2) | Key Finding |
|------|----------------------|-------------|
| Taxonomy iteration | #1 8-Dimension Classifier → #3 Claude 6-role → #7 Reduced 3+3 → #2 Social Role Theory 12-role | Converged on 6 human + 6 AI roles grounded in Parsons/Bales/Eagly Social Role Theory |
| Role distribution analysis | #2 SRT Classifier production run (N=507) | Human: Provider 45.2%, Director 29.0%, IS 22.9%, Social-Expressor 3.0%. AI: Expert-System 64.1%, Advisor 19.7%, Co-Constructor 7.1% |
| Role pair analysis | `taxonomy_comprehensive.json` | Top pair: Provider→Expert-System (33.1%). The "funnel": all major human roles converge on Expert-System |
| Constraint/repair behaviour by role | #9 Move Classifier, #15 Constraint Tracker FSM | 71.5% constraint violation, mean 2.5-turn time-to-violation (median: 1), <1% repair success — the structural basis for why roles freeze |
| Agency Collapse detection | #16 Agency Collapse Detector, #13 LLM Feature Extraction | 50.3% collapse rate (N=398). 3 conditions: repair failure, tone degradation, specificity collapse |
| Implicit State Pathology theory | #14 Mode Detector, #15 Constraint Tracker, #17 Regex Features | Chat interfaces conflate coordination, memory, and execution into one channel. Statelessness creates information-theoretic repair trap |
| Formative evaluation | Context Inventory Interface (React + FastAPI) | N=20: control 4.2/5 vs baseline 2.8/5, repair count 1.2 vs 3.7 |

**What remains for RQ1b** (see §5 below): Role Inference Layer, Role Cards, authority-agency continuous tracking, re-clustering on expanded corpus with move/mode features.

---

## 5. Next Steps: Methods to Build

### RQ2a — Mental Health Pipeline Extensions

| # | Method | Type | What to Build |
|---|--------|------|---------------|
| 1 | Therapeutic Move Classifier | LLM + regex | 7 new move types: VALIDATE_EMOTION, REFLECT_BACK, REFRAME, NORMALIZE, SAFETY_PLAN, SELF_DISCLOSE, SEEK_VALIDATION. Add to `scripts/atlas/core/enums.py` + `move_classifier.py` |
| 2 | Therapeutic Mode Detector | Regex | 3 new modes: CONTAINING, GUIDING, WITNESSING. Add to `mode_detector.py` with signal patterns following LISTENER/ADVISOR/EXECUTOR structure |
| 3 | Therapeutic Violation Types | Rule-based | 3 new violations: PREMATURE_REFRAME, EMOTIONAL_BYPASS, BOUNDARY_VIOLATION. Extend violation classification matrix |
| 4 | Safety Detector | Regex + LLM | Crisis indicator detection (suicidal ideation, self-harm, acute distress). New `safety_detector.py` with SAFETY_ALERT graph node type + audit trail |
| 5 | Mental Health Metrics | Computed | 5 new metrics in `graph_metrics.py`: emotional attunement, therapeutic frame stability, dependency risk index, crisis escalation trajectory, repair-to-rupture ratio |

### RQ2b — Role Definition & Description

| # | Method | Type | What to Build |
|---|--------|------|---------------|
| 6 | Role Inference Layer | Pattern matching | New `role_inferrer.py` — RoleSignature dataclass mapping move/mode distributions to roles. Sits on top of existing pipeline output, not a new classifier |
| 7 | Role Inference API | FastAPI endpoint | `POST /api/context/role/infer` — takes move/mode history, returns current role assignment with confidence, transition count, role history |
| 8 | Role Card Generator | Script | Auto-generate structured Role Cards from pipeline output: feature signature (z-scores), prevalence, trajectory pattern, collapse risk, auto-selected exemplars |
| 9 | Authority-Agency Tracker | Computed | Continuous authority measure over time (not binary). Track attribution changes, compare profiles across role types |

### RQ2c — Visibility Intervention

| # | Method | Type | What to Build |
|---|--------|------|---------------|
| 10 | Incremental Pipeline | Python | New `incremental_runner.py` — per-turn processing (move classify → update FSM → mode detect → role infer) instead of batch. Maintains state between turns |
| 11 | WebSocket Role Stream | FastAPI + WS | `WS /api/context/role/stream` — pushes role state updates to frontend on each turn: current roles, trajectory, stability, suggestions, constraint status |
| 12 | Role Dashboard | React | Real-time role detection sidebar: current role pairing, live polar trajectory, stability indicator, "empty quadrant" invitations, role suggestions |
| 13 | Polar Trajectory (Live) | D3.js / React | Adapt BLOOM atlas_suite polar layout for streaming data. Inward spirals = collapse, outward spirals = healthy exploration |

### Cross-cutting — Human-Human Comparison

| # | Method | Type | What to Build |
|---|--------|------|---------------|
| 14 | Symmetric Move Classifier | Regex + LLM | Relabel actors to speaker_a/speaker_b. Add SELF_REPAIR move type with detection patterns ("I mean", "what I meant was", "let me rephrase") |
| 15 | Symmetric Mode Detector | Regex | Classify BOTH speakers per turn (currently only user→AI). Return two ModeAnnotations per turn pair |
| 16 | Corpus Adapters | Python | Format adapters for Switchboard, BNC, CALLHOME transcripts → same JSON structure as WildChat/Arena/OASST |

### P0 — Infrastructure (Before All Above)

| # | Method | Type | What to Build |
|---|--------|------|---------------|
| 17 | Test Suite | pytest | Unit tests for move classifier, mode detector, constraint FSM. Integration tests (input → graph → metrics). Golden-file regression. Port v1 acceptance tests A/B/C. Target: >80% coverage |
| 18 | Semantic Constraint Matching | sentence-transformers | Replace Jaccard (0.15) with cosine similarity (0.60 threshold) in `constraint_tracker.py`. Add embedding cache |
| 19 | Transformer Affect Scoring | HuggingFace | Replace heuristic PAD with model-based sentiment (candidate: `cardiffnlp/twitter-roberta-base-sentiment-latest`). Target: >500 unique values, model-based |
| 20 | Pipeline Error Fixes | Python | Fix ~250 INTRODUCES errors in constraint FSM, NoneType in move classification, schema validation failures. Add error categorization |

---

All file references verified 2026-02-13. v1 paths relative to `/Users/zac/Documents/Cartography/`. v2 paths relative to `/Users/zac/Documents/Documents-it/GitHub/Cartography_v2/`.
