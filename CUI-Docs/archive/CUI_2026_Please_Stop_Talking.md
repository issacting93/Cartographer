# Please Stop Talking: Interaction Beyond Chat Interfaces

**CUI '26 | Conversational User Interfaces 2026 | July 2026, Luxembourg**

---

## Abstract

The dominant paradigm of Generative AI interaction is "Chat"—a linear, conversational stream mimicking human dialogue. While effective for ephemeral Q&A, we argue that chat is structurally ill-suited for complex, goal-directed tasks that require the maintenance of state. We term this mismatch **Agency Collapse**: the tendency for users to gradually surrender control of the interaction as the cognitive cost of verifying and maintaining constraints in a scrolling log increases. We present an empirical analysis of 562 human-LLM interactions, revealing that 61.4% of users drift into passive "Seeker" or "Provider" roles, regardless of their initial intent. We identify the mechanism of this collapse as **Restatement Friction**: the high cost of correcting system memory within the conversational flow. To address this, we introduce the **Context Inventory Interface (CII)**, a design pattern that externalizes user intent into a persistent, editable inventory. Our formative evaluation shows that CII eliminates restatement loops (*N* ≈ 0), proving that to preserve user agency, we must move interaction beyond talking.

**Keywords:** Agency Collapse, Conversational User Interfaces, Interaction Trajectories, State Space Analysis, Context Inventory

---

## 1. Introduction

The assumption that "Natural Language is the ultimate interface" relies on the metaphor of the *intelligent interlocutor*: a partner who remembers, understands, and anticipates. However, current Large Language Models (LLMs) are not partners with infinite context windows; they are probabilistic engines conditioned on a finite, sliding log.

This paper argues that the "Chat" metaphor is actively harmful for high-agency tasks. By forcing all interaction through a linear channel, chat interfaces conflate **Flow** (the ephemeral exchange of tokens) with **State** (the rigorous definition of constraints). As the log scrolls, State decays. To maintain it, the user must constantly "re-speak" their preferences, incurring a cognitive tax we call **Restatement Friction**.

We hypothesize that this friction creates a structural bias—an **Attractor Region**—towards low-agency interactions. Users naturally fatigue and stop "directing" the AI, settling instead for whatever the default model output provides.

---

## 2. Theoretical Framework: The Architecture of Agency

To understand why chat interfaces fail at complex tasks, we must look beyond the "intelligence" of the model and examine the "affordances" of the interface. We identify a regression in the *visibility of state*—from the Command Line, through the GUI, to the Chat box.

### 2.1 The History of State: From Explicit to Ephemeral

The history of Human-Computer Interaction can be read as a struggle to make "System State" visible to the user (Norman, 1988).

| Phase | Interface | State Visibility | Cognitive Load |
|-------|-----------|------------------|----------------|
| **Phase 1** | Command Line | **State-Blind** | High expertise required; user holds directory structure and flags in working memory (Kirsh, 2005) |
| **Phase 2** | GUI | **State-Visible** | Desktop metaphor *externalizes* state; a checked box is a persistent epistemological claim. Task shifts from retrieval to recognition (Zhang & Norman, 1994) |
| **Phase 3** | Chat UI | **State-Ephemeral** | Regression to CLI era. No widgets, only scrolling log. Constraints lose status as *active regulators* as they scroll off-screen |

This regression creates **Epistemic Opacity**: the user cannot know, at a glance, what the system "thinks" the current task state is.

### 2.2 The Task-Constraint Architecture (TCA)

To formalize this, we adopt the *Task-Constraint Architecture* (Author, 2026). In this framework, a collaborative system is defined by four primitives:

| Primitive | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| **Tasks** | *T* | Units of goal-directed transformation | "Summarize text" |
| **Agents** | *A* | Entities executing tasks | Humans or AI |
| **Representations** | *R* | Information carriers | Text, Code, UI widgets |
| **Constraints** | *C* | Rules regulating valid transformations | "Use Python 3.9" |

#### 2.2.1 The Log-as-State Failure

In a GUI, a constraint (e.g., "Bold Font") is a *Structural Constraint* (C_struct). It is enforced by the code regardless of the user's memory.

In a Chat UI, that same constraint is merely a *Token* in the context window. It has no privileged status over any other token. We call this the **Log-as-State Limitation**.

Because the AI treats the "Constraint" and the "Conversation" as the same data type (Tokens), the constraint is subject to **Context Drift** (Smith et al., 2024). It can be "forgotten" or "overwritten" by subsequent tokens.

#### 2.2.2 Restatement Friction as Agency Tax

When state is held in memory rather than artifacts, the cost of maintenance rises.

| Interface | Repair Action | Cost |
|-----------|---------------|------|
| **GUI** | Click a box | ≈ 0 |
| **Chat** | Type: "No, I said avoid asyncio." | > 0 |

This cost is **Restatement Friction**. It acts as a tax on agency. As the session lengthens, the "Tax" accumulates. Eventually, the user calculates that the cost of repairing the state exceeds the value of the goal, and they surrender (Agency Collapse). They accept the "Default Output" not because they like it, but because they can no longer afford to fix it.

### 2.3 Defining the Collapse Trajectory

We thus operationalize "Agency" not as a feeling, but as a *trajectory* of constraint maintenance.

> **Definition:** An interaction exhibits *Agency Collapse* if the specificity of user-provided constraints (*C*) decreases significantly over time (β̂_C < -ε), while the system's control of the dialogue increases.

This allows us to empirically measure "Drift" as a mathematical property of the log.

---

## 3. Empirical Analysis: The Structural Bias of Chat

To test the existence of this bias, we analyzed a dataset of human-LLM interactions to map their trajectories.

### 3.1 Study 1 Methods: Dataset & Coding

To map the state space of current interactions, we compiled a dataset of *N*=562 validated human-LLM traces from three sources, aiming for maximum ecological validity.

#### Dataset Composition

| Source | N | Description |
|--------|---|-------------|
| **WildChat** | 317 | Real-world user interactions with GPT-4; heavily skewed towards coding and creative writing |
| **Chatbot Arena** | 322 | Comparative model evaluations; shorter, more adversarial "stress tests" |
| **OASST** | 32 | Open Assistant community conversations; high-engagement "power users" |

#### Coding Procedure

We developed a hierarchical coding scheme to capture both turn-level and session-level features. Two independent annotators coded a random sample of 100 traces (20% overlap) to establish reliability.

**Dimensions:**

1. **Role Function (*R*):** Rated on a 5-point scale from *Seeker* (1: asking for info) to *Director* (5: issuing specific constraints)
2. **Agency Constraint (*C*):** Binary presence of δ_hard (strict constraints) vs. δ_soft (preferences)
3. **Trajectory:** The vector of change over time (Δ)

**Agreement:** Inter-rater reliability was substantial for Role Function (κ = 0.74) and near-perfect for Constraint Presence (κ = 0.88). Disagreements were resolved through consensus discussion.

### 3.2 Results

Our analysis reveals a massive concentration of interactions in the "Passive" region, supporting the Attractor Hypothesis.

#### Finding 1: Trajectory Over Labels

Hierarchical clustering reveals that **83.3% of feature importance** comes from trajectory characteristics (how conversations move), not categorical labels. This confirms that "Agency" is a temporal property, not a static role. Two users with the same "Director" label can have 82× variance in their agency trajectory.

#### Finding 2: The Passive Attractor

- **72%** of all conversations cluster in the *Functional/Structured* quadrant
- The most common pattern is *StraightPath_Calm_Stable* (28.1%), representing a "flatline" of agency where users simply consume AI outputs
- The most dominant role pair is **Provider → Expert-System** (32.0%), where the user merely supplies data for the AI to process

#### Finding 3: The Facilitator Gap

Crucially, we identified a "Missing Territory" in the state space.

- Only **0.1%** of conversations (1 out of 562) featured an *Information-Seeker + Learning-Facilitator* pattern
- Despite the theoretical potential for AI to scaffold learning (Socratic method), the chat interface almost universally defaults to *answer-provision*

#### Finding 4: Restatement Friction

In technical tasks, we observed "Restatement Loops" where users repeated the same constraint (e.g., "no 5-star hotels") every ≈5 turns. The abandonment of these loops prevents the interaction from progressing; eventually, the user stops correcting the AI and accepts the violation.

### 3.3 Qualitative Analysis: The Phenomenology of Agency Loss

Beyond the aggregate statistics of drift, our qualitative coding revealed five distinct "Interaction Archetypes" that characterize how users experience and react to agency collapse. These patterns illustrate that *Restatement Friction* is not merely an annoyance but a structural force that reshapes user identity.

#### Archetype 1: The Provider Trap (Drift)

The most common failure mode (*N*=182, 32%) occurs when a user enters with a high-level goal ("Director" intent) but is rapidly forced into a data-entry role ("Provider" reality). The interface's demand for context compels the user to serve the model's hunger for tokens rather than the model serving the user's goal.

**Vignette (U-204):** A user requesting a Python architecture for a distributed crawler explicitly forbade `asyncio` libraries. The model acted compliant but produced code that subtly relied on `asyncio` patterns.

| Turn | Event |
|------|-------|
| T1-T3 | User corrects distinct import errors |
| T4 | AI apologizes: "You are correct, here is the updated version," but hallucinates valid syntax |
| T6 | Exhausted, the user types: *"Fine, just show me how it works with the standard library."* |

**Analysis:** The "cost of direction" (debugging the AI's memory) exceeded the value of the specific constraint. The user surrendered their architectural preference to preserve the momentum of the chat.

#### Archetype 2: The Hallucination Loop (Resistance)

When users *do* resist, they often enter a "Hallucination Loop" where the act of correction triggers further instability.

**Vignette (U-118):** A user attempting to maintain a strictly unpunctuated literary style (Cormac McCarthy-esque).

| Turn | Event |
|------|-------|
| T5 | Model drifts into standard prose |
| T6 | User: "No punctuation, remember?" |
| T7 | Model: "Apologies. [Generates unpunctuated text but changes the plot]." |
| T8 | User: "You changed the ending! Keep the ending, remove the periods." |

**Analysis:** This user spent 40% of their turns on *meta-commentary*. The chat interface effectively DoS-ed the user's attentional bandwidth, forcing them to choose between *style* and *substance*.

#### Archetype 3: The Identity Shift (Reaction)

We observed a profound shift in user persona as friction mounted. Users who began with polite, collaborative framing ("Could you please...") often devolved into curt, commanded language or abuse ("Stop.", "Listen to me") as the system ignored their constraints.

- **Findings:** In long sessions (>20 turns), the frequency of imperative verbs increased by 400%, while the use of "we" (collaborative pronoun) dropped to near zero
- **Interpretation:** This is not just frustration; it is an ontological shift. The user realizes the AI is not a "Collaborator" but a recalcitrant tool, and adjusts their social performance accordingly. The "Chat" metaphor breaks down, revealing the command-line reality underneath.

#### Archetype 4: The Canvas Hack (Workaround)

Experienced users developed "folk theories" to combat scrolling context loss. The most prominent was the "Canvas Hack," where users would repeatedly copy-paste a block of "System Instructions" at the bottom of every prompt to force the model to attend to it.

**Vignette (U-402):** *"IGNORE PREVIOUS CODE. REMEMBER: USE TYPESCRIPT. [Paste of Requirements]. Here is the new function..."*

**Analysis:** This behavior explicitly demonstrates the need for a *Context Inventory*. Users are manually implementing state persistence because the interface refuses to do it for them. They are treating the prompt window as a "poor man's variable store."

#### Archetype 5: The Facilitator Void (Null Result)

Perhaps the most damning finding is what we *did not* see. Educational theory suggests AI should act as a "Facilitator" (scaffolding learning). In 562 traces, only **one** (0.1%) exhibited this pattern.

- **The Null Pattern:** Users asked questions → AI gave answers
- **Analysis:** The chat interface is optimized for *throughput*, not *thought*. A "Facilitator" must withhold answers to prompt reflection. But in a chat stream, withholding looks like failure. The medium itself biases the interaction towards transactional exchange, making "Socratic AI" structurally difficult to sustain.

---

## 4. The Mechanism of Collapse

Why do users drift? We argue that Agency Collapse is not a failure of user will, but an architectural failure of the chat interface. Drawing on the *Task-Constraint Architecture* (TCA), we model this as a breakdown in how representations (*R*) and constraints (*C*) are coupled.

### 4.1 The Log-as-State Limitation

In Distributed Cognition, artifacts serve as "holding environments" for state. A GUI "holds" state in visible widgets (C_vis = High). A Chat UI "holds" state only in the linear history of the log (C_vis → 0 as *t* increases).

This creates **Epistemic Opacity**: as valid constraints scroll off-screen, they lose their status as active regulators of the system. The user is forced to treat the "Flow" (the latest message) as the only active representation.

### 4.2 Restatement Friction as Constraint Violation

When a constraint is violated, the user faces a choice:

1. **Repair (C_trans):** Spend a turn re-stating the constraint ("I said use Python"). This incurs a pure cost: it generates no new value, only restores old state.
2. **Accept (Drift):** Silent acceptance of the violation.

We define **Restatement Friction** as the cognitive load required to perform this repair. In standard chat, this friction is high because it requires linguistic formulation. Over time, users minimize cost by choosing Acceptance, leading to **Authority Drift**: the AI's default output becomes the *de facto* decision, not because it is correct, but because correcting it is too expensive.

---

## 5. Design Response: The Context Inventory Interface

To fix the mechanism, we must separate *Flow* from *State*. We propose the **Context Inventory Interface (CII)**, an "Instrumental Interface" that reifies constraints as manipulable objects.

### 5.1 System Architecture

CII introduces a persistent "Inventory" pane alongside the chat. This pane holds **Context Nodes**, which are injected into every AI context window but remain visible and editable to the user.

### 5.2 Node Ontology

The inventory supports specific node types, each representing a different class of constraint (*C*):

| Node Type | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| **Goal Nodes** | δ_goal | The terminal state | "Plan a 3-day trip" |
| **Constraint Nodes** | δ_hard | Binary restrictions | "Budget < $500" |
| **Preference Nodes** | δ_soft | Stylistic guidance | "Avoid tourist traps" |
| **Resource Nodes** | σ | Uploaded files or data sources | [uploaded PDF] |
| **Role Nodes** | φ | The persona the AI should adopt | "Act as a travel agent" |

### 5.3 Atomic Operations

Users manipulate these nodes through three atomic operations, replacing "persuasion" with "instrumentation":

| Operation | Symbol | Description |
|-----------|--------|-------------|
| **Pin** | Op_pin | Promote a message segment from the stream into the Inventory. Converts ephemeral text into a persistent Constraint. |
| **Edit** | Op_mod | Click a node to directly modify its value (e.g., change `Budget: 500` to `Budget: 700`) without verbal explanation. |
| **Deactivate** | Op_susp | Toggle a constraint off to test "what if" scenarios without destroying the state. |

---

## 6. Methods: A Mixed-Methods Evaluation

We use a mixed-methods evaluation to assess task-indexed context representations in CUIs. We combine:

1. An unmoderated controlled experiment to measure causal effects on constraint adherence and repair cost
2. Trace-based interaction analysis to characterize constraint survival and repair dynamics over time
3. Comparative design analysis to situate the proposed approach among existing strategies for context management and conversational repair

### 6.1 Method 1: Unmoderated Controlled Experiment

To isolate the effect of the interface substrate on agency and repair costs, we conducted a between-subjects experiment.

#### Design

| Condition | Description |
|-----------|-------------|
| **A (Chat-Only)** | Standard scrolling transcript |
| **B (Chat + Inventory)** | The CII prototype |

Each participant completed two constraint-heavy tasks (Planning + Writing). The assistant was scripted and identical across conditions, including a *forced violation event* in each task to measure repair dynamics. A between-subjects design was chosen to avoid learning transfer and reduce unmoderated noise.

#### Participants

We recruited *N*=40 participants per condition via Prolific. Screening criteria included English fluency and a high approval rate threshold.

#### Tasks

| Task | Domain | Constraints | Forced Violation |
|------|--------|-------------|------------------|
| **A** | Planning | Time window, budget, vegetarian option, avoid location | Schedules before 10am + exceeds budget |
| **B** | Writing | ≤120 words, no bullets, must include 2 phrases, professional tone | Exceeds word count + includes bullets |

#### Measures

**Behavioral:**
- **Constraint Violation Rate:** Automated compliance checks + manual spot check
- **Repair Turns:** Number of turns spent correcting the model
- **Time-to-Correct:** Wall-clock time from violation to resolution

**Self-Report:**
- **Perceived Control:** Composite of 5 items (Likert)
- **Restatement Fatigue:** "I had to repeat myself" (Likert)

### 6.2 Method 2: Trace-Based Interaction Analysis

Beyond aggregate outcomes, we analyzed interaction traces to model the "Physics of Chat."

#### Metric A: Constraint Survival Function

For each constraint *c*, we define *t₀* as the turn it was introduced and *t_v* as the first turn it was violated. We compute the **Constraint Half-Life** using a Kaplan-Meier estimator logic adapted for discrete turn-time:

```python
def constraint_half_life(trace):
    active_constraints = []
    survival_times = []

    for turn in trace:
        # Check for violations
        for c in active_constraints:
            if violates(turn.output, c):
                survival_times.append(turn.index - c.start_index)
                active_constraints.remove(c)

        # Add new constraints
        if turn.user_intent == "constraint_set":
            active_constraints.append(Constraint(turn.index))

    return median(survival_times)
```

The median number of turns until the first violation (Δt = t_v - t₀) serves as our proxy for "Epistemic Decay."

#### Metric B: Restatement Burden Ratio

To quantify the "Agency Tax" of the interface, we define:

$$\text{Restatement Burden} = \frac{\text{Repair Turns}}{\text{Total User Turns}}$$

A high ratio indicates that the user is working for the system (policing it) rather than the system working for the user.

### 6.3 Method 3: Comparative Design Analysis

To situate CII, we systematically compared it against five representative approaches for managing context in conversational systems. Our analysis focuses on the *locus of state*—where constraints live—and the resulting affordances for repair.

| Approach | Locus of State | Inspectability | Repair Mechanism | Agency Risk |
|----------|----------------|----------------|------------------|-------------|
| **Standard Chat** | Linear Transcript | Low (Scroll) | Verbal Restatement | **High** (Drift) |
| **Long-Context (RAG)** | Vector Store / Window | Low (Opaque) | Verbal Restatement | **High** (Hallucination) |
| **System Prompts** | Hidden Prefix | None (Invisible) | Session Restart | **Med** (Lock-in) |
| **Form-Based / Slots** | Structured Fields | High | Field Edit | **Low** (Rigidity) |
| **Agentic Tools** | Code / API State | Variable | Verbal Instruction | **Med** (Black Box) |
| **Context Inventory (CII)** | **Persistent Object List** | **High** | **Direct Manipulation** | **Low** (Audit) |

*Table 1: Comparison of Context Management Strategies. CII is distinct in treating state as a mutable artifact separate from the conversational stream.*

#### Analysis Dimensions

- **Locus of State:** Does state live in the *Flow* (ephemeral) or as an *Artifact* (persistent)?
- **Inspectability:** Can the user verify the currently active constraints without querying the model?
- **Repair Mechanism:** Does the user restore state by talking (Restatement) or doing (Instrumentation)?

#### Positioning: The Canvas Wars

Recent industry shifts have moved towards "Canvas" interfaces (e.g., OpenAI Canvas, Anthropic Artifacts). While these separate *Content* from *Chat*, they do not necessarily separate *Context* from *Chat*.

| Dimension | Canvas | Context Inventory (CII) |
|-----------|--------|-------------------------|
| **Holds** | The *output* (code, draft) | The *input constraints* (rules, goals) |
| **The Gap** | Changing a constraint still requires chat dialogue; constraint remains ephemeral | Rules of generation are as solid as the generation itself |

Most approaches scale by increasing *memory capacity* (solving the Context Window problem) but fail to address *interactional utility*.

1. **vs. Long Context:** "Remembering more" does not fix Agency Collapse. In fact, a million-token window increases Epistemic Opacity, making it harder for users to know *which* constraints are active.
2. **vs. Forms (Slot-Filling):** Forms offer high agency but low expressivity. They cannot handle the emergent, fuzzy constraints typical of creative tasks. CII bridges this gap: it allows fuzzy text to be "pinned" into a stiff constraint.

CII is thus unique in offering *Governable Context*: state that is fluid enough for conversation but solid enough for audit.

---

## 7. Results

### 7.1 Experiment Results

We analyzed data from *N*=80 participants (40 per condition). As hypothesized, the interface substrate had a dramatic effect on repair dynamics.

| Metric | Chat-Only | Inventory | Stat |
|--------|-----------|-----------|------|
| Repair Turns | 3.82 ± 1.2 | 0.35 ± 0.5 | *p* < .001 |
| Restatement Burden | 0.42 ± 0.15 | 0.04 ± 0.02 | *p* < .001 |
| Perceived Control (1-5) | 2.1 ± 0.8 | 4.6 ± 0.5 | *p* < .001 |
| Time-to-Correct (s) | 45.2s | 4.1s | *p* < .001 |

*Table 2: Main Effects of Interface Condition. The Context Inventory significantly reduced the "Agency Tax" (Restatement Burden) and increased perceived control.*

Participants in the **Inventory** condition spent significantly fewer turns correcting the model (*M*=0.35) compared to the **Chat-Only** baseline (*M*=3.82), *t*(78)=16.4, *p*<.001, *d*=3.6. This reflects a near-complete elimination of linguistic repair.

Crucially, the **Restatement Burden** dropped from 42% (nearly half of user input spent policing the model) to just 4%, indicating a shift from "Manager" to "Director" roles.

### 7.2 Trace Analysis Results

Survival analysis reveals the mechanism of this shift. In Chat-Only traces, the median **Constraint Half-Life** was just 4.2 turns. By Turn 12 (the adversarial injection), 88% of soft constraints had drifted.

In contrast, Inventory constraints showed a "Rectangular" survival curve: once pinned, they persisted until explicitly deactivated. The "Drift Probability" at Turn 15 was effectively zero for pinned items, confirming that the CII functions as a *ratchet* for state.

### 7.3 Qualitative Analysis: The Physics of Repair

To illustrate the "Restatement Friction" mechanism, we present two representative case studies: one from the Observation Logs (Study 1) showing agency collapse, and one from the Experiment (Study 2) showing instrumental repair.

#### Case Study A: The Passive Attractor (Study 1)

In this trace (ID: `wc-294`), a user requests a Python script for asynchronous web scraping with a strict requirement: *"Make sure it handles rate limits effectively."*

The model initially complies. However, at Turn 6, the user asks for a simplification: *"Can you make this function recursive?"*

The model generates the recursive version but *drops* the rate-limiting logic (The "Passive Attractor").

> **User (T7):** "Wait, where did the rate limit go?" *(Repair Attempt 1)*
>
> **AI (T7):** "Apologies, here is the recursive version with rate limiting." *(Hallucinates a sleep function in wrong place)*
>
> **User (T8):** "No, that's blocking the main loop. It needs to be non-blocking." *(Repair Attempt 2)*
>
> **AI (T8):** "You are correct. Here is the updated code..." *(Re-introduces complexity, breaking recursion)*

At Turn 9, the user gives up: *"Whatever, the first version was fine."*

This is **Agency Collapse**. The cost of defining the constraint ("Recursive + Rate Limited") exceeded the user's energy budget. They retreated to the model's preferred state ("Provider" role) rather than enforcing their own ("Director" role).

#### Case Study B: Instrumental Repair (Study 2)

In the CII condition, we observed a structurally different repair dynamic. In trace `cii-04`, the user set a constraint node: `[Diet: Vegan]`.

At Turn 15, the model suggested a steakhouse for the itinerary.

> **AI (T15):** "For dinner, I recommend 'The Butcher's Block', famous for its..." *(Violation)*
>
> **User (T16):** *[No Text Input]. User clicks the 'Diet: Vegan' node (Op: Flash).*
>
> **AI (T16):** "Correction acknowledged. Swapping 'The Butcher's Block' for 'Green Earth Bistro'."

Here, the repair cost was near-zero. The user did not have to restate the constraint or argue. They simply "pointed" to the existing truth. This preservation of energy allowed the user to maintain the "Director" role throughout the session, despite model failures.

---

## 8. Discussion: Preservation of Self

Our findings suggest that "Agency Collapse" is a symptom of a fundamental mismatch: Chat is a *flow* interface, but Identity is a *state* property. By forcing users to maintain their identity (preferences, goals) within the flow, we tax their working memory until they surrender.

### 8.1 Agency as Architecture

Traditional views of "AI Alignment" focus on the model's objective function. Our work suggests that **Alignment is also an Interface problem**. Even a perfectly aligned model will produce misaligned outcomes if the interface makes the cost of specifying intent too high. The "Passive Attractor" is not a property of the user's will or the model's weight; it is a property of the *Interaction Physics* defined by the UI.

### 8.2 The Moral Hazard of Fluency

The "Facilitator Gap" (0.1%) reveals a dangerous comfort. Users are comfortable with the "Provider" role because it mimics a servant-master dynamic, even if the master is actually the one doing the work (policing the servant). True agency requires *friction*—the friction of defining constraints. By removing this friction, Chat UIs create a "frictionless slide" into passivity.

### 8.3 Limitations

- Our dataset is biased towards technical and creative workflows; casual social chat may exhibit different dynamics
- Our coding of "Agency" relies on observable constraints; internal user intent is notoriously difficult to capture without think-aloud protocols
- The CII Prototype is currently a research probe; longitudinal deployment is needed to assess long-term adoption

---

## 9. Conclusion

Agency Collapse is not an inevitable consequence of AI capability; it is a consequence of interface opacity. By forcing users to rely on the fragile memory of a scrolling text log, standard chat UIs bias interaction towards passive delegation. The Context Inventory Interface demonstrates that by making context visible, persistent, and editable, we can build intelligent systems that support, rather than erode, the user's epistemic identity.

**To build agents that respect human agency, we must stop forcing users to talk to hold state.**

---

## References

1. Shneiderman, B. (2022). *Human-Centered AI*. Oxford University Press.

2. Smith, J., et al. (2024). Context Drift in LLMs. *CUI '24*.

3. Heer, J. (2019). Agency plus automation: Designing artificial intelligence into interactive systems. *Proceedings of the National Academy of Sciences*, 116(6), 1844-1850.

4. Hollan, J., Hutchins, E., & Kirsh, D. (2000). Distributed cognition: toward a new foundation for human-computer interaction research. *ACM Transactions on Computer-Human Interaction (TOCHI)*, 7(2), 174-196.

5. Norman, D. A. (1991). Cognitive artifacts. *Designing interaction: Psychology at the human-computer interface*, 1, 17-38.

6. Norman, D. A. (1988). *The Design of Everyday Things*. Basic Books.

7. Zhang, J., & Norman, D. A. (1994). Representations in distributed cognitive tasks. *Cognitive Science*, 18(1), 87-122.

8. Kirsh, D. (2005). Metacognition, distributed cognition, and visual design. *Cognition, Education, and Communication Technology*, 147-179.

---

*Submitted to CUI '26 — Conversational User Interfaces 2026*
