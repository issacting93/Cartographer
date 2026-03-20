# Section 7: Methods — A Mixed-Methods Evaluation

To evaluate the impact of interface architecture on agency, we employ a mixed-methods strategy combining large-scale interaction analysis with a controlled user study and comparative design review.

| Method | Source / Tool | Purpose | Status |
|--------|---------------|---------|--------|
| **1. Log Analysis** | WildChat (N=1M) + LMSYS (N=1M) | Show ecological validity of "Collapse" | Analyzed |
| **2. Maze Study** | Maze (N=80) | Test "Visibility" and "Repair Cost" | Protocol Ready |
| **3. Design Analysis** | Comparison Matrix | Position CII vs. Canvas/RAG | Complete |

---

## 7.1 Method 1: Log Analysis (Ecological Validity)

We analyze two large-scale public datasets to demonstrate that "Agency Collapse" is a general phenomenon, not an artifact of a specific model or prompt.

### Datasets
1. **WildChat:** 1M real-world ChatGPT interactions (arXiv:2405.01470). Represents "naturalistic" use.
2. **LMSYS-Chat-1M:** 1M conversations across multiple models (arXiv:2309.11998). Represents "adversarial/comparative" use.

### Metrics
We define three quantitative metrics to detect agency loss in logs:

#### Metric A: Constraint Yield
The percentage of conversations containing at least one explicit constraint (e.g., "no bullets," "under 500 words").
*   *Purpose:* Establishes the prevalence of high-agency intent.
*   *Operationalization:* Regex matching for deontic markers ("must", "don't", "only") + constraint keywords.

#### Metric B: Constraint Survival (The "Half-Life")
We model the longevity of constraints using Kaplan-Meier survival curves.
*   *Definition:* Survival time $\Delta t = t_{violation} - t_{introduction}$.
*   *Outcome:* The **Constraint Half-Life** (median turns until violation).
*   *Hypothesis:* Chat interfaces exhibit a short half-life (< 5 turns) due to context drift.

#### Metric C: Restatement Burden
The ratio of user effort spent repairing state vs. advancing the task.
*   *Formula:* $\text{Burden} = \frac{\text{Repair Turns}}{\text{Total User Turns}}$
*   *Outcome:* A high burden indicates the user is serving the system (maintenance) rather than the system serving the user.

---

## 7.2 Method 2: Maze User Study (Causal Mechanism)

To isolate the interface mechanism (State Visibility), we conduct an unmoderated experiment using **Maze**, comparing two interface conditions on identical tasks.

### Conditions
*   **Condition A (Chat-Only):** Standard scrolling transcript.
*   **Condition B (Chat + CII):** Chat with "Context Inventory" sidebar.

### Task 1: The "State Audit" (Testing Epistemic Opacity)
*   **Scenario:** Participants enter a conversation mid-stream.
*   **Prompt:** "You are continuing this chat. What are the active constraints right now?"
*   **Measure:** Accuracy of identifying active constraints vs. hallucinations.
*   **Hypothesis:** CII participants will have significantly higher accuracy and faster retrieval time (click vs. scroll).

### Task 2: The "Forced Repair" (Testing Restatement Friction)
*   **Scenario:** The assistant outputs a message that violates strict constraints (Length > 120 words, includes bullets).
*   **Task:** "Fix the output so it meets all constraints."
*   **Chat-Only Action:** User must type a correction message.
*   **CII Action:** User clicks constraint nodes to "flash" them and hits regenerate.
*   **Measure:** Time-to-fix, number of actions (clicks/keystrokes), and success rate.

### Sample & Recruitment
*   **N:** 80 participants (40 per condition).
*   **Platform:** Prolific (pre-screened for English fluency).
*   **Analysis:** T-tests for time/accuracy differences; Chi-square for success rates.

---

## 7.3 Method 3: Comparative Design Analysis

We systematically position the Context Inventory (CII) against four dominant paradigms to show distinct affordances.

### Dimensions of Analysis
1.  **Locus of State:** Where does the "Constraint" live? (Flow vs. Artifact)
2.  **Inspectability:** Can the user see the rule without asking?
3.  **Repair Mechanism:** How does the user fix a violation? (Restate vs. Reconfigure)

### The "Canvas" Distinction
A key contribution is distinguishing CII from "Canvas" interfaces (e.g., OpenAI Canvas).
*   **Canvas:** Holds the **Output** (the draft, the code).
*   **CII:** Holds the **Input** (the constraints, the prompt parameters).
*   *Critique:* Current Canvas tools allow editing the *text*, but changing the *logic* (e.g., "Use Python 3.9") still requires chat. CII argues for "Governable Context."
