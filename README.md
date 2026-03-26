# Cartographer

## What this project is about

When you tell a chatbot "answer in bullet points" or "don't use jargon" — does it actually listen?

We looked at 1,383 real conversations between people and AI chatbots to find out. The answer is mostly no.

**What we found:**

- People gave 559 explicit instructions across those conversations
- **69% were broken** by the AI
- Only **17% were clearly followed**
- The rest (14%) — we can't tell (the AI never acknowledged them, but didn't obviously break them either)
- **24% were broken on the very first reply** — the AI didn't even try
- **65% were broken within the first two exchanges**
- Only 6% of people even bothered trying to correct the AI
- When they did try, it worked **1% of the time**

We call this **Agency Collapse**: people give up trying to steer the conversation because the AI doesn't hold up its end.

## Why this happens

Chatbots rebuild their understanding of the conversation from scratch every time they reply. There's no persistent memory of "the user told me to use bullet points." The instruction is just buried somewhere in the chat history, and the model may or may not pick up on it.

The fix isn't better models — it's better interfaces. Instructions should be visible, trackable, and editable, not hidden in a scrolling chat log.

## How we measure this

We built a pipeline called **Atlas** that reads a conversation and turns it into a graph:

1. **Move classification** — Labels each message with what it's doing (proposing a rule, breaking a rule, trying to fix things, giving up, etc.)
2. **Constraint tracking** — Follows each instruction from when the user states it to when the AI breaks it (or doesn't)

The output is a structured graph per conversation with nodes for turns, moves, constraints, and violations.

## What's in this repo

```
scripts/
  atlas/                    # The pipeline (move classifier, constraint tracker, graph builder)
  analyze_instructions.py   # "Did the AI follow the instructions?" — plain-language analysis
  compute_verified_stats.py # Single source of truth for all statistics
  validate_report.py        # Checks that paper claims match computed data
  classify_roles_srt.py     # Role classification (human/AI roles per conversation)
  generate_v3_figures.py    # Paper figures (reads from verified_stats.json)
  download_*.py             # Download source datasets
  enrich_graphs.py          # Enrich conversation graphs with metadata

data/
  atlas_canonical/graphs/   # 1,383 conversation graphs (the main dataset)
  v2_unified/               # Processed conversations + evidence features
  v2_unified/reports/       # Computed statistics (verified_stats.json, instruction_analysis.json)
  mental_health/            # Mental health conversation extension (pilot, N=150)

paper/
  CUI_2026_Short_Paper.md   # Conference submission (short paper)
  CUI_2026_Paper.md         # Full paper draft
  FINDINGS_REPORT_v2.md     # Detailed findings

theory/
  implicit_state_pathology.md  # Core theory: why unstructured state architectures fail at grounding
  mode_taxonomy_v2.md          # Proposed taxonomy for interaction stances
  related_work.md              # Literature review

archive/                    # Old scripts, data, and documents no longer in active use
```

## Running it

```bash
# Compute all verified statistics
python scripts/compute_verified_stats.py

# Run the plain-language instruction analysis
python scripts/analyze_instructions.py

# Check that paper claims match the data
python scripts/validate_report.py

# Run the full pipeline on new conversations
cd scripts && PYTHONPATH="." python -m atlas.run_pipeline \
  --enriched ../data/atlas_canonical/all_task_enriched.json \
  --source-dir ../data/conversations_raw \
  --output-dir ../data/atlas_canonical/graphs
```

## Data sources

Conversations come from three public datasets:
- **Chatbot Arena** — People comparing AI models side-by-side
- **WildChat** — Real conversations people had with ChatGPT
- **OpenAssistant** — Community-contributed conversations

## Known limitations

- Constraints are extracted by an LLM (GPT-4o-mini) with no human validation
- Matching violations to constraints uses word overlap (Jaccard, threshold 0.15) — about half of extracted constraints are lost in this step
- Mode detection (Listener/Advisor/Executor) is broken — it classifies AI responses by text length, not intent. We don't use it in our claims.

## Status

Active research. CUI 2026 short paper submitted. Statistics pass 60/60 validation checks.
