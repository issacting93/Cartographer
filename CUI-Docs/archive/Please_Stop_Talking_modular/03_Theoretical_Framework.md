# Section 3: Theoretical Framework — The Architecture of Agency

To understand why chat interfaces fail at complex tasks, we must look beyond the "intelligence" of the model and examine the "affordances" of the interface. We identify a regression in the *visibility of state*—from the Command Line, through the GUI, to the Chat box.

## 3.1 The History of State: From Explicit to Ephemeral

The history of Human-Computer Interaction can be read as a struggle to make "System State" visible to the user (Norman, 1988).

| Phase | Interface | State Visibility | Cognitive Load |
|-------|-----------|------------------|----------------|
| **Phase 1** | Command Line | **State-Blind** | High expertise required; user holds directory structure and flags in working memory (Kirsh, 2005). |
| **Phase 2** | GUI | **State-Visible** | Desktop metaphor *externalizes* state; a checked box is a persistent epistemological claim. Task shifts from retrieval to recognition (Zhang & Norman, 1994). |
| **Phase 3** | Chat UI | **State-Ephemeral** | Regression to CLI era. No widgets, only scrolling log. Constraints lose status as *active regulators* as they scroll off-screen. |

This regression creates **Epistemic Opacity**: the user cannot know, at a glance, what the system "thinks" the current task state is.

## 3.2 The Task-Constraint Architecture (TCA)

To formalize this breakdown, we adopt the *Task-Constraint Architecture*. In this framework, a collaborative system is defined by four primitives:

| Primitive | Symbol | Description | Example |
|-----------|--------|-------------|---------|
| **Tasks** | $T$ | Units of goal-directed transformation | "Summarize text" |
| **Agents** | $A$ | Entities executing tasks | Humans or AI |
| **Representations** | $R$ | Information carriers | Text, Code, UI widgets |
| **Constraints** | $C$ | Rules regulating valid transformations | "Use Python 3.9" |

### 3.2.1 The Log-as-State Failure

In a GUI, a constraint (e.g., "Bold Font") is a *Structural Constraint* ($C_{struct}$). It is enforced by the code regardless of the user's memory.

In a Chat UI, that same constraint is merely a *Token* in the context window. It has no privileged status over any other token. We call this the **Log-as-State Limitation**.

Because the AI treats the "Constraint" and the "Conversation" as the same data type (Tokens), the constraint is subject to **Context Drift**. It can be "forgotten" or "overwritten" by subsequent tokens, requiring the user to constantly monitor the hidden state of the model.

## 3.3 Restatement Friction as Agency Tax

When state is held in memory rather than artifacts, the cost of maintenance rises.

| Interface | Repair Action | Cost |
|-----------|---------------|------|
| **GUI** | Click a box | $\approx 0$ |
| **Chat** | Type: "No, I said avoid asyncio." | $> 0$ |

We define this cost as **Restatement Friction**. It acts as a tax on agency. As the session lengthens, the "Tax" accumulates. Eventually, the user calculates that the cost of repairing the state exceeds the value of the goal, and they surrender (**Agency Collapse**). They accept the "Default Output" not because they like it, but because they can no longer afford to fix it.

## 3.4 Defining the Collapse Trajectory

We thus operationalize "Agency" not as a feeling, but as a *trajectory* of constraint maintenance.

> **Definition:** An interaction exhibits *Agency Collapse* if the specificity of user-provided constraints ($C$) decreases significantly over time ($\hat{\beta}_C < -\epsilon$), while the system's control of the dialogue increases.

This definition moves the discussion of "Agency" from a vague sentiment to an empirically measurable property of the interaction log.
