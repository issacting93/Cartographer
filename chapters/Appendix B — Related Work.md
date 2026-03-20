# Appendix B: Related Work

> **Theoretical Positioning | Status: Complete**

---

This appendix positions Interactional Cartography within four research traditions and maps how each informs the program's claims. For the full citation details and slot-in summaries, see `theory/related_work.md`.

---

## B.1 Social Role Theory and CASA

**Foundational claim:** Humans unconsciously apply social heuristics to machines.

The CASA paradigm (Computers Are Social Actors; Reeves & Nass 1996) established that humans treat interactive systems as social actors when those systems exhibit minimal social cues — linguistic fluency, interactivity, responsiveness. This was demonstrated with systems far less capable than modern LLMs. The central prediction: more fluent systems should trigger social heuristics more strongly.

Our contribution extends CASA in two directions:

1. **Role classification at scale.** Rather than testing whether social projection occurs (it does), we classify *which roles* are projected and find that the repertoire is almost entirely instrumental (97%). CASA predicts social projection; we map its structure and discover its limits.

2. **Bounded Personhood.** CASA showed that people apply social scripts to machines. We show that this creates a specific mismatch: the AI is attributed the social status of a person (authority, competence) without the structural capacity (agency, memory, self-correction) that makes personhood functional in interaction. This explains why users persist in repair loops — their social scripts expect a competent partner to incorporate feedback.

**Key references:** Reeves & Nass 1996; Nass & Moon 2000; Parsons 1951; Bales 1950; Eagly 1987.

---

## B.2 Conversation Analysis and Repair

**Foundational claim:** Conversation is a structured, rule-governed activity with built-in repair mechanisms.

Conversation Analysis (CA), originating with Sacks, Schegloff, and Jefferson, established that human conversation follows systematic turn-taking rules with a strong preference for self-repair — speakers catch and correct their own errors. This preference hierarchy (self-initiated self-repair > other-initiated self-repair > self-initiated other-repair > other-initiated other-repair) is one of the most robust findings in linguistics.

Our contribution applies CA's repair framework to human-AI interaction and finds a structural inversion:

1. **LLMs never self-repair.** No introspective access to communicative intent means no same-turn self-correction and no transition-space repair.
2. **Users are forced into the least efficient repair type** (other-initiated other-repair) — the most face-threatening and labor-intensive option.
3. **Repair attempts actively degrade future repair probability** via the information-theoretic mechanism described in Chapter 3.

The 6x repair burden (18% repair rate in human-AI vs. 3% in human-human task dialogue from MultiWOZ) and the 0.74% repair success rate (2/271 events) extend CA's repair framework to a domain where its foundational assumptions — that conversational partners have persistent mental models and introspective access — do not hold.

**Key references:** Schegloff, Jefferson, & Sacks 1977; Sacks, Schegloff, & Jefferson 1974; Clark & Brennan 1991.

---

## B.3 Mixed-Initiative Interaction

**Foundational claim:** Authority allocation between human and agent requires explicit interface mechanisms, not merely capable models.

Horvitz (1999) established principles for mixed-initiative interaction: systems that shift initiative between user and agent need explicit mechanisms for managing uncertainty, authority, and turn-taking. Allen et al. (1999) framed dialogue as a coordination problem that natural language alone cannot solve. Ferguson & Allen (2007) argued that collaborative systems need explicit representations of goals, plans, and shared state beyond conversational history.

Our findings directly extend this tradition:

1. **Mode violations as authority failures.** 535 mode violations across the corpus (49.5% Premature Execution, 38.5% Unsolicited Advice) are precisely the initiative-management failures Horvitz predicted would occur without explicit authority mechanisms.

2. **Constraint decay as shared-state failure.** Ferguson & Allen anticipated that shared state embedded in dialogue alone would be insufficient. Our constraint tracker quantifies this: constraints decay to violation within a median of 1 turn.

3. **ISP as the mechanism.** The mixed-initiative literature identified the design problem. We identify the information-theoretic mechanism: repair noise accumulating in the context window structurally prevents state maintenance, regardless of model capability.

**Key references:** Horvitz 1999; Allen et al. 1999; Ferguson & Allen 2007.

---

## B.4 Grounding Theory and Information Theory

**Foundational claim:** Successful communication requires establishing mutual understanding ("common ground") through an interactive process of grounding.

Clark & Brennan (1991) defined grounding as the process by which communicative partners establish shared understanding through contribution, acknowledgment, and repair. Grounding costs vary by medium — phone conversation has different grounding properties than written text.

Our contribution adds the LLM context window as a grounding medium with unique failure modes:

1. **Grounding costs are asymmetric.** The user pays all grounding costs (reformulation, repair, constraint restatement). The AI pays none — it has no persistent model to update.
2. **The grounding medium degrades with use.** Each repair attempt adds tokens that dilute the original signal, making the next grounding attempt less likely to succeed. This is unique to context-window-based interaction.
3. **Context windows violate the "least collaborative effort" principle.** Clark & Brennan's framework assumes both partners minimize effort to reach mutual understanding. In LLM interaction, effort is maximally skewed toward the user.

**Key references:** Clark & Brennan 1991; Clark 1996; Shannon 1948 (information theory).

---

## B.5 State Externalization and Interface Design

**Foundational claim:** Externalizing internal representations into persistent, inspectable interface elements improves human cognitive performance and system oversight.

A growing body of work demonstrates that the field is converging on state externalization as a solution to conversational AI's limitations, even without a shared theoretical framework for why:

- **ChainForge** (Arawjo et al. 2024, CHI): Externalizes prompt variants into a visual comparison toolkit.
- **DreamSheets** (2024, CHI): Externalizes prompt-result relationships into a spreadsheet grid.
- **WaitGPT** (2024, ACM): Makes LLM agent state inspectable and steerable during execution.
- **Sovite** (Li et al. 2020, UIST): Grounds conversational repair in visible UI state rather than dialogue.

Our contribution provides the theoretical framework connecting these disparate design solutions:

1. **ISP as the common cause.** These tools all address the same underlying problem — state that is implicit in conversation and decays — but lack a shared diagnosis. ISP provides it.
2. **The Context Inventory Interface** as a principled instantiation. Rather than ad-hoc externalization, we decompose the chat interface's three conflated functions (coordination, memory, execution) into separate, persistent, editable UI elements.
3. **Measurement-first.** Unlike the tools above, which are primarily design contributions, our program diagnoses the problem quantitatively (constraint decay, repair failure rates, collapse probability) before proposing the solution.

**Key references:** Norman 1988, 1991; Hutchins 1995; Zhang & Norman 1994; Arawjo et al. 2024; Li et al. 2020.

---

## B.6 Positioning Summary

| Tradition | What it established | What we add |
|-----------|-------------------|-------------|
| CASA / Social Role Theory | Humans project social roles onto machines | Role structure is 97% instrumental; Bounded Personhood explains repair persistence |
| Conversation Analysis | Repair is structured with self-repair preference | LLMs invert the preference; repair degrades signal; 0.74% success rate |
| Mixed-Initiative | Authority allocation needs explicit mechanisms | Quantified: 535 mode violations, median 1-turn constraint decay |
| Grounding Theory | Mutual understanding requires interactive grounding | Context windows make grounding costs asymmetric and self-defeating |
| State Externalization | Externalizing state improves cognition and oversight | ISP provides the theoretical framework; CII provides principled decomposition |

---

## B.7 What This Literature Does Not Cover

Several aspects of our work lack established precedent:

1. **Constraint tracking as a formal method.** No prior work systematically tracks user constraint survival rates in conversational AI. Our constraint state machine is novel instrumentation.

2. **Agency Collapse as a measurable construct.** "Frustration" and "failure" in CUI research are typically self-reported. Our operationalization (repair count thresholds, tone degradation, specificity collapse) makes collapse detectable from interaction data alone.

3. **The variance ratio.** The finding that conversations with identical role labels show 2,817x variance in emotional trajectory has no precedent we are aware of. It suggests that role taxonomies capture destination but completely miss journey — a blind spot in existing CUI evaluation frameworks.

4. **Domain-dependent instrumental monopoly.** The shift from 97% instrumental (general) to ~50% expressive (mental health) has not been documented in the CASA or CUI literature. Prior work treats "social projection onto AI" as domain-invariant.
