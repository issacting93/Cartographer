# Inter-Rater Reliability Study Plan

**Purpose:** Establish publishable inter-rater reliability for the Atlas pipeline's three core annotation tasks before CUI 2026 submission.

---

## 1. Sample

**N = 100 conversations**, stratified by source and role to ensure representation of all 6 human roles (minimum 5 per role):

| Source | Corpus N | Corpus % |
|--------|----------|----------|
| Chatbot Arena | 1,739 | 67.5% |
| WildChat | 786 | 30.5% |
| OASST | 50 | 1.9% |

Selection: Stratified random sampling via `scripts/irr_sample.py` (seed=42). Sample generated and exported to:
- `data/v2_unified/reports/irr_sample.json` (metadata)
- `data/v2_unified/reports/irr_coding_sheet.csv` (blank coding sheet for raters)

**Sample role distribution** (N=100): Information Seeker 58, Director 19, Collaborator 6, Relational Peer 6, Provider 6, Social Expressor 5.

---

## 2. Annotation Tasks

### Task A: Move Classification (per turn)

Each turn is annotated with zero or more communicative moves from the Atlas move taxonomy:

- `PROPOSE_CONSTRAINT`, `ACCEPT_CONSTRAINT`, `VIOLATE_CONSTRAINT`, `RATIFY_CONSTRAINT`
- `REPAIR_INITIATE`, `REPAIR_EXECUTE`, `ABANDON_CONSTRAINT`
- `STATE_GOAL`, `TASK_SHIFT`, `GENERATE_OUTPUT`
- `REQUEST_CLARIFICATION`, `PROVIDE_INFORMATION`, `PASSIVE_ACCEPT`

**Unit of analysis:** One turn = one annotation unit. Multi-move turns produce a set of labels.

**Agreement metric:** Cohen's kappa (per move type, binary present/absent).

### Task B: Constraint Violation (per turn, yes/no)

For each assistant turn where the pipeline detected `VIOLATE_CONSTRAINT`:
- **Yes:** The assistant's output violates an active user constraint.
- **No:** False positive (the output is consistent with constraints).

**Unit of analysis:** One assistant turn flagged by the pipeline.

**Agreement metric:** Cohen's kappa (binary).

### Task C: Mode Classification (per turn pair)

For each user-assistant turn pair:
1. Classify the **user-requested mode**: Listener, Advisor, Executor, Ambiguous.
2. Classify the **AI-enacted mode**: Listener, Advisor, Executor, Ambiguous.
3. Determine whether a **mode violation** occurred (mismatch = yes).

**Unit of analysis:** One user-assistant turn pair.

**Agreement metric:** Cohen's kappa (4-class for mode, binary for violation).

---

## 3. Reliability Targets

| Task | Metric | Target | Minimum Acceptable |
|------|--------|--------|--------------------|
| A: Move classification | Cohen's kappa (per type) | >= 0.75 | >= 0.70 |
| B: Constraint violation | Cohen's kappa | >= 0.80 | >= 0.70 |
| C: Mode classification | Cohen's kappa (mode) | >= 0.75 | >= 0.70 |
| C: Mode violation | Cohen's kappa (binary) | >= 0.80 | >= 0.70 |

Kappa interpretation (Landis & Koch, 1977): 0.61-0.80 = substantial, 0.81-1.00 = almost perfect.

---

## 4. Annotators

- **2 independent annotators**, both with background in HCI or computational linguistics.
- Neither annotator has access to the pipeline's automated classifications during annotation.
- Disagreements resolved by discussion after independent coding (not adjudicated by a third rater).

---

## 5. Procedure

### Phase 1: Training (Week 1)

1. Develop codebook with definitions, decision rules, and worked examples for each task.
2. Both annotators independently code **10 practice conversations** (not from the 50-conversation sample).
3. Meet to discuss disagreements, refine codebook.
4. Repeat with **5 additional practice conversations** until kappa >= 0.70 on practice set.

### Phase 2: Independent Annotation (Weeks 2-3)

1. Each annotator independently codes all 100 conversations for all 3 tasks.
2. No communication between annotators during this phase.
3. Annotations recorded in a shared spreadsheet with standardized column structure.

### Phase 3: Analysis (Week 4)

1. Compute Cohen's kappa for each task.
2. Identify systematic disagreement patterns (confusion matrices).
3. If kappa < 0.70 for any task, conduct reconciliation session and re-annotate problematic categories.
4. Report final kappa values with 95% confidence intervals.

---

## 6. Timeline

| Week | Activity |
|------|----------|
| 1 | Codebook development + training phase (15 practice conversations) |
| 2 | Independent annotation (50 conversations each) |
| 3 | Independent annotation (50 conversations each) |
| 4 | Agreement analysis, reconciliation if needed, write-up |

**Total duration:** ~3-4 weeks.

---

## 7. Outputs

- `data/v2_unified/reports/irr_annotations_rater1.json`
- `data/v2_unified/reports/irr_annotations_rater2.json`
- `data/v2_unified/reports/irr_agreement_report.json` (kappa values, confusion matrices)
- Updated `paper/CUI_2026_Paper.md` Section 3 (Methodology) with IRR results
