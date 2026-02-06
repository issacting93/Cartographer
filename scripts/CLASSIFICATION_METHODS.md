# Dataset Classification Methods

Two approaches for classifying the N=562 conversation dataset for Agency Collapse analysis.

---

## Method 1: Heuristic Rules

**Script:** `scripts/classify_dataset.py`

### Approach
- Regex patterns for constraint detection
- Keyword matching for domain classification
- Rule-based archetype assignment
- No external API calls

### Strengths
- Fast (processes 562 files in seconds)
- Free (no API costs)
- Deterministic (same input → same output)

### Weaknesses
- High "Mixed/Other" rate (~93%)
- Cannot understand context
- Misses nuanced patterns

### Usage
```bash
python scripts/classify_dataset.py \
    --input /Users/zac/Downloads/Cartography/public/output \
    --output ./data/classified \
    --sample 562
```

### Output
- `classified_dataset.json` — Full coded data
- `paper_statistics.md` — Summary tables

---

## Method 2: LLM Classification

**Script:** `scripts/classify_llm.py`

### Approach
- GPT-4o-mini analyzes each conversation
- Structured prompt with archetype definitions
- Returns JSON with classification + reasoning
- Concurrent API calls (5 by default)

### Strengths
- Understands context and nuance
- Better archetype detection
- Provides reasoning for each classification
- Detects subtle patterns (tone shifts, implicit violations)

### Weaknesses
- Costs money (~$0.01/conversation → ~$6 for 562)
- Slower (rate limited)
- Non-deterministic (temperature > 0)

### Usage
```bash
export OPENAI_API_KEY=sk-...

python scripts/classify_llm.py \
    --input /Users/zac/Downloads/Cartography/public/output \
    --output ./data/classified \
    --sample 100 \
    --model gpt-4o-mini \
    --concurrent 5
```

### Output
- `llm_classified_dataset.json` — Full coded data with reasoning
- `llm_paper_statistics.md` — Summary tables

---

## Comparison

| Aspect | Method 1 (Heuristic) | Method 2 (LLM) |
|--------|---------------------|----------------|
| Speed | ~1 sec/100 files | ~30 sec/100 files |
| Cost | Free | ~$0.01/file |
| Accuracy | Low (93% Mixed) | Higher (TBD) |
| Reasoning | None | Yes |
| Reproducibility | 100% | ~90% |

---

## Recommended Workflow

1. **Run Method 1** on full dataset for baseline metrics
2. **Run Method 2** on stratified sample (100-200) for validation
3. **Compare** archetype distributions between methods
4. **Report** Method 2 results in paper, cite Method 1 as initial filter

---

## Archetype Definitions

| Archetype | Detection Pattern |
|-----------|------------------|
| **Provider Trap** | High initial specificity → passive acceptance |
| **Hallucination Loop** | 3+ failed repair attempts |
| **Identity Shift** | Tone degrades (polite → curt → frustrated) |
| **Canvas Hack** | Same constraint text copied 2+ times |
| **Passive Default** | No specific requirements stated throughout |
| **Mixed/Other** | No clear collapse pattern |
