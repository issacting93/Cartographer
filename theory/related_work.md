# Related Work — Theoretical Grounding for Interactional Cartography

Organized by argumentative function in the CHI paper. Each entry includes a slot-in summary (1–2 sentences) ready for the Related Work section.

---

## 1. Mixed-Initiative Interaction & Authority Allocation

These establish that misalignment between user and system initiative is a **design problem**, not a capability problem — the theoretical ancestor of our "role overstepping" finding.

### Horvitz (1999) — Principles of Mixed-Initiative User Interfaces
- **Venue:** CHI 1999
- **PDF:** https://erichorvitz.com/chi99horvitz.pdf
- **Key claim:** Systems that shift initiative between user and agent need explicit mechanisms for managing uncertainty and authority — algorithmic intelligence alone is insufficient.
- **Slot-in:** Horvitz's principles of mixed-initiative interaction [1] established that authority allocation in human–agent dialogue requires explicit interface mechanisms, not merely capable models — a framing our mode violation findings directly extend to LLM-based CUIs.

### Allen, Hearst, Horvitz, Guinn (1999) — Mixed-Initiative Interaction
- **Venue:** AI Magazine 1999
- **PDF:** https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/mixedinit.pdf
- **Key claim:** Dialogue is a coordination problem requiring explicit structure; natural language alone doesn't solve collaborative control.
- **Slot-in:** Allen et al. [2] framed mixed-initiative dialogue as a coordination problem that natural language alone cannot solve, arguing for structured representations of initiative and shared plans — a position our "conversation as overloaded interface" mechanism formalizes empirically.

### Ferguson & Allen (2007) — Mixed-Initiative Systems for Collaborative Problem Solving
- **Venue:** AI Magazine 2007
- **PDF:** https://www.cs.rochester.edu/~ferguson/papers/ferguson-allen-collaborative-ai-mag-2007.pdf
- **Key claim:** Collaborative systems need explicit representations of goals, plans, grounding, and shared state — not just dialogue.
- **Slot-in:** Ferguson and Allen [3] argued that true collaboration requires explicit representations of goals and shared state beyond conversational history, anticipating our finding that task-state embedded in dialogue decays within 2–3 turns.

---

## 2. Repair as Measurable Interactional Phenomenon

These establish that conversational repair is structured, detectable, and fragile — supporting our operationalization and our 0.1% success rate finding.

### Li et al. (2020) — Sovite: Error Handling in Task-Oriented Conversations Grounded in Mobile UI
- **Venue:** UIST 2020
- **PDF:** https://toby.li/files/Li_Sovite_Error_Handling_UIST2020.pdf
- **Key claim:** Breakdowns hurt satisfaction and continuation; grounding repair in visible UI state makes recovery more actionable than repair through speech/chat alone.
- **Slot-in:** Li et al. [4] demonstrated that grounding conversational repair in visible interface state significantly improves recovery, consistent with our finding that repair through the conversational medium alone succeeds at 0.1% and motivating our CII's constraint pinning mechanism.

### Alloatti et al. (2024) — Tag-Based Detection of User Repair
- **Venue:** Computer Speech & Language 2024
- **DOI:** https://dl.acm.org/doi/10.1016/j.csl.2023.101603
- **Key claim:** User repair in human–agent dialogue is systematic, structured, and detectable via tagging methodologies.
- **Slot-in:** Alloatti et al. [5] showed that user repair attempts in human–agent dialogue are systematic and detectable, validating our operationalization of repair as a measurable interactional move rather than an anecdotal user behavior.

---

## 3. Prompting Burden & Its Limits

These support the "not just better prompting" rebuttal — showing that the field already recognizes prompting as hard and increasingly builds tooling to escape plain chat.

### Arawjo et al. (2024) — ChainForge: Visual Toolkit for Prompt Engineering
- **Venue:** CHI 2024
- **PDF:** https://glassmanlab.seas.harvard.edu/papers/chainforge.pdf
- **Key claim:** Ad-hoc chat makes evaluation and iteration difficult; people build external tools to compare prompts, models, and responses.
- **Slot-in:** ChainForge [6] demonstrates that researchers and practitioners routinely build tools to externalize and compare prompt variants outside of conversational interfaces, implicitly acknowledging that chat alone is insufficient for reliable steering — a pattern our constraint decay metrics quantify.

### Becker et al. (2024) — Prompting in the Dark
- **Venue:** CHI 2024
- **DOI:** https://dl.acm.org/doi/10.1145/3706598.3714319
- **Key claim:** Humans perform poorly at prompting and evaluating LLM outputs; better interfaces for evaluation and control are needed.
- **Slot-in:** Becker et al. [7] found that humans struggle systematically with prompting and evaluating LLM outputs, framing the burden as an interface-level concern rather than a skill deficit — supporting our argument that constraint failure is a property of the medium, not of user competence.

### Cai et al. (2024) — The Social Construction of Generative AI Prompts
- **Venue:** CHI 2024 (Extended Abstracts)
- **DOI:** https://dl.acm.org/doi/10.1145/3613905.3650947
- **Key claim:** "Prompt engineering" is a socio-cultural practice shaped by norms and tools, not a simple technical fix.
- **Slot-in:** Cai et al. [8] reframed prompt engineering as a collective socio-technical practice, undermining the assumption that individual prompt skill is sufficient to prevent constraint failure — a position our large-scale evidence reinforces by showing systematic decay regardless of prompt clarity.

### Dynamic Prompt Middleware (2024)
- **Venue:** arXiv 2024
- **URL:** https://arxiv.org/html/2412.02357v1
- **Key claim:** Middleware that adapts prompts dynamically improves user control and steerability.
- **Slot-in:** Even prompt-level solutions tend to become interface-level solutions: dynamic prompt middleware [9] improves control by interposing an architectural layer between user and model, consistent with our argument that the conversational medium requires structural augmentation, not better phrasing.

### Subramonyam et al. (2025) — Emerging Approaches in Generative AI Prototyping
- **Venue:** ACM 2025
- **DOI:** https://dl.acm.org/doi/full/10.1145/3706598.3713166
- **Key claim:** The field recognizes prompt iteration limits; instability, evaluation difficulty, and workflow integration remain open challenges.
- **Slot-in:** Subramonyam et al. [10] synthesized emerging challenges in generative AI prototyping, noting that prompt instability and evaluation difficulty remain unsolved — our work contributes the specific metrics and mechanism (constraint decay in the conversational medium) that these challenges lack.

---

## 4. State Externalization & Inspectable Interfaces

These show a growing pattern: the field keeps reinventing ways to get task state *out of* the conversation — supporting the task-first design argument.

### DreamSheets (2024) — Spreadsheet Interface for Prompt-Space Exploration
- **Venue:** CHI 2024
- **DOI:** https://dl.acm.org/doi/10.1145/3613904.3642858
- **Key claim:** Externalizing prompts and results into a grid supports reliable steering and sensemaking beyond linear chat.
- **Slot-in:** DreamSheets [11] externalized prompt-result relationships into a spreadsheet grid to support systematic exploration, demonstrating the same design intuition our task-first model formalizes: persistent, inspectable representations reduce steering burden compared to sequential conversation.

### WaitGPT (2024) — Monitoring & Steering Conversational LLM Agents
- **Venue:** ACM 2024
- **DOI:** https://dl.acm.org/doi/fullHtml/10.1145/3654777.3676374
- **Key claim:** Interactive representations of agent state improve oversight and correction of LLM-generated artifacts.
- **Slot-in:** WaitGPT [12] showed that making LLM agent state inspectable and steerable during execution substantially improves user oversight, supporting our thesis that constraints must be externally visible to be governable.

### User Feedback Barriers in Conversational Agents (2026)
- **Venue:** arXiv 2026
- **URL:** https://arxiv.org/html/2602.01405v1
- **Key claim:** Users struggle to give effective feedback to agents because of the ephemeral, turn-by-turn nature of conversation.
- **Slot-in:** Recent work [13] attributes user feedback barriers in conversational agents to the ephemeral, turn-by-turn nature of the medium itself — directly consistent with our finding that repair fails not because users don't try, but because the conversational medium structurally resists correction.

---

## Citation Map: Which References Support Which Claims

| Paper Claim | Supporting References |
|---|---|
| "Chat is an overloaded interface" (mechanism) | Allen et al. 1999, Ferguson & Allen 2007, Horvitz 1999 |
| "Not just better prompting" (rebuttal) | ChainForge, Prompting in the Dark, Social Construction of Prompts, Dynamic Prompt Middleware |
| "Repair is measurable but fragile" (operationalization) | Sovite (Li et al. 2020), Alloatti et al. 2024 |
| "Externalize state to restore agency" (design implication) | DreamSheets, WaitGPT, Sovite, Ferguson & Allen 2007 |
| "Role/mode drift is a design problem" (supporting evidence) | Horvitz 1999, Allen et al. 1999 |
| "The medium resists correction" (core finding) | User Feedback Barriers 2026, Sovite, Prompting in the Dark |
| "Field keeps escaping chat" (pattern) | ChainForge, DreamSheets, WaitGPT, Dynamic Prompt Middleware |
