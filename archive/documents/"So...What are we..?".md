# So… What Are We?
## Mapping the Foreclosed Relational Outcomes of Human–AI Interaction

### Background and Related Work 
Drawing on Social Role Theory and the Computers Are Social Actors (CASA) paradigm, we argue that role assignment emerges predictably from interaction. Linguistic fluency, responsiveness, and norm adherence trigger social heuristics that lead users to project expectations, competence, and intent onto the system, even when they explicitly acknowledge the system is nonhuman. 

Unlike human roles, which imply a coherent self, AI roles are interactional achievements maintained solely through the user's projection and the system's statistical mimicry. They are real in their consequences (affect, reliance) but baseless in their agency. This creates a state of **Bounded Personhood**, where the system is attributed high epistemic authority (knowledge legitimacy) despite having zero volitional agency. The resulting interactional space is characterized by **Implicit State Pathology**—a systematic conflation of coordination (managing the dialogue), memory (retaining context), and execution (performing the task)—which leads to a narrow corridor of **Relational Foreclosure**.

### Motivation
Conversational AI systems are increasingly encountered as social actors: collaborators, listeners, coaches, and advisors. Prior research has examined trust, anthropomorphism, and emotional reliance, yet a more fundamental question remains unresolved:
**What role do users actually assign to AI during interaction—and what kind of role is this, structurally?**

This paper investigates human–AI role dynamics not as a matter of user belief or perception alone, but as an interactional phenomenon that shapes authority, responsibility, and reliance. Rather than asking whether AI feels social, we ask what role it is performing in practice—and whether existing role frameworks adequately describe this relationship. We introduce **Conversational Cartography**, a method for mapping these interactions into a 3D relational-affective space.

---

### Methodology: Interactional Cartography

To map these dynamics, we employed **Interactional Cartography**, a mixed-methods approach that decomposes 2,577 conversations (from Chatbot Arena, WildChat, and OASST) into their constituent structural and effective components.

Rather than relying solely on post-hoc surveys or user self-reports, we analyzed the *interactional artifacts* themselves—the logs of what was actually said and done. We utilized a **30-feature Evidence Architecture** to capture the nuance of these interactions across five high-signal channels:

1.  **Affect Proxy (37.3% Signal Contribution):** Measuring the emotional trajectory of the conversation (Valence, Arousal, Dominance) to detect volatility. We found that *variance* (the shape of the journey) was far more predictive than the average emotional state.
2.  **Linguistic Divergence (21.6%):** Tracking how much the human and AI align or drift apart in their language use, a key proxy for coordination and "sync."
3.  **Interaction Dynamics (15.4%):** Quantifying the stability of goals, the rate of repair attempts, and the ratio of hedging to assertion.
4.  **Expressiveness (15.4%):** Measuring shifts in linguistic complexity and personal disclosure.
5.  **Structure (7.2%):** Simple metrics like turn count and message length.

This multi-dimensional analysis allowed us to move beyond simple role labels and see the *texture* of the interaction, revealing that two conversations with the same "role" could have radically different experiential qualities.

---

### RQ1: Do Human–AI Roles Exist?
The research establishes that human-AI roles do exist and that users do not treat these systems as neutral tools.
*   **Predictable Emergence:** Role assignment emerges predictably from interaction, triggered by features like linguistic fluency and responsiveness.
*   **Social Heuristics:** Users utilize familiar interpersonal schemas to stabilize expectations during the conversation, even in technical contexts.
*   **Interactional Achievements:** AI roles are "real in their consequences" (affect, reliance) but are maintained through user projection and statistical mimicry rather than actual agency.

#### RQ1a: Comparing Human–AI and Human–Human Roles
The structural features of these roles share similarities with human relationships but possess distinct differences:
*   **Authority-Agency Mismatch:** A key difference is the attribution of high epistemic authority to systems that lack volitional agency.
*   **Trajectory Variance:** AI roles are unstable. Our analysis of **2,576 classified conversations** found that identical role labels (e.g., Information-Seeker to Expert-System) showed up to **2,817x variance** in their affective trajectories. This proves that trust and quality are negotiated during the "journey" of the conversation rather than at a static "destination."

---

### RQ1b: Categorization and The Authority-Agency Mismatch

We categorize these interactions using a **12-Role Taxonomy** that maps specifically to the **Authority-Agency Mismatch**.

Our core hypothesis is that users attribute high **Epistemic Authority** (responsibility for truth/outcome) to systems that have zero **Volitional Agency** (responsibility for intent/meaning). This mismatch forces users into a narrow set of roles designed to manage this clearer contradiction.

We identified **535 Mode Violations** where this management broke down. The data reveals a stark reality: **97.0% of human roles are purely instrumental** (Information-Seeker, Director, Provider), while expressive or relational roles account for only 3.0%.

This created a **"Relational Foreclosure"**: users are funneled into treating the AI as a tool, even when the AI's language (e.g., "I'm sorry to hear that") invites a social response.

#### The 12-Role Taxonomy
Human and AI roles are distributed across dimensions of **Orientation** (Instrumental vs. Social) and **Authority**. The table below illustrates how roles are not just "types" of people, but strategies for managing authority:



**Key Findings:**
*   **The Instrumental Monopoly:** As noted, **97.0%** of human roles are purely instrumental. This concentration creates a "narrow funnel" where diverse human needs are compressed into a single "Expert-System" AI response mode (**77.6%**).
*   **The Variance Trap (2,817x):** Perhaps the most critical finding is the **"Same Destination, Different Journey"** effect. Within the dominant Information-Seeker → Expert-System dyad, we found a **2,817x variance** in affective volatility. 
    *   *Implication:* You can have a "smooth" queries interaction or a "volatile" agency collapse, and they look identical on the surface (same roles). The *role* doesn't describe the *struggle*.
*   **Agency Collapse:** 71.5% of user-specified constraints fail, with a mean time-to-violation of **2.5 turns**. Repair succeeds less than **1%** of the time, leading to "Agency Collapse" in **50.3%** of sustained conversations. The user is forced to take responsibility (Authority) for the AI's failure to maintain state (Agency).

---

### RQ2: Impact on Engagement
**How does human engagement change when these roles are made visible?**

To test the visibility hypothesis, we implemented the **Atlas Suite** — an open-source interactive analytics platform that externalizes the three components of Implicit State Pathology (coordination, memory, execution) as persistent, navigable visual artifacts. The suite comprises four views:

*   **Findings Dashboard:** Aggregate KPIs, role distributions, and constraint survival metrics across the corpus. Surfaces the "big picture" — the 97% instrumental concentration, the 70% IS→ES dominance, and the 535 mode violations — as navigable data rather than hidden state.
*   **Atlas Global View:** A force-directed meta-graph clustering all 745 canonical conversations by structural similarity. Makes the shape of the problem visible: tight clusters of smooth IS→ES transactions surrounded by scattered volatile outliers.
*   **Cartography Explorer:** Single-conversation deep dive. Visualizes the graph topology (nodes: turns, moves, constraints; edges: violations, repairs), the affective trajectory, and the repair loop structure. This is where the 2,817x variance becomes tangible — users can compare the flat trajectory of `chatbot_arena_11761` against the volatile spirals of `wildchat_new_300289e3c40bce07`.
*   **Side-by-Side Comparison:** Direct structural comparison of two conversations, enabling the "same role, different journey" analysis that the variance ratio quantifies.

The Atlas Suite is operational and serves from the `atlas_canonical` graph data (N=745). It functions as a diagnostic instrument — making visible the role rigidity, constraint drift, and repair failure that the conversational interface keeps implicit.

#### Planned Evaluation
A formal comparative study is planned to measure the effect of role/state visibility on user behavior:
*   **Design:** Within-subjects comparison (N=20+), standard chat baseline vs. Atlas-augmented interface.
*   **Hypotheses:**
    *   H1: Visibility of role assignments and constraint state increases perceived user agency.
    *   H2: Externalizing constraint state reduces repair loop frequency by allowing users to reference persistent artifacts rather than re-stating constraints in-channel.
    *   H3: Making the "Instrumental Corridor" visible enables users to deliberately shift toward more expressive or co-constructive interaction modes.
*   **Metrics:** Perceived agency (Likert), repair attempts per violation, role diversity index, constraint survival rate.

---

---

### RQ2a: Mental Health Domain Expansion (Phase 4 — Completed)

We applied the full Cartography pipeline to mental health counseling data using two datasets:
- **Single-turn counseling** (Amod, N=100): Real licensed therapist responses to patient queries.
- **Multi-turn caregiver sessions** (MentalChat16K PISCES subset, N=50): Behavioral health coach ↔ caregiver conversations (Alzheimer's, hospice, caregiving). Mean 7.6 turns/session.

Pipeline ran with **Claude Haiku** (claude-haiku-4-5-20251001) for LLM classification steps, using a purpose-built Anthropic-to-OpenAI adapter.

#### Key Findings: The Instrumental Monopoly is Domain-Dependent

| Metric                   |    General Corpus (N=2,577) | Mental Health Single-Turn (N=100) |            Caregiver Multi-Turn (N=50 Pilot) |
| ------------------------ | --------------------------: | --------------------------------: | -------------------------------------------: |
| **Dominant Human Role**  |  Information-Seeker (73.9%) |   **Info-Seeker (50%)** / Soc-Exp (46%) |                     Social-Expressor (~58%) |
| **Dominant AI Role**     |       Expert-System (77.6%) |             **Advisor (65.5%)** |                              Advisor (~44%) |
| **Mode Violation Rate**  |                         42% |                               98% |                                        79.4% |
| **Dominant Violation**   | Premature Execution (49.5%) |          Unsolicited Advice (51%) |                  Unsolicited Advice (66.7%) |
| **Emotional Tone**       |        Neutral/Professional |    63% Supportive, 29% Empathetic |                              94% Empathetic |
| **Conversation Purpose** |   56.3% Information-Seeking |   28% Emotional Processing, 31% Advisory |                    86% Emotional Processing |

**The 97% instrumental finding doesn't hold in mental health.** Patients lead with significant emotional expression (Social-Expressor ~46%). This confirms that the instrumental monopoly is a property of *general-purpose AI use*, not a universal feature of human-AI interaction.

However, the AI's response shifts from "Expert" to **"Advisor" (65.5%)**, creating a **Relational Mismatch**: expressive human input meets prescriptive guidance. This is the **Relational Bypassing**—the system performs advisor moves without the relational infrastructure (sustained listening, empathic attunement) to support them.

Mode violations are **dramatically worse** in therapeutic contexts (79-98% vs 42%), dominated by Unsolicited Advice rather than Premature Execution. The counselor jumps to solutions when the patient is in LISTENER mode. This is the opposite of evidence-based therapeutic practice (motivational interviewing, person-centered therapy), where reflective listening should precede advice-giving.

#### Methodological Refinement & Bias Mitigation
The specific challenges of the mental health domain revealed three critical biases in our initial instrumentation, which we are addressing through a targeted mitigation strategy:

1.  **Instrument Bias (The "Taxonomy Problem"):** The v1 taxonomy (Listener/Advisor/Executor) assumes instrumental intent, blinding the tool to emotional work (e.g., disclosure classified as "providing context").
    *   *Mitigation:* Pilot the **v2 Taxonomy** (Disclosing, Accompanying, Exploring) via manual annotation on a stratified sample (N=20 MH, N=20 General) to calculate Inter-Rater Reliability (IRR) before automated scaling.

2.  **Domain Bias (The "Context Problem"):** The "Instrumental Monopoly" (97% instrumental) is partially a function of the general-purpose, task-oriented domains sampled (coding, Q&A).
    *   *Mitigation:* Explicitly frame the Mental Health findings (48% Social-Expressor) as the **domain counter-weight**, proving that the monopoly is context-dependent rather than a universal law of AI interaction.

3.  **Model Bias (The "Classifier Problem"):** Reliance on specific LLMs (GPT-4o vs Claude) may introduce model-specific labeling tendencies.
    *   *Mitigation:* **Cross-Model Validation** — run a sub-sample of the General corpus through Claude Haiku (using the new `anthropic_adapter.py`) to quantify classifier drift and ensure role definitions are robust across models.

---

### Next Steps and Primary Work
*   **RQ2 Evaluation:** Conduct the comparative study described above using the operational Atlas Suite.
*   **Multi-Turn Mental Health at Scale:** Expand the PISCES multi-turn analysis from N=50 to the full 423 multi-turn sessions available in MentalChat16K, and integrate constraint lifecycle tracking for longer sessions.
*   **Human Baselines (Phase 5):** Large-scale comparison with human–human corpora (e.g., DailyDialog) to quantify the "relational deficit" and establish whether the 97% instrumental concentration is specific to human-AI interaction or reflects broader conversational norms in text-based media.
*   **Real-Time Intervention:** Extending the Atlas Suite from a post-hoc diagnostic tool to a real-time overlay that detects volatility spikes and role rigidity during live conversations, intervening before Agency Collapse occurs.
