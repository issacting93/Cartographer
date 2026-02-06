# Comprehensive Data Analysis Report (N=983)
**Date:** February 3, 2026
**Datasets:** WildChat, ChatbotArena, OASST (Filtered for Goal-Directed Tasks)

## 1. Executive Summary
This report details the findings from our Hybrid Taxonomy Analysis of 983 human-AI interactions. By combining LLM-based semantic classification (GPT-4o) with heuristic stability analysis, we have uncovered a structural "Agency Tax" that users pay when attempting complex tasks in chat interfaces.

**Headline Finding:** Users do not abandon failing tasks ("Agency Collapse": 2.8%); instead, they laboriously fix them ("Constraint Drift": 48.6%). This repair cost is not uniform—it spikes mainly in tasks requiring **Planning** and **Strict Constraints**.

---

## 2. Visualizing the Failure
We generated three key visualizations to verify our hypotheses.

### Figure 1: The Context Cliff (Drift vs. Time)
![Context Cliff](../paper/figures/context_cliff.png)
**Observation:** The probability of a constraint violation does not increase linearly with context length. Instead, it spikes **early (Turns 3-7)** and stays high.
**Implication:** This disproves the "Memory Capacity" hypothesis (that LLMs fail because they run out of context). It supports the "Structural" hypothesis: the system fails to "lock in" the task definition from the start, leading to immediate drift.

### Figure 2: The Drift Risk Matrix (Heatmap)
![Drift Heatmap](../paper/figures/drift_heatmap.png)
**Observation:** Drift is not random. It is clustered in the "Red Zone":
*   **Red Zone (Failure > 65%):** **Planning** Tasks + **Strict** Constraints.
*   **Blue Zone (Failure < 30%):** **Information Seeking** + **Flexible** Constraints.
**Implication:** Chat is a valid interface for the Blue Zone (Search/Vibes). It is invalid for the Red Zone (Engineering/Logistics). We simply keep trying to use it for the wrong quadrant.

### Figure 3: The Agency Tax Map (Effort vs. Repair)
![Agency Tax Map](../paper/figures/agency_tax_map.png)
**Observation:**
*   **Planning Tasks (Red Dots):** Show a steep slope. A short planning conversation requires disproportionately high repair.
*   **Info Seeking (Green Dots):** Flat slope. You can talk for hours without needing to "fix" the AI.
**Implication:** The "Agency Tax" is progressive. Complex tasks are not just harder; they are *exponentially* more expensive to manage in a chat UI.

---

## 3. Detailed Statistics

### 3.1 By Task Architecture
| Architecture | Count | Drift Rate | Risk Factor |
| :--- | :--- | :--- | :--- |
| **Planning** | 46 | **67.4%** | **1.39x** |
| **Analysis** | 131 | 56.5% | 1.16x |
| **Generation** | 414 | 53.1% | 1.09x |
| **Transformation** | 106 | 42.5% | 0.87x |
| **Info Seeking** | 277 | **37.2%** | **0.76x** |

**Interpretation:** "Planning" requires maintaining a global state (Step 1 to Step N). Chat logs bury this state, causing the high failure rate. "Info Seeking" is stateless, hence the success.

### 3.2 By Constraint Hardness
| Hardness | Count | Drift Rate | Risk Factor |
| :--- | :--- | :--- | :--- |
| **Strict** | 337 | **68.0%** | **1.40x** |
| **Mixed** | 296 | 48.0% | 0.99x |
| **Flexible** | 350 | **30.6%** | **0.63x** |

**Interpretation:** The "Paradox of Precision." The clearer the rule (e.g., "JSON only"), the more likely the system is to be perceived as failing. This suggests current LLMs are "Vibe Engines", not "Rule Engines."

---

## 4. Theoretical Synthesis (Link to CogSci)
These findings empirically validate the **Task-Constraint Architecture (TCA)** proposed in our CogSci work.

1.  **Epistemic Opacity:** The early spike in the *Context Cliff* confirms that users struggle to see if the AI "understands" the task until it errors.
2.  **Abstraction Collapse:** The failure of *Planning* tasks confirms that LLMs struggle to maintain high-level goals against the entropy of low-level token generation.
3.  **Agency Tax:** The *Scatter Plot* quantifies exactly how much cognitive labor is wasted on "repair loops" (Authority Inversion).

## 5. Conclusion for CUI Paper
We can confidently claim:
> "The failure of Agentic AI is not incorrectly predicted next tokens (hallucination); it is the inability of the Chat Interface to hold Task State (Drift). Our data shows this failure is structural, heavily penalized in complex tasks (Planning), and requires a massive 'Agency Tax' from users to manually bridge the gap."
