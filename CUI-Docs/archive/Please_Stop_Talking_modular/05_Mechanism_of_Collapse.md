# Section 5: The Mechanism of Collapse

**Status:** DONE — Clean theoretical argument

---

## Content

Why do users drift? We argue that Agency Collapse is not a failure of user will, but an architectural failure of the chat interface. Drawing on the *Task-Constraint Architecture* (TCA), we model this as a breakdown in how representations (*R*) and constraints (*C*) are coupled.

---

## 5.1 The Log-as-State Limitation

**Status:** DONE

In Distributed Cognition, artifacts serve as "holding environments" for state. A GUI "holds" state in visible widgets (C_vis = High). A Chat UI "holds" state only in the linear history of the log (C_vis → 0 as *t* increases).

This creates **Epistemic Opacity**: as valid constraints scroll off-screen, they lose their status as active regulators of the system. The user is forced to treat the "Flow" (the latest message) as the only active representation.

### Theoretical Grounding
- Distributed Cognition: Hollan, Hutchins, & Kirsh (2000)
- Cognitive Artifacts: Norman (1991)

---

## 5.2 Restatement Friction as Constraint Violation

**Status:** DONE

When a constraint is violated, the user faces a choice:

1. **Repair (C_trans):** Spend a turn re-stating the constraint ("I said use Python"). This incurs a pure cost: it generates no new value, only restores old state.
2. **Accept (Drift):** Silent acceptance of the violation.

We define **Restatement Friction** as the cognitive load required to perform this repair. In standard chat, this friction is high because it requires linguistic formulation. Over time, users minimize cost by choosing Acceptance, leading to **Authority Drift**: the AI's default output becomes the *de facto* decision, not because it is correct, but because correcting it is too expensive.

### Key Contribution
- **Authority Drift** — Novel term describing how AI defaults become decisions by attrition

---

## Section Checklist

- [x] Builds on Section 3 (TCA)
- [x] Clear causal mechanism
- [x] Grounded in Distributed Cognition literature
- [x] Novel terms defined (Authority Drift)
- [x] No data claims requiring verification
