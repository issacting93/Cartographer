# Section 6: Design Response — The Context Inventory Interface

To fix the mechanism of "Agency Collapse," we must separate *Flow* from *State*. We propose the **Context Inventory Interface (CII)**, an "Instrumental Interface" that reifies constraints as manipulable objects.

## 6.1 System Architecture

CII introduces a persistent "Inventory" pane alongside the chat. This pane holds **Context Nodes**, which are injected into every AI context window but remain visible and editable to the user.

### Key Insight
> Constraints should be *artifacts*, not *utterances*.

## 6.2 Interaction Patterns: Beyond Chat

We introduce three novel interaction patterns that shift the locus of control from the conversational stream to the spatial interface.

### Pattern 1: Keyword as Context (The "Pin" Operator)
*Problem:* In standard chat, key constraints are buried in prose.
*Solution:* Users can highlight any phrase in the chat stream (e.g., "keep it under 500 words") and "Pin" it. This action extracts the text and converts it into a formal Constraint Node ($C$).
*   **Mechanism:** `Selection` $\to$ `Promotion` $\to$ `Reification`.
*   **Result:** Context is curated from the flow, not just typed into it.

### Pattern 2: Context as Inventory (The "Hold" Operator)
*Problem:* Constraints drift out of the context window or are overridden by recency bias.
*Solution:* The active state of the system is visualized as a persistent list (the Inventory). This is not a "history" but a "dashboard" of active rules.
*   **Mechanism:** Visually distinct nodes ($\delta_{hard}$, $\delta_{soft}$, $\phi_{role}$) that persist across turns.
*   **Result:** The user can audit the system's "mind" at a glance (solving Epistemic Opacity).

### Pattern 3: Drag-and-Drop Modules (The "Compose" Operator)
*Problem:* Complex prompts require re-typing standard instructions (e.g., "Act as a Senior Engineer").
*Solution:* Users can drag pre-defined "Persona" or "Task" modules from a library into the active Inventory.
*   **Mechanism:** Direct manipulation of cognitive resources.
*   **Result:** Complex contexts can be composed like Lego blocks, reducing the activation energy for high-agency tasks.

## 6.3 Node Ontology

| Node Type | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| **Goal Nodes** | $\delta_{goal}$ | The terminal state | "Plan a 3-day trip" |
| **Constraint Nodes** | $\delta_{hard}$ | Binary restrictions | "Budget < $500" |
| **Preference Nodes** | $\delta_{soft}$ | Stylistic guidance | "Avoid tourist traps" |
| **Resource Nodes** | $\sigma$ | Uploaded files/data | [uploaded PDF] |
| **Role Nodes** | $\phi$ | The persona to adopt | "Act as a travel agent" |

## 6.4 Atomic Operations

| Operation | Symbol | Description | Associated Pattern |
|-----------|--------|-------------|--------------------|
| **Pin** | $Op_{pin}$ | Promote message segment $\to$ Inventory | *Keyword as Context* |
| **Compose** | $Op_{drag}$ | Drag module $\to$ Inventory | *Drag & Drop* |
| **Edit** | $Op_{mod}$ | Click to modify value directly | *Inventory Management* |
| **Deactivate** | $Op_{susp}$ | Toggle constraint off | *State Auditing* |

### Key Insight
> Replace "persuasion" with "instrumentation." We do not *ask* the AI to remember; we *equip* it with the memory.
