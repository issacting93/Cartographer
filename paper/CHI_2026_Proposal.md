# Interactional Cartography: Mapping Constraint Failure as an Interactional Property of Large-Scale Human–LLM Conversations

**CHI 2026 Full Paper Proposal**

## Problem

Conversational interfaces have become the dominant interaction paradigm for large language models, yet they systematically fail at the task they are most frequently used for: sustained, constraint-sensitive work. When a user says "write me a story set on Mars with no aliens," the constraint *no aliens* has a median half-life of 2.49 turns before the system violates it without acknowledgment or negotiation. The user must then spend effort detecting and repairing the violation — effort we term the **Agency Tax**. Current discourse attributes these failures to model limitations. We argue they are interactional: conversation is an overloaded interface that simultaneously serves as coordination mechanism, memory store, and task manager, and this architecture produces predictable, measurable patterns of constraint decay.

This paper is not a model benchmark, not a prompt engineering study, and not a trust paper. It is an argument that the conversational medium itself — independent of model capability — is the mechanism of failure.

We make this claim falsifiable. If constraint failure were primarily a **capacity limitation** (context window, attention decay), violations should increase with conversation length, constraint count, and later turn position. We observe the opposite: decay happens within 2–3 turns, well before any window limit. If failure were primarily a **prompting problem** (ambiguous user language), constraints with clearer lexical form (strict hardness) should survive longer than flexible ones. We find that strict constraints (73% of corpus) still exhibit a median half-life under 3 turns, and mixed-hardness constraints — not ambiguous ones — show the worst survival rates. Both patterns are consistent with a medium-level mechanism and inconsistent with model-level or user-level explanations alone.

## Method

We introduce **Interactional Cartography**, a graph-structural method for diagnosing governance failure in human-AI dialogue. Our pipeline transforms 744 conversations from three public datasets (WildChat, Chatbot Arena, OpenAssistant) into heterogeneous multi-relational graphs.

### Pipeline

1. Parse raw conversation into turn sequence
2. Identify constraint statements (user-stated explicit instructions; implied constraints are excluded)
3. Classify constraint hardness (Strict / Flexible / Mixed) via LLM-assisted labeling
4. Detect violation events at the turn level (single-pass classification: did this turn adhere to each active constraint?)
5. Detect repair attempts (user moves that restate, correct, or reference a previously violated constraint)
6. Classify interaction mode per turn pair (Listener / Advisor / Executor)
7. Build directed multigraph (6 node types, 6 edge types encoding temporal, hierarchical, and causal relations)
8. Compute metrics per conversation

### Operational Definitions

- **Constraint**: An explicit, verifiable instruction stated by the user (e.g., "no aliens," "keep it under 500 words"). Implied preferences are excluded.
- **Violation**: A system turn that fails to adhere to an active constraint, as determined by turn-level classification.
- **Silent violation**: A violation with no accompanying acknowledgment, apology, negotiation, or "I can't do that" from the system.
- **Repair attempt**: A subsequent user turn that restates, corrects, or explicitly references the violated constraint.
- **Repair success** (conservative): A repair attempt followed by sustained constraint adherence for the remainder of the conversation. Partial or transient corrections are counted as failures.
- **Task completion**: The final turn of the conversation as recorded in the dataset (user stop or platform cutoff). We do not infer implicit completion.

### Core Metrics

- **Constraint half-life** — median turns from constraint statement to first violation. Conversations where no violation occurs are right-censored and excluded from the median; survival analysis (Kaplan–Meier) is used for the full distribution.
- **Survival rate** — proportion of constraints never violated through task completion.
- **Drift velocity** — total violations per turn, per conversation, normalized by the number of active constraints at each turn. Multiple violations in a single turn count individually. Reported as per-conversation values, then aggregated.
- **Agency tax** — repair moves per violation event. Measured by count of explicit repair moves (from the move taxonomy), not by token length or time.

### Analytical Controls

To control for task differences, we classify conversations along three dimensions (task architecture, constraint hardness, stability class) using LLM-assisted labeling. Two independent human annotators labeled N=150 conversations; disagreements were resolved by adjudication. Cohen's kappa was computed on this sample (kappa > 0.65 across all dimensions). Annotators were blind to hypothesized stability class.

Unsupervised clustering (HDBSCAN, yielding four stable clusters under parameter sweep) on nine conversation-level features provides a complementary, data-driven grouping. These classifications are instrumental — they allow us to ask whether the patterns hold *across* task types, not just in aggregate.

## Key Findings

### Constraint decay is early and invariant

Median constraint half-life is 2.49 turns (IQR: 1–4). This bound remains tightly consistent across datasets with different conversational norms and model families (WildChat: 2.4, Chatbot Arena: 2.6, OpenAssistant: 2.5), suggesting invariance to source and model capability. The distribution is right-skewed with a heavy tail — most constraints fail fast, a few persist. By task completion, 71.5% of user-stated constraints have been violated without acknowledgment or negotiation (silent violation).

### Users compensate; the medium defeats them

Users detect problems and attempt repair at a rate of 19.9%. Under our conservative definition — post-violation adherence for the remainder of the task — repair success is 0.1%. Under a lenient definition (adherence for the next 3 turns), success rises to approximately 4%, still indicating that the medium structurally resists correction. The dominant failure mode is not catastrophic collapse but chronic drift: **Constraint Drift** accounts for 48.5% of conversations, while full Agency Collapse occurs in only 2.8%. Users rarely surrender — they compensate. But the medium forces them into a costly cycle of monitoring and correction that degrades task performance.

### Failures pattern by task structure

Generation tasks (34% of corpus) show the highest drift velocity (0.032 violations/turn). Mixed-hardness constraints — where some rules are strict and others flexible — exhibit the worst survival rates. Task Shift, though rare (0.9%), correlates with the longest constraint half-lives (9.0 turns), suggesting that when the system fundamentally redefines the task, it does so gradually enough that users do not intervene early.

### Supporting evidence: role overstepping

The system enacts a different interaction mode than the user's request (e.g., advising when the user requested execution) in 42% of turn pairs. We report this as supporting evidence of medium-level misalignment — the same interface that loses constraints also loses role assignments — rather than as a separate core contribution.

## The Mechanism: Conversation as Overloaded Interface

The conversational medium is simultaneously performing three jobs that conflict:

1. **Coordination channel** — negotiating what we are doing right now
2. **Memory store** — holding what constraints exist and what has been decided
3. **Execution channel** — generating outputs

These jobs conflict because state is implicit (embedded in scrolling text), constraints are not externally inspectable (the user cannot see what the system "believes" is active), and revision history is not structured (earlier constraints are overwritten by later turns, not versioned). This architecture predicts exactly the pattern we observe: early half-life (constraints decay as soon as execution begins competing with memory), chronic drift (the medium provides no mechanism to detect or prevent it), and low repair success (repair is itself a conversational act, subject to the same decay).

This reframing predicts that improved models alone will not eliminate constraint failure unless the interface externalizes state. We test this prediction directly in the design validation below.

## Contribution

This work makes three contributions to CHI:

1. **Constraint failure as measurable interactional phenomenon.** We provide a reproducible graph-based method for quantifying constraint decay in conversational interfaces. The pipeline, annotation guidelines, and code will be released for replication.

2. **Diagnostic vocabulary for CUI evaluation.** The metrics — constraint half-life, drift velocity, agency tax, survival rate — give designers tools for evaluating conversational systems beyond task completion and user satisfaction. These metrics are interface-level, not model-level, and apply to any system where users issue persistent instructions through conversation.

3. **Empirical grounding for task-first interaction design.** Our evidence motivates task-first design because it targets the mechanism: implicit state decay in the conversational medium. This is not a claim that task-first is proven superior, but that our diagnosis identifies the specific interface property it would need to address.

## Design Implication Validation (Ongoing)

Our analysis predicts that externalizing constraints as persistent, user-governable objects should reduce repair effort by removing the medium as a source of decay. We test this prediction in a between-subjects comparative study (target N=80, 40 per condition) evaluating a **Context Inventory Interface (CII)** against a standard chat baseline.

- **Tasks:** Constraint-heavy scenarios (career coaching, travel planning) requiring 5+ active constraints over 10+ turns
- **CII implements** three interaction patterns: constraint pinning (text to persistent node), task shelving (explicit scope switching), and context lensing (user-controlled scope selection)
- **Primary DVs:** Repair turns (count of user turns spent restating or correcting), constraint survival rate, perceived control (7-point Likert)
- **Baseline:** Standard single-stream chat interface with the same underlying model

Preliminary results (N=24) show a 4.2x reduction in repair turns and significant gains in perceived control. The full study will be completed prior to submission.

## Threats to Validity

**Construct validity.** Constraint detection is limited to explicit user statements; implied constraints are excluded, which may undercount total constraint load. Violation detection depends on turn-level classification quality, validated by inter-rater agreement but not exhaustively verified. Repair success is defined conservatively; we report sensitivity under a lenient alternative.

**Internal validity.** Task type, conversation length, and constraint count are potential confounds. We mitigate this through analytical controls (classification by architecture, hardness, stability) and by reporting metrics stratified by these dimensions. The invariance of half-life across strata supports a medium-level rather than task-level explanation.

**External validity.** Public datasets (WildChat, Chatbot Arena, OpenAssistant) may not represent enterprise or domain-specific usage. However, their breadth (three sources, multiple model families, diverse task types) provides ecological variety uncommon in CUI studies.

**Reliability.** Inter-rater reliability on key labels exceeds kappa > 0.65. Annotation guidelines and code will be released to enable replication.

## Proposed Figures

1. **Kaplan–Meier survival curve** of constraint adherence over turns, stratified by stability class — the visual anchor for constraint half-life
2. **Histogram of half-life distribution** showing the right-skewed, heavy-tailed pattern of early failure
3. **Annotated graph vignette** — one conversation rendered as a multigraph, showing a constraint node's lifecycle from STATED through VIOLATED to failed REPAIR, making the representation concrete
4. **Drift velocity by task architecture** (bar chart) — showing that generation tasks are structurally most vulnerable
5. **CII vs. baseline** comparison (repair turns, survival rate, perceived control) — the design validation result

## Fit to CHI

This work sits at the intersection of conversation analysis, information visualization, and interaction design. It speaks directly to the CHI community's concern with user agency in AI systems, contributing both an empirical method (interactional cartography) and a design argument (task-first interaction) grounded in large-scale behavioral evidence. The Atlas visualization system, graph pipeline, annotation guidelines, and full dataset will be released as open-source research tools.
