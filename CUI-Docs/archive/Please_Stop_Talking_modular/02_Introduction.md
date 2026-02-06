# 1. Introduction

Conversational user interfaces (CUIs) have become a dominant paradigm for interacting with large language models and AI-powered systems. From general-purpose assistants to specialized task bots, these systems present interaction primarily as a sequence of dialogue turns: users issue prompts, systems respond, and context is implicitly maintained through the conversational history. This paradigm has proven remarkably flexible, enabling users to accomplish a wide range of goals—from drafting documents and planning trips to debugging code and navigating customer service workflows—using natural language alone.

However, as CUIs are increasingly used for complex, multi-step, and constraint-sensitive work, cracks in the conversation-first paradigm have begun to surface. Users frequently report needing to restate goals, repeat constraints, or correct the system after it produces outputs that are locally coherent but globally misaligned with the task at hand. These failures are often attributed to limitations of language models or imperfect prompt engineering. In this paper, we argue that many of these breakdowns are **structural**, not merely model-level: they arise because conversation is being asked to serve simultaneously as a coordination mechanism, a memory store, and a task management system.

## 1.1 Conversation as an Overloaded Interface

In current CUIs, task state is embedded implicitly within the scroll of dialogue. Goals, constraints, intermediate artifacts, and decisions are expressed through natural language and then pushed upward as the conversation progresses. While this representation is flexible, it is also ephemeral: earlier information becomes less visible, harder to reference, and more costly to reintroduce. As tasks extend over time, users must actively remember and restate what matters, while the system must infer which parts of the dialogue history remain relevant.

This design places a heavy burden on both parties. For users, conversation becomes the de facto file system, debugger, and state manager for their work. For systems, conversational history becomes a lossy proxy for task structure. The result is a pattern we repeatedly observe in practice: constraint drift, scope confusion, and breakdowns in long-horizon tasks, even when individual responses appear correct.

Importantly, this is not a claim that conversation is an unnatural or inappropriate medium for task-oriented interaction. On the contrary, dialogue is highly effective for **coordination**—for clarifying intent, negotiating requirements, and refining ideas. The issue arises when conversation is also forced to carry the responsibilities of persistent task representation and context management. In effect, CUIs conflate *how users communicate* with *how tasks are structured and maintained*.

## 1.2 Empirical Motivation: Tasks Hidden in Plain Sight

Despite this structural fragility, users overwhelmingly approach conversational systems with functional intent. Prior analyses of conversational datasets and our own exploratory studies suggest that the majority of interactions with general-purpose AI systems are task-oriented rather than purely social or expressive. Users ask systems to write, plan, analyze, summarize, transform, and decide. These requests often belong to recurring task types with recognizable structures and constraints.

Yet, within a chat interface, these tasks have no explicit representation. A “write a blog post,” “plan a trip,” or “debug this script” request exists only as a sentence in the dialogue stream. When the user shifts focus, pauses, or returns later, the task must be reconstructed from conversational traces—if it can be reconstructed at all. As a result, users routinely encounter moments where they ask some variant of “Can you remind me what we were doing?” or reintroduce documents, policies, or constraints that were previously provided.

These breakdown moments are not edge cases; they are signals of a mismatch between users’ mental models of tasks as persistent entities and the interface’s representation of interaction as transient dialogue turns. Rather than treating such moments as failures of memory or attention, we treat them as design evidence: they indicate that tasks are present, meaningful, and central to user activity, but are insufficiently supported by the interface.

## 1.3 Reframing the Primary Unit of Interaction

This paper proposes a reframing of conversational interaction: **tasks, not dialogue turns, should be treated as the primary, persistent unit of interaction in CUIs**. In this model, conversation remains important, but it is no longer the container for task state. Instead, tasks are represented explicitly as first-class objects that persist across time, interruptions, and interaction modalities. Conversation becomes one tool for operating on a task—alongside other interaction mechanisms such as context selection, artifact management, and tool invocation.

Unlike traditional graphical user interfaces, which externalize task state through persistent visual structures such as files, tabs, and windows, conversational user interfaces internalize task state within dialogue history. This shift enables flexible language-based interaction but collapses task structure into an ephemeral conversational stream. Our work does not propose a return to form-based or menu-driven interaction. Instead, it introduces task objects as a lightweight structural layer designed specifically for language-first interfaces, allowing conversation to operate within explicit task scope while preserving the flexibility of natural language interaction.

By separating task structure from conversational flow, we aim to reduce the cognitive and interactional load placed on dialogue alone. Users should be able to see what task they are working on, what context is currently in scope, and what artifacts or constraints are active—without needing to infer these from a scrolling history of messages. Similarly, systems should be able to ground their responses in explicitly selected task context rather than relying on implicit inference from dialogue history.

## 1.4 Task Objects and Task Lifetimes

To make this reframing concrete, we introduce the notion of a **Task Object**: a persistent representation of a user-defined goal, its associated context, and its evolving state. Unlike a conversational turn, a task object has a lifetime. It can be created, worked on, suspended, resumed, and eventually completed or archived. Conversation occurs *within the scope* of an active task object, rather than defining the task implicitly.

This task-first framing enables interaction patterns that are difficult or impossible to support in purely conversational interfaces, such as:

* Explicitly pinning important context or intermediate results to a task.
* Switching between multiple ongoing tasks without losing state.
* Resuming work after interruptions with preserved constraints and artifacts.
* Making visible which information is currently “in scope” for the system.

Crucially, this approach does not require abandoning conversational interaction. Instead, it repositions conversation as a scoped, task-aware mechanism for coordination and execution, rather than as an all-purpose container for state.

## 1.5 Contributions

This paper makes four contributions to the study and design of conversational user interfaces:

1. **An empirical motivation** showing how task structure is routinely collapsed into dialogue history, leading to recurrent breakdowns in constraint-sensitive work.
2. **A task-first conceptual model** that reframes tasks as persistent interaction units with explicit lifetimes, distinct from conversational turns.
3. **Three reusable interaction patterns**—Pin to Task, Task Shelf, and Context Lens—that operationalize this model in a CUI setting.
4. **A comparative evaluation** demonstrating that task-first interfaces improve constraint maintenance, task continuity, and user-perceived control relative to standard chat-based interaction.

By articulating tasks as first-class objects and repositioning conversation as a tool rather than the interface itself, this work aims to expand the design space of CUIs toward more robust support for complex, long-horizon human–AI collaboration.
