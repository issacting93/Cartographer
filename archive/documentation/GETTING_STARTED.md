# Getting Started with Cartographer

**Quick start guide to get up and running in 10 minutes.**

---

## What is Cartographer?

Cartographer is a research framework that diagnoses governance failure in human-AI dialogue by modeling conversations as directed graphs. It quantifies how well AI systems respect user-defined constraints.

**Key capabilities:**
- 📊 **8 CUI Metrics** — Drift Velocity, Agency Tax, Constraint Half-Life, etc.
- 🔄 **13-Move Taxonomy** — Classify conversational acts (propose, violate, repair)
- 🎯 **Context Engine** — Task-first interaction model with persistent constraints
- 📈 **Evaluation Suite** — Between-subjects user studies (N=80)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Pipeline execution |
| Node.js | 18+ | Frontend development |
| OpenAI API Key | — | LLM classification (optional) |
| Git | — | Version control |

---

## 5-Minute Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Cartography_v2.git
cd Cartography_v2
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 4. Run "Hello World" Pipeline

```bash
# Process a single conversation
python -m scripts.atlas.run_pipeline \
  --enriched data/task_classified/sample_conversation.json \
  --output-dir data/test_output \
  --model gpt-4o-mini \
  --limit 1
```

**Expected output:**
```
Processing 1 conversations...
✓ Conversation abc123: 12 turns, 3 constraints
  - Drift Velocity: 0.42
  - Agency Tax: 1.75
  - Constraint Half-Life: 2.5 turns
Saved to data/test_output/graphs/abc123.json
```

### 5. View the Graph (Optional)

```bash
# Open the interactive explorer
python -m http.server 8000
# Visit: http://localhost:8000/scripts/atlas/explorer.html
```

---

## What's Next?

### Run the Full Pipeline

Process all 744 conversations:

```bash
python -m scripts.atlas.run_pipeline \
  --enriched data/task_classified/all_task_enriched.json \
  --output-dir data/atlas_canonical \
  --model gpt-4o-mini \
  --workers 5
```

**Time estimate:** ~2-3 hours (with LLM calls)

### Start the Context Engine API

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

### Explore the Data

```bash
# View aggregate metrics
cat data/atlas_canonical/metrics/aggregate.json

# View metrics report
cat data/atlas_canonical/metrics/metrics_report.md

# Open explorer
open scripts/atlas/explorer.html
```

---

## Common First Tasks

### 1. Classify Your Own Conversation

```bash
# Add your conversation to data/raw/my_conversation.json
# Format: {"messages": [{"role": "user", "content": "..."}, ...]}

# Classify it
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/ \
  --output data/my_enriched.json \
  --model gpt-4o-mini

# Run pipeline
python -m scripts.atlas.run_pipeline \
  --enriched data/my_enriched.json \
  --output-dir data/my_output
```

### 2. Add a New Metric

1. Edit `scripts/atlas/graph_metrics.py`
2. Add function: `def compute_my_metric(G: nx.MultiDiGraph) -> float:`
3. Update `compute_conversation_metrics()` to include it
4. Rerun pipeline

See: [DEVELOPMENT.md](DEVELOPMENT.md) for details

### 3. Run User Study

```bash
cd frontend
npm run dev

# Visit http://localhost:5173
# Navigate to /baseline or /treatment
```

---

## Project Structure

```
Cartography_v2/
├── scripts/atlas/           # 🔄 Pipeline (move classification, metrics)
├── context_engine/          # 🎯 Backend API (task management)
├── frontend/                # 📊 React UI (evaluation prototype)
├── data/                    # 📁 Datasets and outputs
│   ├── raw/                 # Source conversations
│   ├── task_classified/     # LLM-enriched data
│   └── atlas_canonical/     # Pipeline outputs
├── documentation/           # 📚 This file + technical docs
├── theory/                  # 📖 Research papers and notes
└── CUI-Docs/                # 📝 Process documentation
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"

```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### "FileNotFoundError: all_task_enriched.json"

```bash
# Generate classification first
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/ \
  --output data/task_classified/all_task_enriched.json
```

### "OpenAI API Error: 429 Rate Limit"

```bash
# Reduce concurrency
python -m scripts.atlas.run_pipeline \
  --workers 1 \
  --delay 2  # 2 seconds between requests
```

### Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Learning Path

| Step | Resource | Time |
|------|----------|------|
| 1 | This guide | 10 min |
| 2 | [INSTALLATION.md](INSTALLATION.md) | 15 min |
| 3 | [DOCUMENTATION.md](DOCUMENTATION.md) — Section 2 (Pipeline) | 30 min |
| 4 | [DATA_GUIDE.md](DATA_GUIDE.md) | 15 min |
| 5 | Run full pipeline | 2 hrs |
| 6 | [DOCUMENTATION.md](DOCUMENTATION.md) — Full read | 1 hr |

---

## Getting Help

- **Technical docs:** [DOCUMENTATION.md](DOCUMENTATION.md)
- **API reference:** [API_REFERENCE.md](API_REFERENCE.md) *(coming soon)*
- **Issues:** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) *(coming soon)*
- **Research context:** See `theory/` and `CUI-Docs/`

---

## Key Concepts (2-Minute Primer)

### What is a "Constraint"?

User-defined requirement, e.g., "use only Python standard library", "keep it under 100 lines"

### What is "Agency Collapse"?

When users progressively surrender control because maintaining constraints becomes too costly. Measured by repair loops.

### What is "Drift Velocity"?

Violations per turn. Higher = AI ignores constraints faster.

### What is "Agency Tax"?

Repair effort per violation. Higher = users work harder to keep AI on track.

### What are the 13 Moves?

Conversational acts like `PROPOSE_CONSTRAINT`, `VIOLATE_CONSTRAINT`, `REPAIR_INITIATE`. See [Section 2.2](DOCUMENTATION.md#22-move_classifierpy--13-move-taxonomy).

---

**Ready to dive deeper?** Continue to [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.
