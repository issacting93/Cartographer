# Context Engine: Implementation Plan

**Project:** Context Engine for Task-First Conversation
**Paper:** "Tasks, Not Turns: Reframing Conversational Interfaces Around Persistent Task Objects"
**Target Venue:** CUI 2026 (Full Paper)
**Status:** ✅ Evaluation Prototype Complete

---

## 1. What Is the Context Engine?

The **Context Engine** is a backend system that manages persistent task state for conversational AI interfaces. It solves a fundamental problem:

> **In current chat interfaces, task state is collapsed into dialogue history. The Context Engine externalizes this state into inspectable, manipulable Task Objects.**

### 1.1 The Problem It Solves

| In Chat-Only Interfaces | With Context Engine |
| :--- | :--- |
| Constraints buried in scroll | Constraints are visible nodes |
| State inferred from history | State explicitly managed |
| Tasks implicit in conversation | Tasks are first-class objects |
| Resumption requires re-reading | Resumption loads Task Object |
| User must remember context | System holds context |

### 1.2 Core Concepts

| Term | Definition |
| :--- | :--- |
| **Task Object** | A persistent container for a user-defined goal, its constraints, artifacts, and state |
| **Constraint Node** | A typed element (Goal, Constraint, Preference) within a Task |
| **Context Inventory Interface (CII)** | The user-facing UI that exposes Task Objects |
| **Agency Collapse** | Progressive surrender of user control due to cognitive cost of constraint maintenance |

---

## 2. Current Implementation Status

### ✅ Completed Components

| Component | File | Status |
|-----------|------|--------|
| **Baseline Chat** | `pages/BaselineChat.tsx` | ✅ Complete |
| **Treatment Chat** | `pages/TreatmentChat.tsx` | ✅ Complete |
| **Constraint Sidebar** | `components/ConstraintSidebar.tsx` | ✅ Complete |
| **Chat Interface** | `components/ChatInterface.tsx` | ✅ Complete |
| **Career Coaching Script** | `scenario.ts` | ✅ Complete |
| **BLOOM Design System** | `index.css` | ✅ Complete |
| **Hex Workspace Demo** | `components/HexWorkspace.tsx` | ✅ Complete |

### Evaluation Prototype

The prototype implements a **between-subjects comparative study**:

- **Condition A (Baseline):** `/baseline` - Chat-only interface
- **Condition B (Treatment):** `/treatment` - Chat + Constraint Sidebar

**Scenario:** Career Coaching with forced constraint violation at Turn 8.

---

## 3. Technical Architecture

### 3.1 Frontend Structure

```
frontend/src/
├── App.tsx                    # Main routing
├── index.css                  # BLOOM Design System
├── scenario.ts                # Career coaching script
├── types.ts                   # TypeScript types
├── pages/
│   ├── BaselineChat.tsx       # Condition A - Chat only
│   ├── TreatmentChat.tsx      # Condition B - Chat + Sidebar
│   └── ContextInventory.tsx   # Hex workspace demo
└── components/
    ├── ChatInterface.tsx      # Chat UI component
    ├── ConstraintSidebar.tsx  # Persistent constraint list
    ├── ContextPalette.tsx     # Draggable context pills
    ├── HexWorkspace.tsx       # 6-node hex grid
    └── TaskWizardPanel.tsx    # Full task management (legacy)
```

### 3.2 Key Data Types

```typescript
// Constraint for scenario
interface Constraint {
  id: string;
  type: 'Goal' | 'Constraint' | 'Preference';
  label: string;
  description: string;
}

// Study metrics tracking
interface StudyMetrics {
  condition: 'baseline' | 'treatment';
  constraintRestatements: number;
  constraintViolationsDetected: number;
  repairTurns: number;
  totalTurns: number;
  pinActions: number;           // Treatment only
  contextLensQueries: number;   // Treatment only
}
```

---

## 4. Evaluation Design

### 4.1 Career Coaching Scenario

**Initial Constraints:**
| Type | Constraint |
|------|------------|
| Goal | Find next senior engineering role |
| Constraint | Work-life balance (max 45 hrs/week, no on-call) |
| Constraint | Remote-first companies only |
| Preference | Tech/AI sector |

**Scripted Flow:**
- **Turns 1-7:** Normal coaching conversation
- **Turn 8:** Forced violation (OpenScale AI suggestion)
- **Turn 9+:** User repairs, AI acknowledges

**Turn 8 Violation:**
> "OpenScale AI - Founding Engineer: Expect 60+ hour weeks, on-call rotation, SF office 3 days/week..."

Violates: work-life balance, no on-call, remote-first

### 4.2 Conditions

| Condition | Interface | Repair Method | Metrics |
|-----------|-----------|---------------|---------|
| **A (Baseline)** | Chat only | Type from memory | Keystrokes, time |
| **B (Treatment)** | Chat + Sidebar | Click constraint | Clicks, time |

### 4.3 Key Metrics

| Metric | Operationalization | Paper Reference |
|--------|-------------------|-----------------|
| **Repair Time** | Seconds from Turn 8 → user correction | Section 7.3 |
| **Repair Actions** | Keystrokes (A) vs clicks (B) | Section 7.4 |
| **Restatement Count** | Explicit re-mentions of constraints | Section 7.3 |
| **Perceived Control** | Post-task 7-point Likert | Section 7.3 |

---

## 5. BLOOM Design System

### 5.1 Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--black` | `#1A1A1A` | Headers, primary text |
| `--white` | `#FFFFFF` | Backgrounds |
| `--yellow` | `#FFD700` | Primary accent, CTAs |
| `--orange` | `#FF8C42` | Warnings, violations |
| `--green` | `#4CAF50` | Success, goals |
| `--gray` | `#E5E5E5` | Borders |
| `--gray-dark` | `#666666` | Secondary text |

### 5.2 Components

- **Pills:** Rounded buttons with icon + text
- **Cards:** Rounded corners (16-24px), subtle shadows
- **Icons:** Material Symbols Rounded
- **Typography:** Inter font family

---

## 6. Backend API (Reference)

```
POST /api/context/task/create     # Create new task
GET  /api/context/task/list       # List user's tasks
POST /api/context/task/switch     # Switch active task
POST /api/context/event/pin       # Pin text as constraint
POST /api/context/query/context   # Query with scoped context
```

Note: Current evaluation prototype uses scripted responses. Backend integration is optional for the study.

---

## 7. Next Steps

### For CUI 2026 Submission

1. [ ] **Pilot Test:** Run with 5-10 participants
2. [ ] **Maze Integration:** Set up unmoderated study flow
3. [ ] **Main Study:** N=80 (40 per condition)
4. [ ] **Data Export:** Log repair times, click counts
5. [ ] **Analysis:** Compare metrics between conditions

### Future Development

1. [ ] Live LLM integration (replace scripted responses)
2. [ ] Real constraint detection (NLP-based)
3. [ ] Multi-task support with Task Shelf
4. [ ] Context Lens for explicit scope selection

---

## 8. Files Reference

### Pages
| File | Description |
|------|-------------|
| `BaselineChat.tsx` | Condition A: Chat-only with timer |
| `TreatmentChat.tsx` | Condition B: Chat + Constraint Sidebar |
| `ContextInventory.tsx` | Demo: Hex workspace for context composition |

### Components
| File | Description |
|------|-------------|
| `ChatInterface.tsx` | BLOOM-styled chat with messages |
| `ConstraintSidebar.tsx` | Persistent constraint list with click-to-reference |
| `ContextPalette.tsx` | Draggable context pills by category |
| `HexWorkspace.tsx` | 6-node hex grid with drag-drop |
| `TaskWizardPanel.tsx` | Legacy: Full 3-tab task manager |

### Core
| File | Description |
|------|-------------|
| `scenario.ts` | Career coaching script with 10 turns |
| `types.ts` | TypeScript interfaces |
| `index.css` | BLOOM design system CSS |

---

**Last Updated:** 2026-02-01
