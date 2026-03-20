 When you talk to ChatGPT, Claude, or any AI — what's actually happening between you? Not technically, but relationally. Are you a customer? A     
  collaborator? A boss giving orders? A student? And what is the AI to you — a tool, an advisor, a companion, a servant?                            

  Nobody had mapped this systematically.

  ---
  Phase 1: Do Roles Even Exist? (v1, N=562)

  What we did: Took 562 conversations from three public datasets (WildChat, Chatbot Arena, OASST) and classified them using a 12-role taxonomy
  grounded in Social Role Theory (Parsons, Bales, Eagly). Built a 3D terrain visualization — X-axis for functional↔social orientation, Y-axis for
  aligned↔divergent structure, Z-axis for emotional intensity.

  What we found:
  - Yes, roles exist. Users unconsciously assign social roles to AI (CASA paradigm — Computers Are Social Actors). Not because AI is sentient, but
  because linguistic fluency triggers social heuristics.
  - 98.8% of human roles are purely instrumental. Provider, Director, Information-Seeker. Only 1.2% were expressive (Social-Expressor). The entire
  social-relational quadrant of the map was empty.
  - "Same destination, different journeys." This was the breakthrough finding. Conversations with identical role labels (e.g., Information-Seeker →
  Expert-System) showed 2,030x variance in their emotional trajectories. Two people asking the same type of question had wildly different experiences.
   Role labels describe where conversations end up, but completely miss how they get there.
  - The map was mostly empty. 84.4% of conversations clustered in one quadrant (Functional-Aligned). Co-construction, facilitation, play, creative
  exploration — all nearly absent. Not because they're impossible, but because they're foreclosed by design.

  What went wrong (the audits):
  - We built the terrain using role-derived spatial features, then claimed those spatial features were more important than roles. That's circular
  (R²=1.0 — the features perfectly encoded what they were derived from).
  - The emotional intensity measurement only had 53 unique values for 507 conversations. Too coarse to detect real differences.
  - 98 duplicate conversations inflated the corpus.
  - Hand-transcribed statistics had 15-22% error rates.
  - The flagship example conversation was misclassified.
  - No unit tests existed anywhere.

  How we fixed it (v5.0):
  - Strict separation: 30 "evidence features" (text-derived, R² < 0.01 with labels) for all claims, 2 "viz-only features" (role-derived) for terrain
  positioning only.
  - Improved affect proxy: 503 unique values (up from 53).
  - SHA-256 deduplication: canonical corpus of 507 (down from 625).
  - Automated exemplar selection — no more manual picking.
  - Formal acceptance tests (A/B/C) that must pass before any quantitative claim.
  - Honest framing: labels actually cluster better than evidence features (silhouette 0.21-0.29 vs 0.10-0.11). Evidence features capture what labels
  compress — they don't replace them.

  ---
  Phase 2: Why Do Conversations Break Down? (v2, N=863)

  What we did: Shifted focus from mapping roles to understanding failure. Developed a theory called Implicit State Pathology and tested it on 863
  conversations.

  The theory: Chat interfaces conflate three functions into one channel — coordination ("what are we doing?"), memory ("what did we agree?"), and
  execution ("do the thing"). Because LLMs are stateless, they re-infer everything from the chat history every turn. Each repair attempt adds tokens,
  which dilutes the original signal, which increases violation probability, which requires more repair. It's an information-theoretic trap.

  What we found:
  - 50.3% of sustained conversations end in Agency Collapse — the user loses the ability to steer the interaction.
  - Mean time-to-violation: 2.5 turns (median: 1 turn). 24.5% of constraints fail at turn 0. This is an early-turn problem, not a context window problem.
  - 71.5% of user constraints are violated without acknowledgment.
  - Repair succeeds less than 1% of the time (0.74% event-level). The medium structurally resists correction.
  - The Repair Loop is a trap. Once a user enters 5+ repair attempts, there's an 89.1% collapse rate with less than 11% escape probability.
  Conversations that enter this regime show inward-spiraling topological patterns (tightening knots in the polar visualization), while healthy
  conversations spiral outward.
  - The Authority-Agency Mismatch. AI presents high authority (confident, fluent) but has zero agency (no accountability, no persistent state). Users
  keep trying to correct because social scripts say it should work. But corrections never "stick."

  What we built:
  - A 7-stage pipeline: move classifier (13 communicative act types, hybrid regex+LLM) → mode detector (3 interaction modes) → constraint tracker
  (deterministic state machine) → graph builder (NetworkX MultiDiGraph) → metrics computer (8 CUI diagnostic metrics) → visualization → export.
  - A Context Inventory Interface (the proposed solution): React frontend + FastAPI backend that externalizes implicit state into visible, persistent,
   editable UI elements. Three interaction patterns: Pin to Task (extract constraints from conversation), Context Lens (explicit scope selection),
  Task Shelf (multi-task management).
  - BLOOM Design System — interactive web visualizations (dashboard, explorer, global view, comparison tool) for researchers to inspect individual
  conversations.

  Formative evaluation (N=20):
  - User control: 4.2/5 (treatment with visible constraints) vs 2.8/5 (baseline chat-only)
  - Repair count: 1.2 (treatment) vs 3.7 (baseline)
  - Qualitative: "I could see what it was supposed to remember"

  ---
  Phase 3: Planning v2 (Now)

  What we just did in this session:

  1. Read through everything — both the v1 codebase (/Users/zac/Documents/Cartography) and the v2 codebase, including all audit documents, error logs,
   the comprehensive findings report, the theoretical framework, the pipeline code, the context engine, and the frontend.
  2. Catalogued every known problem — 3 blockers, 12 major issues, ~268 pipeline errors, methodology limitations, data quality gaps.
  3. Defined the research scope for v2, centered on three new questions:
    - RQ2a: What happens when we apply this framework to mental health conversations?
    - RQ2b: Can we rigorously define and describe these roles (not just label them)?
    - RQ2c: What happens when we show people their roles in real-time?
    - Cross-cutting: How does human-AI interaction compare to human-human through the same lens?
  4. Analyzed the context engine — mapped every API endpoint, data model, regex pattern, state machine transition, and LLM prompt. Discovered that the
   existing system already detects the behavioral signatures of roles — it just doesn't aggregate them into role labels yet.
  5. Wrote a detailed implementation plan (plan.md) with:
    - All v1 findings carried forward (evidence architecture, acceptance tests, honest ablation results)
    - A Context Engine Repurposing Strategy showing what stays, what extends, and what needs rebuilding (answer: almost nothing needs rebuilding —
  only the real-time incremental pipeline is genuinely new)
    - A Role Inference Layer design — roles as patterns over existing move/mode output
    - Specific extensions: 7 new therapeutic move types, 3 new interaction modes, 3 new violation types, 5 new mental health metrics, self-repair
  detection for human-human comparison
    - A 9-step build order with exact files to create/modify
    - Priority-tiered implementation table (P0 through P3)

  ---
  The Throughline

  v1 asked: "What's on the map?" Answer: Almost nothing. 98.8% instrumental. The relational territory is empty.

  v2 Phase 1 asked: "Why do conversations fail?" Answer: Implicit State Pathology. The medium is structurally broken — stateless systems pretending to
   maintain state creates an information-theoretic trap.

  v2 Phase 2 (next) asks: "What happens when people can see the map?" This is the open question. Does showing users their roles change anything? Does
  it activate the foreclosed relational modes? Does it reduce Agency Collapse? Does it matter differently in mental health contexts where the stakes
  are higher?

  The context engine we already built — the move classifier, mode detector, constraint tracker — is the measurement instrument. We're repurposing the
  diagnostic tool as a mirror.

  ---
  Phase 4: Mental Health Domain Extension (Feb 2026)

  What we did: Applied the full Cartography pipeline to mental health counseling data to test whether therapeutic contexts break the instrumental
  concentration. Two datasets:
  - **Single-turn counseling** (Amod/mental_health_counseling_conversations, N=100): Real licensed therapist responses to patient questions.
  - **Multi-turn caregiver counseling** (MentalChat16K PISCES subset, N=50): Multi-session behavioral health coach ↔ caregiver conversations
    (Alzheimer's, hospice, end-of-life care). Average 7.6 turns per session.

  Pipeline: Ran the full 7-stage pipeline with Claude Haiku (claude-haiku-4-5-20251001) for LLM steps. Built an Anthropic adapter
  (anthropic_adapter.py) to use Claude as a drop-in replacement for OpenAI in the pipeline. Also ran SRT role classification
  (classify_roles_srt.py) with Claude for role distributions and interaction dimensions.

  What we found:

  **The Instrumental Monopoly Breaks — Partially:**
  - In mental health, the dominant human role is **Social-Expressor (48.7%)**, not Information-Seeker. This is a dramatic shift from the general
    corpus (73.9% Information-Seeker). Patients lead with emotional sharing, not questions.
  - In multi-turn caregiver sessions, Social-Expressor rises to **58.1%** and Collaborator emerges at 11.7%.
  - But the AI side barely shifts: Expert-System (43.7%) + Advisor (37.8%) still dominate. The AI responds instrumentally to expressive human input.

  **Mode Violations Are Worse, Not Better:**
  - Single-turn: **98% mode violation rate** (vs 42% in general corpus). Nearly every counselor response violates the patient's mode.
  - Multi-turn: **79.4% mode violation rate**. Better than single-turn but still far worse than general corpus.
  - Dominant violation: **Unsolicited Advice** — patient shares emotional content in LISTENER mode, counselor immediately jumps to EXECUTOR.
  - This is the opposite of good therapeutic practice (listen first, advise later).

  **Emotional Tone Shifts Dramatically:**
  - General corpus: 56% neutral, professional
  - Single-turn mental health: 63% supportive, 29% empathetic
  - Multi-turn caregiver: **94% empathetic** — nearly universal
  - Conversation purpose: 69-86% **emotional processing** (vs 0.5% in general corpus)

  **PAD Affect Profile Differs:**
  - Patient Pleasure: 0.48 (lower than general corpus ~0.60-0.65)
  - Patient Arousal: 0.52 (comparable)
  - Patient Dominance: 0.51 (comparable)
  - Lower pleasure reflects the distressed nature of help-seeking

  **Structural Limitation Discovered:**
  - Single-turn counseling data is structurally incapable of showing mode dynamics — the counselor *must* advise in their only turn,
    making mode "violations" structurally inevitable. This is a methodological finding, not a clinical one.

  What this means:
  - The 97% instrumental finding is **domain-specific to general-purpose AI use**, not a universal property of human-AI interaction.
  - Mental health contexts activate the Social-Expressor role that is nearly absent (2.4%) in general conversation.
  - But the AI still responds instrumentally — creating a **Relational Mismatch** where the human is expressive and the AI is functional.
  - This is the "Relational Bypassing" we predicted: the system performs advisor moves without the relational infrastructure to sustain them.
  - Multi-turn data is essential for meaningful constraint/mode analysis. Single-turn data can only assess role distributions and affect.

  Scripts created:
  - scripts/download_mental_health.py — Downloads and converts Amod dataset
  - scripts/atlas/anthropic_adapter.py — Claude ↔ OpenAI adapter for pipeline
  - data/mental_health/ — Single-turn graphs, conversations, enriched metadata
  - data/mental_health_multiturn/ — Multi-turn PISCES graphs and conversations