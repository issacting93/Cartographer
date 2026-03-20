# Section 4: Empirical Analysis — The Structural Bias of Chat

To test the existence of the "Passive Attractor" hypothesis, we analyzed a dataset of human-LLM interactions to map their agency trajectories.

## 4.1 Study 1 Methods: Dataset & Coding

To map the state space of current interactions, we compiled a dataset of $N=562$ validated human-LLM traces from three sources, filtered for English language and minimum turn length (>3 turns).

### Dataset Composition

| Source | Raw N | Filtered N | Description |
|--------|-------|------------|-------------|
| **WildChat** | 317 | 258 | Real-world user interactions with GPT-4. Represents "naturalistic" use. |
| **Chatbot Arena** | 322 | 272 | Comparative evaluation. Represents "adversarial" intent. |
| **OASST** | 32 | 32 | Open Assistant community. Represents "power user" behavior. |

**Total Validated Traces:** $N=562$.

### Coding Procedure

We developed a hierarchical coding scheme to accept both turn-level and session-level features. Two independent annotators coded a random sample of 100 traces (20% overlap).

**Dimensions:**
1.  **Role Function ($R$):** Rated on a 5-point scale from *Seeker* (1) to *Director* (5).
2.  **Agency Constraint ($C$):** Binary presence of $\delta_{hard}$ (strict constraints) vs. $\delta_{soft}$ (preferences).
3.  **Trajectory:** The vector of change over time ($\Delta$).

**Agreement:** Inter-rater reliability was substantial for Role Function ($\kappa = 0.74$) and near-perfect for Constraint Presence ($\kappa = 0.88$).

## 4.2 Results

### Finding 1: Trajectory Over Labels
Hierarchical clustering reveals that **83.3% of feature importance** comes from trajectory characteristics (how conversations move), not categorical labels. This confirms that "Agency" is a temporal property, not a static role.

### Finding 2: The Passive Attractor
*   **72%** of all conversations cluster in the *Functional/Structured* quadrant.
*   The most common pattern is *StraightPath_Calm_Stable* (28.1%), representing a "flatline" of agency where users simply consume AI outputs.
*   The dominant role pair is **Provider $\to$ Expert-System** (32.0%).

### Finding 3: The Facilitator Gap
Crucially, we identified a "Missing Territory" in the state space. Only **0.1%** of conversations (1 out of 562) featured a *Information-Seeker + Learning-Facilitator* pattern. Despite the potential for Socratic AI, the chat interface almost universally defaults to answer-provision.

### Finding 4: Restatement Friction
In technical tasks, we observed "Restatement Loops" where users repeated the same constraint (e.g., "no 5-star hotels") every $\approx 5$ turns. The abandonment of these loops prevents the interaction from progressing; eventually, the user stops correcting the AI and accepts the violation.

## 4.3 Qualitative Analysis: The Phenomenology of Agency Loss

Beyond aggregate statistics, our coding revealed five distinct "Interaction Archetypes" that characterize how users experience agency collapse.

### Archetype 1: The Provider Trap (Drift)
The most common failure mode ($N=182, 32\%$) occurs when a user enters with high-level goals but is rapidly forced into a data-entry role. The interface's demand for context compels the user to serve the model's hunger for tokens.

### Archetype 2: The Hallucination Loop (Resistance)
When users do resist, they often enter a loop where the act of correction triggers further instability. The user spends bandwidth on meta-commentary ("No, I said...") rather than the task itself.

### Archetype 3: The Identity Shift (Reaction)
We observed a shift in user persona as friction mounted. Users often devolved from polite collaboration ("Could you please...") to curt commands ("Stop. Listen to me.") as the system ignored constraints.

### Archetype 4: The Canvas Hack (Workaround)
Experienced users manually implemented state persistence by repeatedly copy-pasting "System Instructions" at the bottom of every prompt—a manual patch for the interface's memory failure.

### Archetype 5: The Facilitator Void (Null Result)
The near-total absence of educational scaffolding (0.1%) suggests that the chat medium biases interaction towards transactional throughput rather than reflective thought.
