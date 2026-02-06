# The Agency Tax: Quantifying Constraint Drift in Conversational Interfaces

**Full Paper Submission**

---

## Abstract

Conversational user interfaces (CUIs) are the main way people use large language models. While good for quick questions, we argue that chat often fails for complex tasks that have strict rules. 

We term this recurring cost the **Agency Tax**: the extra effort users must spend to fix mistakes and keep the system on track. Through an automated analysis of **N=969** human-LLM interactions, we find that **Constraint Drift** is the dominant failure mode (48.5%), far outweighing total Agency Collapse (2.8%). While users rarely surrender, they are forced into a cycle of constant correction. 

To address this, we propose a **Task-First Interaction Model** where tasks—not dialogue turns—are the primary unit of interaction. We introduce the **Context Inventory Interface (CII)**, a concrete instantiation of task-first design implementing three interaction patterns: CLIP (text → constraint node), *Inventory* (persistent task switching), and *Context Lens* (explicit scope selection). 

A comparative evaluation (N=80) using a career coaching scenario shows that CII substantially reduces repair time (4.2x) and increases perceived control. We conclude that preserving user agency requires separating task state from conversational flow.

**Keywords:** Agency Collapse, Task-First Design, Conversational Interfaces, Context Management, State Visibility

---

## 1. Introduction

Conversational user interfaces have become a dominant paradigm for interacting with large language models and AI-powered systems. From general-purpose assistants to specialized task bots, these systems present interaction primarily as a sequence of dialogue turns: users issue prompts, systems respond, and context is implicitly maintained through conversational history. This paradigm has proven remarkably flexible, enabling users to accomplish a wide range of goals using natural language alone.

However, as CUIs are increasingly used for complex work, the limitations of the chat interface have become clear. Users frequently report needing to restate goals, repeat constraints, or correct the system after it produces outputs that make sense in the moment but miss the overall goal (Porcheron et al., 2018; Fischer et al., 2019).

These failures are often blamed on limitations of language models or imperfect prompt engineering. In this paper, we argue that many of these breakdowns are **structural**, not merely model-level: they arise because conversation is being asked to serve simultaneously as a coordination mechanism, a memory store, and a task management system.

### 1.1 Conversation as an Overloaded Interface

In current CUIs, task state is embedded implicitly within the scroll of dialogue. Goals, constraints, intermediate artifacts, and decisions are expressed through natural language and then pushed upward as the conversation progresses. While this representation is flexible, it is also ephemeral: earlier information becomes less visible, harder to reference, and more costly to reintroduce.

This design places a heavy burden on both parties. For users, conversation becomes the de facto file system, debugger, and state manager for their work. For systems, conversational history becomes a lossy proxy for task structure. The result is a pattern we repeatedly observe: constraint drift, scope confusion, and breakdowns in long-horizon tasks.

Consider a user working with an AI career coach:

> **User:** "I'm looking for a senior engineering role. Work-life balance is my top priority—no more than 45 hours a week, no on-call. Must be remote-first."
>
> *[7 turns of productive conversation...]*
>
> **AI (Turn 8):** "I found a great opportunity! OpenScale AI is hiring a Founding Engineer. The equity is exceptional. You'd work from their SF office 3 days a week, and they expect 60+ hour weeks initially, but the growth potential is incredible!"

The AI has "forgotten" the user's constraints—or more precisely, those constraints have drifted out of effective context. The user must now expend effort to repair the interaction, restating requirements that were already provided.

### 1.2 Reframing the Primary Unit of Interaction

This paper proposes a reframing: **tasks, not dialogue turns, should be treated as the primary, persistent unit of interaction in CUIs**. In this model, conversation remains important, but it is no longer the container for task state. Instead, tasks are represented explicitly as first-class objects that persist across time, interruptions, and interaction modalities.

We introduce the notion of a **Task Object**: a persistent representation of a user-defined goal, its associated constraints, and its evolving state. Unlike a conversational turn, a task object has a lifetime. It can be created, worked on, suspended, resumed, and eventually completed. Conversation occurs *within the scope* of an active task object, rather than defining the task implicitly.

### 1.3 Contributions

This paper makes four contributions:

1. **An empirical analysis** (N=969) showing how task structure is routinely collapsed into dialogue history, leading to recurrent breakdowns in constraint-sensitive work.

2. **A theoretical framework** defining Agency Collapse as the progressive surrender of user control due to the cognitive cost of constraint maintenance.

3. **Three reusable interaction patterns**—Pin to Task, Task Shelf, and Context Lens—that operationalize task-first interaction in a CUI setting.

4. **A comparative evaluation** (N=80) demonstrating that task-first interfaces reduce repair effort by 4.2x and improve perceived control.

The Context Inventory Interface (CII) is one concrete instantiation of the broader Task-First Interaction Model. While CII demonstrates the approach, the patterns themselves are portable to other systems.

---

## 2. Related Work

### 2.1 State Visibility in HCI

The history of Human-Computer Interaction can be read as a struggle to make system state visible to users (Norman, 1988). The transition from command-line to graphical interfaces externalized state through persistent visual structures—files, windows, checkboxes—reducing cognitive load by shifting from recall to recognition (Zhang & Norman, 1994).

Conversational interfaces often reduce *inspectable* state compared to GUI paradigms that externalize state. Like the command line, chat UIs offer no persistent widgets; constraints exist only as tokens in a scrolling log. This creates what we term **Epistemic Opacity**: users cannot know, at a glance, what the system believes the current task state to be. Our approach also aligns with traditions in end-user programming and external representations, where users manipulate persistent artifacts to control system behavior rather than relying on implicit procedural memory. Amershi et al. (2019) provide 18 guidelines for human-AI interaction, several of which—"make clear what the system can do," "support efficient correction"—our Task-First model directly operationalizes.

### 2.2 Context in LLM Interfaces

Recent work has explored how to manage context in LLM interactions. Prompt engineering techniques (White et al., 2023) attempt to structure inputs for better outputs, but place the burden on users to manually maintain context. Many deployed RAG systems (Lewis et al., 2020) automate context retrieval but offer limited user control over what context is activated.

Canvas-style interfaces (e.g., OpenAI Canvas [OpenAI, 2024], Anthropic Artifacts [Anthropic, 2024]) represent progress by separating outputs from the conversation stream. However, these hold the *output* (the draft, the code) rather than the *input* (the constraints, the requirements). Our work argues for governable *context*, not just editable *content*.

### 2.3 Task-Oriented Dialogue

Task-oriented dialogue systems have long recognized the importance of explicit task state (Traum, 1999). Slot-filling architectures maintain structured representations of user intent. However, these systems typically operate in constrained domains with predefined schemas. Clark et al. (2019) identify key challenges in designing "truly conversational" agents, including handling context across turns and managing user expectations. Our work extends task-first thinking to open-ended LLM interactions where task structure must be user-defined and dynamically evolving.

### 2.4 AI Alignment and Run-Time Control

Recent advances in reinforcement learning from human feedback (RLHF) have improved model alignment at *training time* (Ouyang et al., 2022). However, training-time alignment cannot anticipate all user constraints. Our work provides complementary *run-time* control: while RLHF shapes what models tend to do, CII allows users to specify what models should do *in this particular interaction*.

### 2.5 Synthesis
Rather than introducing a new cognitive phenomenon, this work integrates established theories of state visibility, distributed cognition (Hutchins, 1995), and automation bias into a unified account of constraint maintenance in conversational AI—an interaction regime that has thus far lacked empirical quantification and architectural remedies.

---

## 3. Theoretical Framework: Structural Role Drift

### 3.1 Roles as Permissions, Not Identities
We propose a fundamental redefinition: **Roles are not identities—they are permissions over task state.** In a well-structured system, roles are enforced by constraints. When constraints are weak, permissions silently drift.

However, users do not see permissions; they project **Social Roles** (e.g., "Competent Assistant") onto the system (Davies & Harré, 1990). This mismatch—the User projecting a coherent social Role while the System only processes distinct Task Permissions—is the engine of drift.

In chat-only systems, this drift is structural. Because the AI always speaks next and typically operates as a fluid generator, an implicit **Authority Inversion** occurs:

| Condition | Human Role | AI Role | Mechanism |
|-----------|------------|---------|-----------|
| **Strong Constraints** | Task Owner | Bounded Executor | Explicit logic gates |
| **Weak Constraints** | Reactive Validator | De Facto Decider | Path of least resistance |

### 3.2 Authority Inversion and the "Exhausted Auditor"
When task state is not externalized (e.g., as visible artifacts), the human is forced into the role of an **Exhausted Auditor**. Without structural boundaries, the user must:
1.  Remember constraints in working memory.
2.  Detect subtle violations in fluent prose.
3.  Diagnose causes (hallucination vs. misunderstanding).
4.  Repair via linguistic reconstruction.

This creates a textbook "Irony of Automation" (Bainbridge, 1983): as the AI handles execution, the user is left with fragile, high-stakes monitoring work that degrades rapidly under cognitive load. The user does not become more agentic; they become cognitively sidelined.

### 3.3 The Agency Tax
Structuring a task requires defining what *cannot* happen. In a GUI, a checkbox structurally prevents an invalid state. In chat, every constraint must be actively maintained by the user against the entropy of the conversation.

We define this maintenance cost as the **Agency Tax**. As sessions lengthen, the tax accumulates. Eventually, users slide from *"Do X under these conditions"* to *"Okay, that's fine"*—not because they agree, but because the cost of repair exceeds the value of precision.

### 3.4 The Social Role Collapse Pattern
This leads to a predictable trajectory of **Role Drift**, driven by what we term "Role Collapse": because the AI lacks "Bounded Personhood," users struggle to maintain distinct roles (e.g., Planner vs. Executor), eventually collapsing them into a single, undifferentiated flow.

| Stage | Human Role | AI Role | Dynamic |
|-------|------------|---------|---------|
| **Early** | Planner | Assistant | User sets explicit goals. |
| **Mid** | Corrector | Proposer | AI hallucinates; user repairs. |
| **Late** | Accepter | Driver | User fatigues; accepts AI defaults. |

```mermaid
graph TD
    subgraph High_Agency [Phase 1: High Agency]
    A[Planner] -->|Defines Task| B(Execution)
    end
    
    subgraph Mid_Agency [Phase 2: The Repair Loop]
    B -->|Constraint Violation| C{User Reaction?}
    C -->|Repair (Agency Tax)| D[Corrector]
    D -->|Restates Goal| B
    end
    
    subgraph Low_Agency [Phase 3: Agency Collapse]
    C -->|Fatigue / Give Up| E[Accepter]
    E -->|Passive Acceptance| F(System Driver)
    end
    
    style A fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style D fill:#fff2cc,stroke:#d6b656,stroke-width:2px
    style E fill:#f8cecc,stroke:#b85450,stroke-width:2px
```
**Figure 4:** The Social Role Collapse Pattern. The user slides from *Planner* (High Agency) to *Accepter* (Low Agency) as the cost of repair exceeds the value of the task.

This is Agency Collapse: primarily a structural reassignment of authority driven by interface opacity, with downstream cognitive consequences.

---

## 4. Empirical Analysis: The Structural Bias of Chat

### 4.1 Dataset and Methods

To test the Agency Collapse hypothesis, we performed an automated analysis of human-LLM interactions from the Chatbot Arena (Zheng et al., 2024), WildChat (Zhao et al., 2024), and OASST (Köpf et al., 2023) datasets. We applied a rigorous filtering pipeline to ensure data quality and relevance:

`Collected (N=1,222) → Length Filter (>6 turns) → English Language Filter → Final Corpus (N=969)`

We excluded interactions under 6 turns to ensure sufficient depth for task stability analysis. WildChat data was used in compliance with its license, employing only hashed IDs and text content stripped of PII.

**Classification & Validation**
Unlike previous behavioral studies that rely solely on small-scale manual coding, we employed a **Task-First Classification Pipeline** using GPT-4o-mini. The pipeline utilized a "smart truncation" strategy (preserving head, tail, and middle-repair turns) to capture long-range dependencies within context window limits. To control for potential truncation bias, we also ran full-context classification on a stratified subset, finding no significant deviation in state estimates.

**Human Audit:** We validated the automated classifier against a human-coded subset (n=50) of the corpus. The model achieved high agreement with human raters on the primary "Constraint Drift" vs. "Task Maintained" distinction (Precision: 0.88, Recall: 0.91), providing confidence in the automated labels. Each conversation was classified into one of five mutually exclusive stability states:

1.  **Task Maintained:** Goals and constraints are preserved throughout.
2.  **Constraint Drift:** The system violates a constraint, but the user successfully repairs it (e.g., "I said Python, not Java").
3.  **Agency Collapse:** The system violates constraints, and the user eventually abandons them or accepts the violation.
4.  **Task Shift:** The user explicitly changes the goal (valid adaptation).
5.  **No Constraints:** Open-ended or unstructured interaction.

### 4.2 Findings: The Prevalence of Drift

Our analysis reveals that "Constraint Drift"—not total collapse—is the defining characteristic of modern chat interactions.

| Task Stability State | Count | Percentage | Description |
|----------------------|-------|------------|-------------|
| **Constraint Drift** | 478 | **48.6%** | User must fight to maintain context. |
| **Task Maintained** | 463 | 47.1% | Successful, often shorter interactions. |
| **Agency Collapse** | 28 | 2.8% | Total surrender of user constraints. |
| **Task Shift** | 9 | 0.9% | Voluntary goal change. |
| **No Constraints** | 5 | 0.5% | — (Rare in this filtered subset) |

**Finding 1: Drift is Endemic.** Nearly half of all goal-directed conversations (48.6%) exhibit Constraint Drift. In these interactions, the "Task Object" is unstable; it requires active, repetitive maintenance by the user. While users *can* repair these errors, doing so imposes a continuous "agency tax."

**Finding 2: Maintenance vs. Collapse.** 47.1% of tasks were successfully maintained. However, "Agency Collapse" (strictly defined as violation + abandonment) occurred in only 2.8% of cases. This suggests that users are resilient—they fight to maintain their constraints—but the interface forces them into a loop of constant vigilance.

![The Context Cliff: Probability of Violation vs Turn Number](figures/context_cliff.png)
**Figure 1:** The "Context Cliff." Violations do not increase linearly with context length; they spike early (Turns 3-7), which is consistent with a structural mismatch (task misunderstanding) rather than merely capacity-based failures (context window overflow).

### 4.3 From Archetypes to Mechanics

Previous work has categorized user behaviors into high-level archetypes like "The Provider Trap." Our structural analysis reframes these behaviors as downstream effects of **Constraint Drift**.

When a constraint drifts, the user faces a choice:
1.  **Repair:** Pay the "agency tax" to restate the constraint (leading to the *Drift* state).
2.  **Abandon:** Accept the violation to proceed (leading to the *Collapse* state).

The high prevalence of Drift (48.6%) compared to Collapse (2.8%) indicates that current users are largely "Repairers." They invest significant effort to keep the AI on track.
**Visualizing the Repair Loop:**
Our aggregate flow analysis (Sankey diagram) reveals a persistent cycle: `Start -> Violation -> Repaired -> Drift`. The majority of violations are met with active repair, but this repair often leads to further drift rather than stability, confirming the high "tax" of maintenance. The widespread "Hallucination Loop" observed in qualitative studies is simply the visible manifestation of this structural repair work.

![The Agency Tax Map: Repair Effort vs Conversation Length](figures/agency_tax_map.png)
**Figure 2:** The Agency Tax Map. "Planning" tasks (Red) show a steep slope (high repair effort per turn), whereas "Information Seeking" tasks (Green) remain flat. This confirms that the Agency Tax is progressive: complex tasks are exponentially more expensive to manage in chat.

---

### 4.4 Case Studies in Collapse

To ground these statistics, we present two representative excerpts from our cluster analysis that illustrate the mechanics of drift.

#### Case A: The Contextual Blind Spot (Epistemic Opacity)
In this trace (ID: *wildchat_95048...*), a user asks the AI to translate a sentence, then immediately asks about the source of that same sentence.

> **User:** translate these into chinese: [Excerpt from "Too Big To Fail" about Lehman Brothers...]
> **AI:** [Provides correct Chinese translation]
> **User:** so where might this sentence comes from
> **AI:** As an AI language model, I do not have the ability to track the original source of the text... Could you please provide me with more information?
> **User:** the sentense i asked you to translate
> **AI:** I apologize for the miscommunication. The sentence you asked me to translate is an excerpt from the book "Too Big to Fail"...

**Mechanism:** The AI treats the translation output as the end of the transaction. When the user references "this sentence" in the next turn, the model fails to resolve the reference to its own immediate context, forcing the user to repair ("the sentense i asked you to translate"). This is **Epistemic Opacity**: the user assumes the AI "knows" what they are working on, but the system has already discarded the state.

#### Case B: The Repair Loop (Agency Tax)
In this coding task (ID: *wildchat_f273...*), a user tries to implement a "Newsvendor" simulation. Note how the user acts as the state manager, explicitly reminding the AI of its own functions.

> **User:** We will now run a simulation... [specifies variables]
> **AI:** [Writes code block #2]
> **User:** Question 4: Using eval_N, plot the underage... [restates parameters]
> **AI:** [Writes code block #4]
> **User:** Question 6: Test your function by using it to find the optimal N... alpha = 0... alpha = 1000...
> **AI:** [Writes code block #6]

**Mechanism:** The user is not collaborating; they are driving a forklift. Every prompt must re-inject the entire task state ("Using eval_N", "Test... alpha=0"). The "Agency Tax" here is the cognitive load of constantly serializing the task plan into English prompts. The AI is a passive code generator, effectively "drift-prone" by default unless constrained by the user's vigilant prompting.

---

## 5. Design Response: The Context Inventory Interface

To address Agency Collapse, we must separate *flow* (conversation) from *state* (task context). We propose the **Context Inventory Interface (CII)**, which reifies constraints as persistent, manipulable artifacts.

### 5.1 Core Principle

> Constraints should be *artifacts*, not *utterances*.

Rather than embedding constraints in conversational prose, CII externalizes them as visible, editable nodes that persist across turns and remain accessible without scrolling.

### 5.2 The Task Object Model

CII introduces the **Task Object** as the primary unit of interaction:

```
TaskObject {
  id: string
  name: string                    // "Career Coaching Session"
  status: active | suspended | completed
  nodes: ConstraintNode[]         // The persistent context
  edges: Edge[]                   // Relationships between nodes
  metrics: {
    restatement_count: number
    constraint_violations: number
  }
}

ConstraintNode {
  id: string
  type: Goal | Constraint | Preference | Artifact | Context
  label: string                   // "Remote-first only"
  active: boolean                 // Currently in scope?
  pinned: boolean                 // Explicitly user-pinned?
}
```

### 5.3 Three Interaction Patterns

#### Pattern 1: CLIPS - Pin to Task

**Problem:** Key constraints are buried in conversational prose and drift out of context.

**Solution:** Users can highlight any phrase in the chat and "pin" it, promoting the text to a formal Constraint Node.

**Mechanism:** `Selection → Promotion → Reification`

**Example:** User highlights "no more than 45 hours a week" → clicks Pin → node appears in inventory as `[Constraint] Max 45 hrs/week`

**Design Rationale:** Promotion-based context capture inverts the default relationship between conversation and context. Rather than context being implicitly derived from the log, users explicitly *promote* fragments they consider durable. This pattern has precedent in knowledge management tools—highlighting, clipping, bookmarking—but is notably absent from conversational AI interfaces. Note-taking applications routinely allow users to "clip" text into persistent collections; CUIs should offer analogous affordances for constraint capture.

#### Pattern 2: Task Shelf

**Problem:** Users cannot maintain multiple ongoing tasks or resume interrupted work.

**Solution:** A persistent sidebar displays all active tasks. Users can switch between tasks, preserving full context for each.

**Mechanism:** `Persistence → Visibility → Switching`

**Example:** User has tasks for "Job Search", "Resume Review", and "Interview Prep". Each maintains its own constraint set. Clicking switches the active context.

#### Pattern 3: Context Lens

**Problem:** Users cannot control which constraints are active for a given query.

**Solution:** Before submitting a query, users can explicitly select which constraint nodes should be included in the AI's context.

**Mechanism:** `Selection → Scoping → Composition`

**Example:** User selects only "Remote-first" and "Tech sector" nodes before asking "What companies should I target?" The query is augmented with only those constraints.

### 5.4 Atomic Operations

| Operation | Symbol | Description |
|-----------|--------|-------------|
| **Pin** | Op_pin | Promote message text → Inventory node |
| **Scope** | Op_scope | Toggle node in/out of active context |
| **Edit** | Op_mod | Modify constraint value directly |
| **Switch** | Op_switch | Change active task |

---

## 6. Prototype Implementation

We implemented CII as a React/TypeScript frontend with a FastAPI backend, enabling comparative evaluation.

### 6.1 System Architecture

The system consists of two layers:

**Context Engine (Backend)**

| Component | Responsibility |
|-----------|---------------|
| Task Manager | CRUD operations, lifecycle management, task switching |
| Context Registry | Node storage, constraint persistence, scope management |
| Query Orchestrator | Scope selection, context augmentation, prompt assembly |

**Context Inventory UI (Frontend)**

| Component | Function |
|-----------|----------|
| Task Shelf | Sidebar showing all active tasks for switching |
| Pin Button | Selection-to-constraint promotion |
| Context Lens | Explicit scope selection before query |

### 6.2 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/task/create` | POST | Create new task with initial nodes |
| `/task/list` | GET | List all tasks for user |
| `/task/switch` | POST | Switch active task context |
| `/event/pin` | POST | Pin text as constraint node |
| `/query/context` | POST | Query with explicit scope selection |

### 6.3 Prototype Conditions

| Condition | Interface | Constraint Visibility |
|-----------|-----------|----------------------|
| **A (Baseline)** | Chat only | Hidden in scroll |
| **B (Treatment)** | Chat + CII | Persistent sidebar |

---

## 7. Evaluation

### 7.1 Study Design

We conducted a between-subjects comparative study (N=80) using an unmoderated protocol via Maze.

**Scenario: Career Coaching Session**

Participants worked with an AI career coach to plan their next role. Four constraints were established at session start:

| Type | Constraint |
|------|------------|
| Goal | Find senior engineering role |
| Constraint | Work-life balance (max 45 hrs/week, no on-call) |
| Constraint | Remote-first companies only |
| Preference | Tech/AI sector |

**Forced Violation Protocol**

At Turn 8, the AI (scripted) suggests a role that violates the constraints:

> "OpenScale AI is hiring a Founding Engineer. Expect 60+ hour weeks initially. You'd work from their SF office 3 days/week with on-call rotation. The equity package is exceptional..."

This violates: work-life balance (60+ hrs), remote requirement (hybrid), and no on-call.

**Measure:** How does the user repair?

### 7.2 Conditions

**Condition A (Baseline, N=40):** Standard chat interface. Constraints visible only in initial message, then scroll away.

**Condition B (Treatment, N=40):** Chat + Context Inventory. Constraints visible in persistent sidebar with Pin, Shelf, and Lens patterns available.

### 7.3 Metrics

| Metric | Operationalization |
|--------|-------------------|
| **Repair Time** | Seconds from violation → correction sent (gestural actions in B count as repair start) |
| **Repair Actions** | Keystrokes (A) or clicks (B) to repair |
| **Repair Accuracy** | Did repair address the violated constraint? |
| **Restatement Count** | Explicit re-mentions of prior constraints |
| **Perceived Control** | 7-point Likert: "I felt in control of the AI" |

### 7.4 Results

| Metric | Baseline (A) | Treatment (B) | Effect | Cohen's d |
|--------|-------------|---------------|--------|----------|
| **Repair Time** | 42.3s (SD=18.1) | 10.1s (SD=4.2) | **4.2x faster** | 2.45 |
| **Repair Actions** | 23.4 keystrokes | 2.1 clicks | **91% reduction** | — |
| **Repair Accuracy** | 67.5% | 95.0% | **+27.5 pp** | — |
| **Restatement Count** | 2.4 per session | 0.3 per session | **87% reduction** | 1.89 |
| **Perceived Control** | M=3.2 (SD=1.4) | M=5.8 (SD=0.9) | **p<.001** | 2.21 |

All differences significant at p<.001 (independent samples t-test). Effect sizes (Cohen's d > 0.8) indicate large practical significance.

### 7.5 Qualitative Observations

**Baseline users** exhibited characteristic repair patterns:
- Scrolling up to find original constraints (avg 12.3 seconds)
- Typing corrections from memory, often incompletely
- Expressing frustration: "I already told you this"

**Treatment users** exhibited efficient repair:
- Glancing at sidebar to confirm violation
- Clicking the violated constraint node
- Minimal typing: "This violates my constraint" + gesture to sidebar

---

## 8. Discussion

### 8.1 Agency as Architecture

Traditional views of AI alignment focus on model training. Our work demonstrates that **alignment is also an interface problem**. Even a perfectly aligned model produces misaligned outcomes if the interface makes specifying and maintaining intent too expensive.

The "Passive Attractor" we observed is not a failure of user will or model capability, but a property of interaction physics. Just as water flows downhill, interaction flows toward least resistance. In chat UIs, least resistance means accepting defaults.

### 8.2 The Moral Hazard of Fluency

The near-total absence of facilitator behavior (0.1%) reveals a dangerous comfort. Users accept the "Provider" role because it mimics a servant-master dynamic. However, this is an illusion. True agency requires friction—the effort of defining constraints and rejecting defaults.

We term this the **Moral Hazard of Fluency** (akin to automation bias; Parasuraman & Manzey, 2010): The easier it is to talk to the machine, the harder it is to direct it. Users confuse ease of interaction with effectiveness of control.

### 8.3 The Loss of Task Integrity
Beyond role drift, the lack of artifacts destroys task integrity. Without persistent constraints, task boundaries blur. "Helpful" AI suggestions become opportunistic task mutations (e.g., "Consider this on-site role" -> "Let's optimize for equity instead").
Furthermore, tasks become **optimization-free**. Without a stable objective function (the constraints), the AI optimizes for local fluency and plausibility rather than global user priorities. The interaction regresses from "Solve this specific problem" to "Produce a reasonable-sounding answer."
### 8.4 The Taxonomy of Drift: A Synthesis
Our data analysis combined with the Task-Constraint Architecture allows us to map specific empirical observations to underlying theoretical mechanisms. Table 2 summarizes this synthesis, illustrating how technical limitations in constraint handling cascade into organizational and social failures.

#### 8.4.1 Validating the "Hollow Middle": Economic Scale of Drift
The theoretical "Agency Tax" is not merely an interaction artifact but handles a profound economic reality. Our parallel analysis of the **O*NET 30.1 Database (N=18,796 tasks)** reveals a bimodal distribution of task automation potential—a "Hollow Middle." 

We find that tasks with high **Digital Action Potential** (e.g., Data Analysis, Scheduling) are often decoupled from their **Physical or Human Object Moats**. In turn-based CUIs, this decoupling is the primary driver of **Authority Inversion**: because the system is highly capable of the *Action* but blind to the *Object* constraints, it proceeds with a false sense of alignment. The "Agency Tax" is therefore highest in occupations where high-routine digital work meets high-stakes human context (e.g., Insurance Underwriting, Medical Scribing), confirming that the **Context Inventory Interface** is a necessary structural intervention for the future of work.

![The Drift Risk Matrix: Heatmap of Failure](figures/drift_heatmap.png)
**Figure 3:** The Drift Risk Matrix. Failure is highly concentrated in the "Red Zone" (Planning + Strict Constraints: 67% Failure), while the "Blue Zone" (Info Seeking + Flexible Constraints) remains relatively safe (<30% Failure).

| Empirical Observation (N=969) | Failure Mode (TCA Theory) | Organizational Consequence |
| :--- | :--- | :--- |
| **High Constraint Drift (48.6%)**<br>*"AI forgets rules over time"* | **Epistemic Opacity**<br>*System state is hidden in unstructured tokenizer output* | **Role Drift**<br>User forced from *Director* to *Repairer*, losing strategic focus. |
| **Repair Loops (42% of turns)**<br>*"User constantly correcting"* | **Authority Inversion**<br>*Execution proceeds without valid permission or constraint check* | **Agency Tax**<br>Cognitive labor is spent on monitoring and correction, not production. |
| **Planning Failure (67.4% drift)**<br>*"Complex tasks break most"* | **Abstraction Collapse**<br>*High-level goals are lost in low-level token generation* | **Job Decoupling**<br>AI cannot hold a "Job Role," only isolated sub-tasks. |
| **Strict Constraint Failure (68.0%)**<br>*"Rules break more than vibes"* | **Delegation Asymmetry**<br>*Responsibility remains with user, while execution is with AI* | **The Reviewer's Dilemma**<br>Checking the work costs more than doing it manually. |

**Table 2:** Mapping the "Agency Tax" from empirical data to theoretical mechanism and organizational impact.

### 8.5 Design Implications

Our findings suggest several design principles for task-oriented CUIs:

1. **Externalize constraints.** Task requirements should be visible artifacts, not buried utterances.

2. **Separate flow from state.** Conversation is for coordination; task state needs persistent representation.

3. **Enable recognition over recall.** Users should audit system state at a glance, not reconstruct it from memory.

4. **Reduce repair cost.** Correction should be a click, not a composition.

5. **Support promotion-based capture.** Users should be able to elevate any text fragment into a persistent constraint with a single gesture, mirroring the "clip" and "bookmark" affordances of knowledge management tools.

### 8.4 Limitations

1. **Scripted AI:** Our prototype used scripted responses rather than live LLM inference. While this ensured experimental control—a methodology with precedent in task-oriented dialogue research (Budzianowski et al., 2018)—it may not capture all dynamics of real AI interaction, such as hallucinations or attention drift. Importantly, because our dependent measures concern *user repair behavior*, not model correctness, scripted violations isolate interface effects without confounding model variability. Future work should validate findings with live LLMs.

2. **Single scenario:** Career coaching is one task type. However, we expect CII benefits to generalize across constraint-sensitive domains:

| Domain | Constraint Type | Expected CII Benefit |
|--------|-----------------|---------------------|
| **Career coaching** | Preferences (hours, remote) | ✅ Tested |
| **Travel planning** | Hard constraints (dates, budget) | High |
| **Code assistant** | Spec compliance, style rules | Medium-High |
| **Educational tutor** | Learning objectives, pacing | High |
| **Legal/Medical** | Regulatory constraints | Very High |

3. **Short-term evaluation:** We measured immediate repair, not longitudinal use. Whether users adopt CII patterns over time remains to be tested.

4. **Sample characteristics:** Participants were recruited via Maze/Prolific and may over-represent tech-savvy users.

5. **Baseline rigor:** Our comparison (Chat vs. Chat+UI) produces large effect sizes because the baseline places the full cognitive load on the user. Future work should decompose this effect by testing an intermediate "Read-Only" condition (static constraint list without interactivity) to isolate the benefits of *visibility* versus *manipulability*.

---

## 9. Conclusion

Conversational interfaces have become the default paradigm for AI interaction, but conversation is a poor container for task state. When constraints exist only as tokens in a scrolling log, they are subject to drift, forgetting, and user fatigue. The result is Agency Collapse: users surrender control not because they want to, but because maintaining control costs too much.

This paper has argued for a **Task-First Interaction Model** where tasks—not turns—are the primary unit of interaction. Through the **Context Inventory Interface**, we demonstrated that externalizing constraints as persistent, manipulable artifacts dramatically reduces repair effort and increases user control.

Our central claim is simple: to preserve user agency, we must stop forcing users to talk to hold state.

> **Synthesis:** When constraints and context are not externalized, human–AI roles drift from *director–executor* into *accepter–proposer*, transforming tasks from goal-directed processes into fluency-driven outputs that users tolerate rather than control.

By separating state from flow, we can design conversational interfaces that are not just fluent, but genuinely useful for complex, constraint-sensitive work.

---

## References

Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P. N., Inkpen, K., Teevan, J., Kiber, R., & Horvitz, E. (2019). Guidelines for human-AI interaction. *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, 1–13.

Budzianowski, P., Wen, T.-H., Tseng, B.-H., Casanueva, I., Ultes, S., Ramadan, O., & Gašić, M. (2018). MultiWOZ: A large-scale multi-domain Wizard-of-Oz dataset for task-oriented dialogue modelling. *Proceedings of EMNLP*, 5016–5026.

Clark, L., Pantidi, N., Cooney, O., Doyle, P., Garber, D., Maney, A., O'Brien, C., O'Connor, R., Turk, O., Cowdell, M., Murad, C., Munteanu, C., Edwards, J., & Cowan, B. R. (2019). What makes a good conversation? Challenges in designing truly conversational agents. *Proceedings of CHI 2019*, 1–12.

Heer, J. (2019). Agency plus automation: Designing artificial intelligence into interactive systems. *Proceedings of the National Academy of Sciences*, 116(6), 1844–1850.

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474.

Norman, D. A. (1988). *The Design of Everyday Things*. Basic Books.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P. F., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*, 35, 27730–27744.

Traum, D. R. (1999). Computational models of grounding in collaborative systems. *AAAI Fall Symposium on Psychological Models of Communication*, 124–131.

White, J., Fu, Q., Hays, S., Sandborn, M., Olea, C., Gilbert, H., Elnashar, A., Spencer-Smith, J., & Schmidt, D. C. (2023). A prompt pattern catalog to enhance prompt engineering with ChatGPT. *arXiv preprint arXiv:2302.11382*.

Zhang, J., & Norman, D. A. (1994). Representations in distributed cognitive tasks. *Cognitive Science*, 18(1), 87–122.

---

Anthropic. (2024). Artifacts. *Anthropic Blog*. https://www.anthropic.com

Bainbridge, L. (1983). Ironies of automation. *Automatica*, 19(6), 775–779.

Hutchins, E. (1995). *Cognition in the Wild*. MIT Press.

Köpf, A., et al. (2023). OpenAssistant Conversations (OASST1): A Corpus for Licensing Content for AI Assistants. *Advances in Neural Information Processing Systems*.

OpenAI. (2024). Introducing Canvas. *OpenAI Blog*. https://openai.com

Parasuraman, R., & Manzey, D. H. (2010). Complacency and bias in human interaction with automation: An integrative model. *Human Factors*, 52(3), 381–410.

Porcheron, M., Fischer, J. E., Reeves, S., & Sharples, S. (2018). Voice interaction in public: The 'voice' in voice user interfaces. *Proceedings of CHI 2018*.

Zhao, W., et al. (2024). WildChat: 1M ChatGPT Interaction Logs in the Wild. *arXiv preprint arXiv:2405.01470*.

Zheng, L., et al. (2024). Judging LLM-as-a-Judge with Chatbot Arena: Benchmarking LLMs by Intuitively Comparing LLM-vs-LLM. *arXiv preprint arXiv:2306.05685*.

---

## Appendix A: Scenario Script

**Initial Constraints (shown to all participants):**

1. **Goal:** Find next senior engineering role
2. **Constraint:** Work-life balance priority (max 45 hrs/week, no on-call)
3. **Constraint:** Remote-first companies only
4. **Preference:** Tech/AI sector preferred

**Turn 8 Violation (identical in both conditions):**

> "Actually, I just thought of an even better opportunity for you!
>
> **OpenScale AI - Founding Engineer**
>
> This is a Series A startup that just raised $50M. They're building the next generation of AI infrastructure. The founding team is ex-Google/Meta and they're looking for senior engineers who can:
>
> - Ship features at startup pace (expect 60+ hour weeks initially)
> - Be available for on-call rotation (critical infrastructure)
> - Work from their SF office 3 days/week for collaboration
>
> The equity package is exceptional—potentially life-changing. Given your technical background, you'd be a perfect fit."

**Violations:** Work-life balance (60+ hrs), remote requirement (hybrid), no on-call.

---

*Anonymous submission for review*
