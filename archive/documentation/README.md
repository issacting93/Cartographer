# Cartographer Documentation

**Complete documentation for the Cartographer research framework.**

---

## 📖 Documentation Index

### Getting Started

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Quick start guide (5-minute setup) | 10 min | New users |
| **[INSTALLATION.md](INSTALLATION.md)** | Detailed installation for all components | 30 min | Developers |
| **[DATA_GUIDE.md](DATA_GUIDE.md)** | Data directory structure and provenance | 20 min | Researchers |

### Technical Reference

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| **[DOCUMENTATION.md](DOCUMENTATION.md)** | Complete technical reference (pipeline, metrics, APIs) | 1-2 hrs | Developers, Researchers |

### Coming Soon

| Document | Purpose | Status |
|----------|---------|--------|
| **API_REFERENCE.md** | REST API documentation for Context Engine | 🚧 Planned |
| **DEVELOPMENT.md** | Contributor guide | 🚧 Planned |
| **TESTING.md** | Testing strategy and how to run tests | 🚧 Planned |
| **TROUBLESHOOTING.md** | Common issues and solutions | 🚧 Planned |
| **METRICS_EXPLAINED.md** | Deep dive on the 8 CUI metrics | 🚧 Planned |
| **DEPLOYMENT.md** | Production deployment guide | 🚧 Planned |
| **CHANGELOG.md** | Version history | 🚧 Planned |

---

## 🧠 Theoretical Foundations

For the complete theoretical framework underlying this research:

**→ [Theory Directory](../theory/)** — Core theories and related work
- **[Implicit State Pathology](../theory/implicit_state_pathology.md)** — Foundational theory of Agency Collapse
- **[Related Work](../theory/related_work.md)** — Literature review and citations

---

## 🚀 Quick Links

**I want to...**

- **Set up the project** → [INSTALLATION.md](INSTALLATION.md)
- **Run my first analysis** → [GETTING_STARTED.md](GETTING_STARTED.md)
- **Understand the data** → [DATA_GUIDE.md](DATA_GUIDE.md)
- **Learn about metrics** → [DOCUMENTATION.md](DOCUMENTATION.md#5-metrics-reference)
- **Understand the pipeline** → [DOCUMENTATION.md](DOCUMENTATION.md#2-pipeline-deep-dive)
- **Use the API** → API_REFERENCE.md *(coming soon)*
- **Contribute code** → DEVELOPMENT.md *(coming soon)*

---

## 📚 Learning Path

### For New Users

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** — 10 minutes
   - Install dependencies
   - Run "Hello World" pipeline
   - Explore results

2. **[DATA_GUIDE.md](DATA_GUIDE.md)** — 20 minutes
   - Understand data structure
   - Learn about source datasets
   - Reproduce canonical results

3. **[DOCUMENTATION.md](DOCUMENTATION.md)** — 1 hour
   - Section 1-2: Overview & Pipeline
   - Section 5: Metrics Reference
   - Section 9: Running the System

### For Researchers

1. **[DATA_GUIDE.md](DATA_GUIDE.md)** — Focus on:
   - Data Provenance
   - Reproduction Guide
   - Data Validation

2. **[DOCUMENTATION.md](DOCUMENTATION.md)** — Focus on:
   - Section 5: Metrics Reference
   - Section 6: Analysis Tools
   - Section 10: Academic Context

3. **[Theory Papers](../theory/)** — Read:
   - `related_work.md`
   - `../CUI-Docs/AGENCY_COLLAPSE_FINAL_REPORT.md`

### For Developers

1. **[INSTALLATION.md](INSTALLATION.md)** — Complete setup

2. **[DOCUMENTATION.md](DOCUMENTATION.md)** — Focus on:
   - Section 2: Pipeline Deep-Dive
   - Section 3: Data Models & Enums
   - Section 4: Graph Schema
   - Section 7: Data Formats

3. **DEVELOPMENT.md** *(coming soon)* — Contributing guide

---

## 🔍 Documentation by Topic

### Installation & Setup
- **Quick Setup:** [GETTING_STARTED.md](GETTING_STARTED.md)
- **Detailed Installation:** [INSTALLATION.md](INSTALLATION.md)
- **Environment Variables:** [INSTALLATION.md - Environment Configuration](INSTALLATION.md#environment-configuration)
- **Docker Setup:** [INSTALLATION.md - Docker Setup](INSTALLATION.md#docker-setup-optional)

### Data & Provenance
- **Data Structure:** [DATA_GUIDE.md - Directory Structure](DATA_GUIDE.md#directory-structure)
- **Source Datasets:** [DATA_GUIDE.md - Data Provenance](DATA_GUIDE.md#data-provenance)
- **Reproduction:** [DATA_GUIDE.md - Reproduction Guide](DATA_GUIDE.md#reproduction-guide)
- **Adding Data:** [DATA_GUIDE.md - Adding New Data](DATA_GUIDE.md#adding-new-data)

### Pipeline & Processing
- **Pipeline Overview:** [DOCUMENTATION.md - Section 2](DOCUMENTATION.md#2-pipeline-deep-dive)
- **Move Classification:** [DOCUMENTATION.md - Section 2.2](DOCUMENTATION.md#22-move_classifierpy--13-move-taxonomy)
- **Constraint Tracking:** [DOCUMENTATION.md - Section 2.4](DOCUMENTATION.md#24-constraint_trackerpy--constraint-state-machine)
- **Graph Construction:** [DOCUMENTATION.md - Section 2.5](DOCUMENTATION.md#25-build_atlas_graphpy--graph-construction)

### Metrics & Analysis
- **8 CUI Metrics:** [DOCUMENTATION.md - Section 5](DOCUMENTATION.md#5-metrics-reference)
- **PAD Scoring:** [DOCUMENTATION.md - Section 6.1](DOCUMENTATION.md#61-pad-scoring)
- **Statistical Analysis:** [DOCUMENTATION.md - Section 6.3](DOCUMENTATION.md#63-scientific-analysis)
- **Sensitivity Analysis:** [DOCUMENTATION.md - Section 6.4](DOCUMENTATION.md#64-sensitivity-analysis)

### Frontend & Evaluation
- **Running the Frontend:** [INSTALLATION.md - Frontend Setup](INSTALLATION.md#frontend-setup)
- **User Study Setup:** [GETTING_STARTED.md - Run User Study](GETTING_STARTED.md#3-run-user-study)
- **Context Engine:** API_REFERENCE.md *(coming soon)*

### Troubleshooting
- **Installation Issues:** [INSTALLATION.md - Troubleshooting](INSTALLATION.md#troubleshooting)
- **Common Errors:** [GETTING_STARTED.md - Troubleshooting](GETTING_STARTED.md#troubleshooting)
- **Full Guide:** TROUBLESHOOTING.md *(coming soon)*

---

## 📊 Project Components

### Backend (`scripts/atlas/`)
**Documentation:** [DOCUMENTATION.md - Section 2](DOCUMENTATION.md#2-pipeline-deep-dive)

The graph-structural pipeline for analyzing conversations:
- **Move Classification** — 13 conversational acts
- **Mode Detection** — 3 interaction modes (Listener, Advisor, Executor)
- **Constraint Tracking** — State machine (Stated → Active → Violated → Repaired)
- **Graph Construction** — NetworkX MultiDiGraph
- **Metrics Computation** — 8 CUI metrics

### Context Engine (`context_engine/`)
**Documentation:** API_REFERENCE.md *(coming soon)*

Backend API for task-first interaction:
- **Task Management** — Create, list, switch tasks
- **Constraint Operations** — Pin text as constraints
- **Context Queries** — Scoped context composition

### Frontend (`frontend/`)
**Documentation:** [GETTING_STARTED.md](GETTING_STARTED.md)

React evaluation prototype:
- **Baseline Chat** — Chat-only interface
- **Treatment Chat** — Chat + Context Inventory
- **Scripted Scenario** — Career coaching with forced violation

### Data (`data/`)
**Documentation:** [DATA_GUIDE.md](DATA_GUIDE.md)

Datasets and pipeline outputs:
- **Raw conversations** — WildChat, OASST, Arena
- **Classified data** — LLM-enriched metadata
- **Graphs** — 744 conversation graphs
- **Metrics** — 8 CUI metrics per conversation

---

## 🎓 Research Context

### Papers & Reports

| Document | Location | Description |
|----------|----------|-------------|
| **Agency Collapse Report** | `../CUI-Docs/AGENCY_COLLAPSE_FINAL_REPORT.md` | N=863 study, 50.3% collapse rate |
| **Context Engine Plan** | `../CUI-Docs/Context_Engine_Implementation_Plan.md` | Evaluation prototype design (N=80) |
| **Methods Section** | `../CUI-Docs/METHODS_SECTION.md` | Classification methodology |
| **Related Work** | `../theory/related_work.md` | Literature review |

### Key Findings

- **50.3% Agency Collapse Rate** — Half of conversations fail structurally
- **Repair Loop as Structural Trap** — Cluster 0 has 89.1% collapse
- **Mean Time-to-Violation: 2.5 turns** (median: 1 turn) — Constraints degrade rapidly
- **71.5% Constraint Failure** — Most constraints are violated

---

## 🛠️ Contributing

See DEVELOPMENT.md *(coming soon)* for:
- Code structure
- Adding new features
- Testing guidelines
- Git workflow

---

## 📝 License

See `../LICENSE` for project license.

Source datasets have separate licenses:
- **WildChat:** CC-BY-SA 4.0
- **OASST:** Apache 2.0
- **Chatbot Arena:** MIT

---

## 📧 Contact

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Research Questions:** See research papers in `../theory/`

---

**Ready to start?** → [GETTING_STARTED.md](GETTING_STARTED.md)
