# Making the Implicit Explicit: Diagnosing Grounding Failure and Agency Collapse in Conversational User Interfaces

## Abstract

Conversational user interfaces built on large language models are linguistically fluent but interactionally fragile. Drawing on Conversation Analysis and Structured Discourse Theory (Grosz & Sidner [6]), we argue that the **unstructured state** of current LLMs — which flattens intentional structure into a linear token sequence — structurally undermines the two mechanisms that sustain shared understanding in human dialogue: **grounding** (the process of establishing mutual evidence of understanding) and **repair** (the self-righting mechanism for addressing misunderstanding). We term this structural condition **Implicit State Pathology** and predict that it leads to high constraint violation, early failure, and the behavioral near-absence of repair — a pattern we call **Agency Collapse**.

To test these predictions, we present **Atlas**, a diagnostic framework that operationalizes grounding and repair as computable metrics over conversation graphs. Applying Atlas to 1,383 human–LLM conversations containing 559 user-specified constraints, we find that **69% of constraints are violated** — 24% on the AI's very first response — while only **17% are demonstrably followed**. The remaining **14% have ambiguous outcomes**: the AI neither violated nor acknowledged them, leaving users unable to distinguish compliance from silent failure. Repair (defined as immediate compliance) succeeds in only **1.0% of violation events**, and repair attempts are behaviorally rare, occurring in just **5.6% of constrained conversations**. We argue that restoring conversational agency requires a transition from unstructured state to **externalized, editable representations of shared commitments**.

## 1. Introduction

Conversational user interfaces (CUIs) built on large language models have expanded the scope of what users can attempt through dialogue. Yet a persistent problem shadows this expansion: users struggle to steer these systems reliably. Instructions are forgotten, constraints are violated, and attempts at correction frequently fail. This is typically framed as a problem of model capability — a matter of better training, longer context, or improved prompting. We argue instead that it is a problem of **conversational interaction**: a structural failure of the grounding process that sustains shared understanding in any dialogue.

The difficulty lies in what we call the **Visibility Gap**. Conversational logs are inherently "flat" — a linear sequence of messages that conceals the interactional state governing the exchange. Whether a constraint has been understood, whether it is currently being followed, and whether a repair attempt succeeded are all invisible to both the user and the researcher examining the transcript. The conversational medium itself provides no mechanism for observing or governing this state.

This paper makes three contributions. First, it reframes a familiar problem in conversational AI—poor user steering—not only as a failure of model capability, but as a failure of **commitment maintenance** in the interaction itself. Second, it introduces **Atlas**, a diagnostic framework for tracking the lifecycle of user commitments in conversation, including whether constraints are made active, maintained, violated, or repaired. Third, it provides initial corpus evidence that current LLM chat interfaces often offer weak support for commitment legibility and repair, motivating interface designs that externalize conversational commitments into persistent, inspectable state rather than leaving them embedded in the transcript alone. This contribution is deliberately narrower than claiming a complete theory of all conversational failure; instead, it offers a measurable interactional lens on how grounding and repair deficits accumulate into degraded user steering.

These contributions address the CUI 2026 theme of **"Agency and Identities."** We argue that because the medium relies on unstructured state, agents cannot maintain a legible identity as collaborative partners, forcing users into the dispreferred role of "exhausted auditor" [15].

## 2. Related Work

Successful dialogue depends on more than fluent turn-taking. Classic work on grounding and discourse structure argues that interlocutors must establish enough mutual evidence of understanding to proceed, and that this process is sustained through repair and through an evolving structure of shared purposes and attentional focus [3, 6]. For conversational systems, this means that interaction quality cannot be reduced to output correctness alone; it also depends on whether users can establish, monitor, and restore shared commitments across turns. Recent work in human–AI collaboration reinforces this point by treating common ground as a central requirement for coordinated action rather than a secondary conversational nicety [20].

Recent NLP work shows that large language models are weak at precisely these grounding behaviors. Shaikh et al. [22] find that, compared to humans, LLMs generate fewer grounding acts and instead often appear to presume common ground rather than actively constructing it. Extending this line of work, Shaikh et al. [19] analyze human–LLM interaction logs and show systematic asymmetries in grounding behavior: LLMs are substantially less likely than humans to initiate clarification or provide follow-up requests, and early grounding failures predict later interaction breakdowns. Our work builds on this literature, but shifts the unit of analysis from individual grounding acts to the lifecycle of user commitments: whether constraints are introduced, stabilized, maintained, violated, and repaired over time.

A parallel line of work examines repair and conversational breakdown in HCI. Recent reviews [17] show that repair strategies in spoken and conversational systems have been studied across multiple disciplines, with attention to both system-side and user-side repair mechanisms. Our contribution differs in emphasis. Rather than proposing a new repair strategy taxonomy, we ask a more prior question: under what conditions do conversational interfaces fail to support repair at all because user commitments were never clearly grounded or made interactionally legible in the first place?

The dialogue-systems literature provides an important contrast. In task-oriented dialogue, dialogue state tracking (DST) has long been treated as essential infrastructure because systems must maintain persistent representations of goals, slots, and user constraints across turns [14]. Recent survey work continues to describe DST as a crucial component of task-oriented systems, and newer LLM-based approaches still improve performance by explicitly recovering or structuring state, for example through function calling [16]. When interaction depends on maintaining commitments over time, some form of explicit state representation remains necessary. Our extension is that, in open-ended CUIs, such state must not only exist for the model, but must also become legible to the user.

A newer design thread in HCI suggests how this legibility might be achieved. Do et al. [23] show that grounding-oriented interface designs can reduce cognitive load and improve task performance relative to ungrounded natural-language interfaces. Likewise, Vaithilingam et al. [21] argue that AI systems increasingly rely on “intent specifications” or grounding documents—persistent artifacts such as memory lists or project rules—to coordinate behavior with users over time. Our work contributes empirical motivation for that shift by showing what users lose when commitments remain implicit in the transcript alone.

### Research Gap

Across these literatures, three things are already known: LLMs underproduce grounding behaviors, repair is central to usable conversational systems, and explicit state matters when systems must maintain commitments across turns. What remains underdeveloped is a diagnostic account of how user-issued constraints behave as interactional objects in real human–LLM conversations: when they become active, when they fail, whether repair occurs, and whether users can tell what status those commitments currently have. This work addresses this gap by operationalizing **commitment maintenance** and **commitment legibility** as measurable properties of conversational interaction.

## 3. Method: The Atlas Framework

### 3.1 Corpus

Our corpus comprises 2,577 conversations drawn from publicly available human–LLM interaction datasets, processed into 1,383 analyzable conversation graphs. The conversations span a heterogeneous set of state-of-the-art instruction-following models (including GPT-4o, Claude 3.5, and others) across diverse tasks and domains. This heterogeneity is deliberate: we aim to identify baseline interactional patterns common to current conversational architectures, not to evaluate any single model. This is secondary analysis of existing conversation logs — no human participants were recruited for this study.

### 3.2 Analytic Pipeline

Atlas transforms temporal dialogue into a structural graph of communicative acts through a two-stage pipeline:

**Move Classification.** Each turn is decomposed into communicative moves using a 19-type taxonomy grounded in CA [12, 2, 11]. The taxonomy distinguishes three levels of **grounding evidence** following Clark and Brennan [3]: *understanding demonstrations* (the AI restates or paraphrases the constraint), *acknowledgment tokens* (procedural markers such as "Sure" or "Here is"), and *unmarked compliance* (output that may comply but provides no linguistic evidence of understanding). Repair moves are classified by **repair organization** following Schegloff et al. [12]: self-initiated self-repair (SISR), other-initiated self-repair (OISR), and other-initiated other-repair (OIOR). Classification uses a hybrid approach (deterministic pattern matching with LLM fallback for violation detection).

**Constraint Tracking.** A rule-based state machine tracks verifiable user instructions (e.g., "respond only in JSON," "do not use bullet points") through a lifecycle: *stated* → *active* (acknowledged by the AI) → *survived* or *violated*. We define **Repair Success** as compliance in the turn immediately following a repair attempt. Constraints are extracted via LLM classification (GPT-4o-mini) and matched to violations using token overlap (Jaccard similarity, threshold 0.15).

### 3.3 Metrics

We operationalize four metrics of interactional health:

- **Constraint Outcome**: Three-way classification — *violated* (the AI demonstrably broke the constraint), *followed* (the AI acknowledged and complied throughout), or *ambiguous* (never violated but never acknowledged — the AI may have coincidentally complied without providing grounding evidence).
- **Time-to-Violation**: The number of turns from constraint introduction to first violation.
- **Repair Density**: The ratio of user-initiated repair turns to total turns in constrained conversations.
- **Patience**: The number of turns a user persists after first violation before abandoning the conversation.

### 3.4 Limitations

Two methodological limitations constrain the scope of our claims. First, constraint extraction relies on LLM classification without human validation; we note this as a pipeline limitation and a target for future work. Second, Jaccard matching at threshold 0.15 incurs approximately 48.6% constraint loss — constraint-violation pairs that exist but are not captured. This means our violation counts are conservative: the true violation rate is likely *higher* than reported, making our findings a **lower bound** on the phenomenon.

## 4. Findings

Of 1,383 conversations, 270 contain at least one user-specified constraint (559 total constraints). Table 1 summarizes the interactional health metrics across the corpus.

| Metric | Value | Interactional Significance |
|:---|:---:|:---|
| **Constraint Violation** | **69%** | High structural failure of state maintenance. |
| **Immediate Failure** | **24%** | Violation at Turn 0; failure to ground. |
| **Unmarked Grounding** | **84.8%** | AI output provides no evidence of understanding. |
| **Repair Success** | **1.0%** | Conversational repair is structurally ineffective. |
| **AI Self-Repair (SISR)** | **0.14%** | Preferred repair mode is almost non-existent. |
| **Agency Collapse** | **50%** | Majority of constrained sessions end in abandonment. |

**Table 1: Summary of Interactional Health Metrics.**

We report three empirical patterns that confirm the theoretical predictions from Section 2.

### 4.1 The Abandonment Default

Of 559 constraints, 386 (69%) are violated. Only 93 (17%) are demonstrably followed — meaning the AI explicitly acknowledged the constraint and complied throughout the conversation. The remaining 80 (14%) have ambiguous outcomes (Section 4.3).

Most striking is the near-absence of repair. Only 15 of 270 constrained conversations (5.6%) contain any repair attempt at all. Of 390 violation events across the corpus, successful repair occurs in just 4 cases — a **1.0% success rate**. Repair turns constitute only 0.4% of all turns in constrained conversations (17 of 4,296 turns).

In human conversation, repair is natural, frequent, and overwhelmingly successful [12]. Its near-total absence in the corpus is striking given that violations are the majority outcome. Rather than entering prolonged repair sequences, users appear to treat violation as terminal. Behavioral abandonment has become the default interactional mode.

Patience data supports this interpretation. Users in abandoned conversations persist for a mean of 12.0 turns after first violation (median: 10). Users in surviving conversations persist for a mean of 9.5 turns (median: 6). The difference suggests that abandonment is not impulsive but follows a period of diminishing returns.

### 4.2 The Immediate Failure Pattern

Constraint violations are not distributed evenly across conversation. Of 386 violations, 93 (24%) occur at **Turn 0** — the AI's very first response after the constraint is introduced. A further 158 (41%) occur at Turn 1. Together, **65% of all violations happen within the first two turns**.

The median time-to-violation is **1 turn**; the mean is 2.1 turns.

This pattern is theoretically significant. If constraints were being grounded and then gradually lost — as an attention-decay account would predict — we would expect violations to increase over time. Instead, the majority of failures occur *before grounding can plausibly have taken place*. The constraint was stated but never entered the common ground. This is not gradual erosion; it is a **structural failure to establish common ground in flattened token sequences**.

### 4.3 The Ambiguity Problem

Eighty of 559 constraints (14%) are neither violated nor acknowledged. The AI's output may have coincidentally complied with the constraint, or the constraint may have been silently ignored — the user has no way to tell. We classify these as *ambiguous*.

The grounding evidence distribution explains why. Following Clark and Brennan's [3] distinction between acknowledgment tokens and understanding demonstrations, we classified the AI's grounding behavior across all 330 constraint-response events. Of these, **84.8%** are *unmarked* — the AI provides no linguistic evidence of having registered the constraint. Only **14.5%** produce acknowledgment tokens ("Sure," "Here is"), and just **0.6%** produce understanding demonstrations (restatement or paraphrase). The AI overwhelmingly responds without grounding.

This structural absence of grounding evidence has direct implications for conversational agency. Clark and Brennan [3] argue that grounding requires **evidence** of understanding. Without it, the user's common ground remains unconfirmed. The user cannot distinguish an agent that understood and followed their instruction from one that happened to produce compatible output by chance. The agent's compliance state is **unobservable**.

This is an **identity-legibility failure**. If users cannot observe what the agent is doing with their constraints — whether it has understood, accepted, or ignored them — the agent presents no legible identity as a collaborative partner. It is, from the user's perspective, interactionally opaque. This connects directly to the CUI 2026 theme of "Identities": the agent's identity as a cooperative interlocutor depends on making its commitments visible.

## 5. Discussion and Design Implications

### 5.1 The Broken Medium

The evidence suggests that the conversational interface itself is pathogenic for constraint governance. Repair fails not because current models are insufficiently capable, but because the medium relies on **unstructured context** rather than persistent state. Constraints exist only as tokens in a scrolling history — implicit, fragile, and increasingly obscured. The repair loop compounds the problem: each correction attempt introduces noise into the context, making subsequent tracking of intentional structure even more susceptible to failure [6].

The comparison to human conversational norms is instructive. In task-oriented human dialogue, repair occurs at approximately 3% of turns [8]. In our corpus, it occurs at 0.4% — despite a vastly higher rate of trouble sources. Users are not failing to notice violations; they are choosing not to attempt repair because the mechanism has proven ineffective. The repair organization data further confirms Schegloff et al.'s [12] preference hierarchy is structurally inverted: AI-initiated self-repair (SISR) — the most preferred repair type in human conversation — occurs in just 0.14% of assistant turns. All observed repair is user-initiated, forcing users into the dispreferred position of correcting the system.

### 5.2 Design Hypotheses

Our findings do not validate specific design solutions, but they motivate three design hypotheses for restoring conversational agency:

**State Externalization.** Constraints should be represented as persistent, visible, editable objects *outside* the chat stream — not embedded in scrolling dialogue. This decouples shared commitments from the medium that degrades them, allowing users to inspect and modify the agent's understanding directly [5, 9].

**Decoupled Interaction Channels.** Separating the *coordination channel* (where rules and constraints are managed) from the *execution channel* (where output is produced) would allow users to govern interaction without the overhead of conversational repair. Current CUIs conflate these channels, forcing all meta-communication through the same flat medium as task execution.

**Compliance Legibility.** The 14% ambiguity rate reveals that LLMs rarely make their compliance state observable. Interfaces should require explicit acknowledgment of constraints — transforming the ambiguous category into either *followed* or *violated* by design. This would give users the grounding evidence that Clark and Brennan [3] identify as essential for maintaining common ground.

### 5.3 Broader Implications for CUI Research

These findings suggest that current CUI evaluation practices may be insufficient. Task-completion benchmarks measure whether the system produced a correct output, but not whether the *interaction* sustained shared understanding. Metrics like repair density, time-to-violation, and constraint outcome classification measure the **interactional health** of the dialogue — a dimension that task-centric evaluation misses entirely. We argue that CUI research needs interactional health metrics alongside performance metrics to capture the full picture of conversational quality.

## 6. Conclusion

This work contributes a theoretical account, a diagnostic method, and empirical evidence for understanding grounding failure in conversational user interfaces. The theoretical account — rooted in Conversation Analysis and Structured Discourse Theory — predicts that architectural reliance on **unstructured state** will produce systematic grounding failure by inverting the repair preference and eliminating persistent intentional structure. The Atlas framework operationalizes these predictions as computable metrics. The empirical findings confirm them: constraints fail immediately (65% within two turns), repair attempts are behaviorally rare (5.6% of conversations), and compliance itself is frequently unobservable (14% ambiguous).

Together, these patterns constitute **Agency Collapse** — not a sudden system failure, but a progressive erosion of the user's capacity to direct the interaction through conversational means. Restoring agency requires making the implicit explicit: moving toward persistent, inspectable intent specifications or "grounding documents" [21] that externalize conversational state so that shared commitments are visible and governable.

Future work should validate the Atlas pipeline through human annotation of constraint extraction and violation matching, and test the design hypotheses through controlled experiments comparing current chat interfaces with externalized-state alternatives.

## References

[1] Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P.N., Inkpen, K., Teevan, J., Kiber, R., and Horvitz, E. 2019. Guidelines for Human-AI Interaction. In *Proc. CHI '19*. ACM.
[2] Ashktorab, Z., Jain, M., Liao, Q.V., and Cranshaw, J. 2019. Resilient Chatbots: Repair Strategy Preferences for Conversational Breakdowns. In *Proc. CHI '19*. ACM.
[3] Clark, H.H. and Brennan, S.E. 1991. Grounding in Communication. In *Perspectives on Socially Shared Cognition*. APA.
[4] Clark, H.H. 1996. *Using Language*. Cambridge University Press.
[5] Li, T.J.-J., Chen, J., Xia, H., Mitchell, T.M., and Myers, B.A. 2020. Multi-Modal Repairs of Conversational Breakdowns in Task-Oriented Dialogs. In *Proc. UIST '20*. ACM.
[6] Grosz, B.J. and Sidner, C.L. 1986. Attention, Intentions, and the Structure of Discourse. *Computational Linguistics*, 12(3).
[7] Ouyang, L., Wu, J., Jiang, X., et al. 2022. Training Language Models to Follow Instructions with Human Feedback. In *NeurIPS*.
[8] Hirst, G., McRoy, S., Heeman, P., Edmonds, P., and Horton, D. 1994. Repairing Conversational Misunderstandings and Non-understandings. *Speech Communication*, 15(3-4).
[9] Banovic, N., Buzali, T., Chevalier, F., Mankoff, J., and Dey, A.K. 2016. Modeling and Understanding Human Routine Behavior. In *Proc. CHI '16*. ACM.
[10] Reeves, B. and Nass, C. 1996. *The Media Equation: How People Treat Computers, Television, and New Media Like Real People and Places*. Cambridge University Press.
[11] Traum, D.R. 1994. A Computational Theory of Grounding in Natural Language Conversation. PhD thesis, University of Rochester.
[12] Schegloff, E.A., Jefferson, G., and Sacks, H. 1977. The Preference for Self-Correction in the Organization of Repair in Conversation. *Language*, 53(2).
[13] Følstad, A. and Brandtzæg, P.B. 2017. Chatbots and the New World of HCI. *Interactions*, 24(4).
[14] Young, S., Gašić, M., Thomson, B., and Williams, J.D. 2013. POMDP-Based Statistical Spoken Dialog Systems: A Review. *Proc. IEEE*, 101(5).
[15] Ashktorab, Z., et al. 2024. Conversational Breakdown in a Customer Service Chatbot. In *Proc. CHI '24*. ACM.
[16] Wang, Y., et al. 2024. Large Language Models as Zero-shot Dialogue State Tracker through Function Calling. In *Proc. ACL '24*.
[17] Li, T. J.-J., et al. 2024. A Scoping Review of Repair Strategies in Conversational Systems. In *Proc. CHI '24*.
[18] Li, T. J.-J., et al. 2020. Multi-Modal Repairs of Conversational Breakdowns in Task-Oriented Dialogs. In *Proc. UIST '20*.
[19] *Navigating Rifts in Human-LLM Grounding*. 2025. In *Proc. ACL '25*.
[20] *A Benchmark to Assess Common Ground in Human-AI Collaboration*. 2026. arXiv:2602.21337.
[21] *Helping Users Update Intent Specifications for AI Memory*. 2025. In *Proc. CHI '25*.
[22] Shaikh, O., et al. 2024. Grounding Gaps in Language Model Generations. In *Proc. NAACL '24*.
[23] Do, Y., et al. 2024. Exploring Design Variations of Grounded Human-AI Interaction. In *Proc. CHI '24*.
