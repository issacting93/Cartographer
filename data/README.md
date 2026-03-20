# Data Directory

All verified research data consolidated from Cartography v1 and v2.

## Directory Structure

### Raw Source Data
- `conversations_raw/` — 2,198 raw conversation JSON files from WildChat, Chatbot Arena, OASST

### v1 Canonical Corpus (N=507, Role Analysis)
- `v1_canonical/conversations/` — 507 canonical conversations with 8-dimension classification + 12-role taxonomy labels
- `v1_canonical/evidence_features.csv` — 30 leak-proof evidence features (R² < 0.01 with labels), 507 rows × 41 columns
- `v1_canonical/affect_proxy/` — 507 per-conversation affect scores (valence, activation, dominance, intensity)
- `v1_canonical/manifests/` — Corpus pipeline manifests:
  - `corpus_stats.json` — Role distributions (97.0% instrumental), source breakdown, message stats
  - `dedupe_manifest.json` — SHA-256 deduplication log (98 duplicates removed)
  - `validated_manifest.json` — Validation gate results
  - `excluded_manifest.json` — Excluded conversations with reasons
  - `non_english_manifest.json` — Language detection results (20 non-English removed)
- `v1_canonical/reports/` — Analysis outputs:
  - `taxonomy_comprehensive.json` — Full 12-role taxonomy with pair distributions
  - `sensitivity-analysis.json` — ±20% threshold stability tests
  - `cluster-separation-metrics.json` — Silhouette scores, cluster validation
  - `validation-report.json` — Feature validation results
  - `path-clusters-hierarchical.json` — 7-cluster trajectory analysis
  - `comprehensive-analysis-538.json` — Full corpus analysis
- `v1_canonical/COMPREHENSIVE_FINDINGS_REPORT.md` — v5.0 definitive findings (853 lines)

### v2 Atlas Canonical (N=745, Constraint/Repair Analysis)
- `atlas_canonical/graphs/` — 745 NetworkX MultiDiGraph JSON files with node types:
  - Conversation, Turn, Constraint (376 total), Move (13 types), ViolationEvent, InteractionMode
- `atlas_canonical/metrics/aggregate.json` — Summary statistics (half-life, repair rate, survival rate)
- `atlas_canonical/metrics/all_metrics.json` — Per-conversation metrics (744 entries)

### v2 Feature Extraction
- `features_llm_collapse.json` — LLM-enhanced features + collapse detection (N=398, 50.3% collapse)
- `features_with_collapse.json` — Regex-based features + collapse detection (N=148)
- `features_llm.json` — LLM features without collapse
- `features_llm_full.json` — Full LLM feature set
- `features_llm_all.json` — All conversations LLM features
- `features_llm_all_collapse.json` — All conversations with collapse
- `features.json` — Base regex features

### v2 Pipeline Intermediate Data
- `task_classified/` — Task classification outputs (Generation, Analysis, etc.)
- `atlas_with_pad/` — ~990 conversations with PAD (Pleasure-Arousal-Dominance) annotations
- `atlas/` — Sample graphs and pipeline cache
- `atlas_test/` — Pipeline test fixtures
- `atlas_v2_production/` — Production pipeline outputs
- `classified/` — Dataset classification outputs
- `analysis/`, `analysis_all/` — Cluster analysis results
- `clustered/`, `clustered_llm/`, `clustered_llm_all/` — Clustering outputs

## Verified Statistics (from `scripts/verify_statistics.py`)

| Statistic | Value | Source | N |
|-----------|-------|--------|---|
| Constraint violation rate | 71.5% | atlas_canonical/graphs (constraint nodes) | 376 constraints |
| Mean time-to-violation | 2.5 turns | verified_stats.json (compute_constraint_stats) | 376 constraints |
| Median time-to-violation | 1 turn | verified_stats.json (compute_constraint_stats) | 376 constraints |
| Turn 0 violation rate | 24.5% | verified_stats.json | 66/269 violations |
| Repair success rate | 0.74% | verified_stats.json (event-level: 2/271) | 271 violation events |
| Agency Collapse rate | 50.3% | verified_stats.json (from features_llm_collapse.json) | 398 conversations |
| Instrumental human roles | 97.0% | verified_stats.json | 2,576 conversations |
| Variance ratio (IS→ES) | 2,817× | verified_stats.json | 1,039 IS→ES pairs (≥6 msgs) |

## What We Did: Established Research Questions

### RQ1 — Do Human-AI Roles Exist? (Established: Yes)
- **Data used:** `v1_canonical/` (N=507 canonical conversations, 30 evidence features, 507 affect scores)
- **Key outputs:** `v1_canonical/manifests/corpus_stats.json` (97.0% instrumental), `v1_canonical/reports/taxonomy_comprehensive.json` (12-role taxonomy with pair distributions), `v1_canonical/evidence_features.csv` (30 leak-proof features, R² < 0.01)
- **Finding:** Roles exist through social projection (CASA paradigm). 84.4% of conversations cluster in Functional-Aligned quadrant. Social-relational territory nearly empty.

### RQ1a — How Do Human-AI Roles Compare to Human-Human? (Established)
- **Data used:** `v1_canonical/evidence_features.csv` + `v1_canonical/conversations/` (IS→ES pairs, N=67 with ≥6 messages)
- **Key outputs:** `v1_canonical/reports/sensitivity-analysis.json`, `v1_canonical/reports/cluster-separation-metrics.json`, `v1_canonical/reports/comprehensive-analysis-538.json`
- **Finding:** 2,030× variance ratio within identical role labels. Same destination, different journeys. Affective volatility (trajectory shape) is the #1 discriminative signal.

### RQ1b — How Do We Categorize and Describe These Roles? (In Progress)
- **Data used:** `v1_canonical/` (role taxonomy) + `atlas_canonical/` (constraint/repair behaviour) + `features_llm_collapse.json` (collapse detection)
- **Key outputs:** `verified_stats.json` (mean 2.5 turns to violation, repair <1%), `features_llm_collapse.json` (50.3% Agency Collapse)
- **Finding:** 12-role taxonomy established but expressive quadrant underpopulated. Constraint violation (71.5%) and Agency Collapse (50.3%) explain why roles freeze. Implicit State Pathology theory developed.

## Next Steps: Data Requirements

### RQ2a — Mental Health Data Integration
- **New corpus needed:** Therapeutic/emotional support conversations (DAIC-WOZ, ESConv, mental health chatbot logs, Reddit support communities)
- **Ethics gate:** IRB approval, PII anonymization pipeline, data retention policy, content warning system
- **Pipeline output:** New graphs with therapeutic move types (VALIDATE_EMOTION, REFLECT_BACK, REFRAME, etc.) and emotional boundary constraints
- **New metrics:** Emotional attunement, therapeutic frame stability, dependency risk index, crisis escalation trajectory
- **Target location:** `data/mental_health_canonical/`

### RQ2b — Role Definition & Description
- **Role Inference Layer output:** Role assignments derived from move/mode distributions (not LLM labels) — stored as Role nodes in graphs
- **Role Cards:** Auto-generated structured descriptions per discovered role (feature signature, prevalence, trajectory pattern, collapse risk, exemplars)
- **Re-clustering required:** Run HDBSCAN on expanded corpus (original + mental health) with move/mode features, not role labels
- **Target location:** `data/role_cards/`, Role nodes added to existing graph schema

### RQ2c — Visibility Intervention Study
- **Study data:** Between-subjects 2×2 (role visibility ON/OFF × general/mental health), N=320 target
- **Real-time pipeline output:** Per-turn role state, trajectory coordinates, stability scores — streamed via WebSocket
- **Dependent variables:** Role diversity, expressive activation, collapse rate, repair behaviour, satisfaction, meta-awareness
- **Target location:** `data/visibility_study/`

### Cross-cutting — Human-Human Comparison
- **New corpus needed:** Human-human conversation data (Switchboard, BNC, CALLHOME, therapy transcripts)
- **Symmetric pipeline:** Both speakers can propose/violate/repair constraints; SELF_REPAIR move type added
- **Expected comparisons:** Instrumental % (~60-70% H-H vs 98.8% H-AI), repair success (~70-80% vs 0.1%), self-repair (~80% vs ~0%)
- **Target location:** `data/human_human_canonical/`

### P0 — Infrastructure (Before Any New Data)
- Build test suite (unit + integration + acceptance tests A/B/C)
- Fix pipeline errors (~250 INTRODUCES errors, NoneType failures, schema validation)
- Replace Jaccard constraint matching (0.15 threshold) with semantic embedding similarity
- Upgrade affect measurement to transformer-based (target: model-based, >500 unique values)

## Regenerating Data

```bash
# Run full v2 pipeline
python -m atlas.run_pipeline \
    --enriched data/task_classified/all_task_enriched.json \
    --source-dir data/conversations_raw \
    --output-dir data/atlas

# Verify all statistics
python3 scripts/verify_statistics.py
```
