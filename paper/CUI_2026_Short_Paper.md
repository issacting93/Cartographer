# Making the Implicit Explicit: A Diagnostic Framework for Observing Grounding Failure in CUIs

## Abstract
Analyzing 1,383 human-LLM conversations containing 559 user-specified constraints, this work demonstrates that **69% are violated**—24% on the very first response—while only **17% are demonstrably followed**. The remaining 14% have ambiguous outcomes. We characterize this as a systematic **grounding failure**—what we term **Agency Collapse**—in which users cannot maintain a stable shared understanding with the system. Drawing on Conversation Analysis, we identify the **stateless architecture** of current Large Language Models (LLMs)—which requires reconstructing common ground from raw conversation history at each turn—as the structural cause of these failures. The median time-to-violation is just **1 turn**, and repair succeeds in only **1.0% of violation events**. Most strikingly, repair attempts occur in only **5.6% of constrained conversations**, with a repair density of just **0.4% of turns**—suggesting users have learned that correction is futile. We argue for a transition from stateless dialogue to **externalized, editable representations of shared commitments**, and we present **Atlas**, a visualization suite designed to make these implicit failures observable.

## 1. Introduction: The Visibility Gap
While Large Language Models (LLMs) have advanced the capabilities of conversational user interfaces (CUIs), they remain notoriously difficult to steer and debug. This difficulty arises from a **Visibility Gap**: conversational logs are inherently "flat," concealing the complex interactional state and grounding attempts that govern the dialogue. In this work, we present **Atlas**, a diagnostic framework designed to make this implicit state explicit. By transforming raw text into an **Interactional MultiDiGraph**, Atlas allows researchers to track **constraint outcomes**, measure repair attempts, and diagnose the structural root of **Agency Collapse**.

## 2. Methodology: Interactional Cartography
Our framework is powered by a two-stage analytic pipeline that transforms temporal dialogue into a structural graph of communicative acts:

1.  **Move Classification**: Turns are decomposed into a 16-move taxonomy (e.g., *Propose*, *Violate*, *Repair_Initiate*, *Escalate*) grounded in **Conversation Analysis (CA)** [5, 13, 14], with repair strategies classified following Ashktorab et al. [15].
2.  **Constraint Tracking**: We use a rule-based state machine to track verifiable instructions (e.g., "format as JSON") through a lifecycle: *proposed* → *acknowledged* → *violated* or *survived*. We measure time-to-violation, repair attempts, and outcomes.

Constraints are extracted via LLM classification (GPT-4o-mini), matched to violations using token overlap (Jaccard similarity, threshold 0.15), and classified into three outcome categories: *violated*, *followed* (acknowledged and never violated), or *ambiguous* (never violated but never acknowledged).

The corpus (N=1,383 graphs from N=2,577 conversations) aggregates interactions across a heterogeneous set of SOTA instruction-following models (e.g., GPT-4o, Claude 3.5) to identify baseline interactional patterns common to current conversational architectures.

## 3. The Atlas Suite: Metrics of Interactional Health
We define three primary metrics to quantify the "Interactional Cliff":
*   **Constraint Outcome**: We classify each constraint into three categories: *violated* (the AI demonstrably broke the rule), *followed* (the AI acknowledged and complied throughout), or *ambiguous* (never violated but never explicitly acknowledged—the AI may have coincidentally complied). Of 559 constraints: 386 (69%) violated, 93 (17%) followed, 80 (14%) ambiguous.
*   **Repair Density**: The ratio of user-initiated repair turns to total turns in constrained conversations. At **0.4%**, this reveals near-total abandonment of the repair mechanism.
*   **Patience**: The number of turns a user persists after first violation before abandoning. Abandoned conversations show a mean patience of **14.2 turns**; surviving conversations show **11.6 turns**.

## 4. Findings: The Anatomy of Grounding Failure
Atlas makes visible two structural pathologies that lead to interactional breakdown:

*   **The Abandonment Default**: Rather than entering prolonged repair sequences, users overwhelmingly abandon violated constraints. Only 15 of 270 constrained conversations (5.6%) contain any repair attempts at all, and successful repair occurs in just 1.0% of violation events (4/390). Users have effectively learned that repair is futile. The median violated instruction survives just **1 turn** before the AI breaks it (mean: 2.1 turns).
*   **The Immediate Failure Pattern**: 24% of constraint violations occur at Turn 0—the AI's very first response. A further 41% fail by Turn 1. This is not a gradual decay but a **structural inability to ground constraints at all**. Together, 65% of all violations happen within the first two turns.

## 5. Discussion & Design Implications
The near-absence of repair is perhaps the most alarming finding. In human-human conversation, repair sequences are natural and frequent [14]. The fact that users have abandoned repair in LLM dialogue—only 5.6% even attempt it, and it succeeds 1% of the time—suggests the conversational medium itself is broken for constraint governance. The 14% ambiguity rate (constraints neither violated nor acknowledged) further reveals that LLMs rarely make their compliance state observable, leaving users unable to distinguish silent compliance from silent failure.

Restoring agency requires moving from **implicit state** (hidden in dialogue) to **externalized grounding**:
*   **Decoupled Interaction Channels**: Separate the *Coordination Channel* (managing rules) from the *Execution Channel* (output).
*   **State Externalization**: Make constraints visible and directly editable, bypassing the pathogenic feedback loop of the conversational medium itself [5, 6].

**Limitations.** Constraint extraction relies on LLM classification without human validation; Jaccard matching (threshold 0.15) for linking violations to constraints may miss some matches. Mode violation analysis (Listener/Advisor/Executor) was attempted but found to be unreliable due to the AI mode detector's dependence on response length rather than intent, and is excluded from the headline findings.

## 6. Conclusion
By adopting the language of **grounding failure** and **survival analysis**, our work provides a rigorous framework for measuring the "Visibility Gap" in CUIs. The Atlas Suite offers a cartographic lens to move beyond "watching chat" toward **observing and governing interactional state.**

## References
[1] Amershi et al. 2019. CHI '19.
[5] Li et al. 2020. Sovite: Repairs in Task-Oriented Dialogs. UIST '20.
[12] Ouyang et al. 2022. InstructGPT. NeurIPS.
[13] WaitGPT. 2024. Monitoring and Steering LLM Agents. DIS '24.
[14] Schegloff et al. 1977. The Preference for Self-Correction. Language.
[15] Ashktorab et al. 2019. Resilient Chatbots: Repair Strategy Preferences for Conversational Breakdowns. CHI '19.
