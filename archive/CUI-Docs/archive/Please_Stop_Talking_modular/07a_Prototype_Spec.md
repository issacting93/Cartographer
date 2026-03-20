# Prototype Spec: CII Experiment via Maze

**Decision:** Build 2 prototypes, test with Maze

---

## The Two Prototypes

| Prototype | Name | Description |
|-----------|------|-------------|
| **A** | Chat-Only | Standard scrolling chat interface |
| **B** | Chat + Inventory | Chat with persistent constraint sidebar (CII) |

---

## Core Interaction Flow (Both Prototypes)

```
1. User sees task briefing
2. User sets constraints (via chat or inventory)
3. AI responds (scripted, not real LLM)
4. [Turns 1-7: Normal interaction]
5. [Turn 8: FORCED VIOLATION - AI breaks constraints]
6. User attempts repair
7. AI acknowledges repair
8. Task complete → Survey
```

---

## Prototype A: Chat-Only

### Screens Needed

1. **Task Briefing** - Instructions + constraints to set
2. **Chat Interface** - Standard chat UI
   - User input field
   - Scrolling message history
   - "Send" button
3. **Completion Screen** - "Task complete"

### Scripted AI Responses

You'll fake the AI with pre-written responses. User "choices" branch to different scripts.

```
Turn 1: User sets constraints
  → AI: "Got it! I'll plan a trip with [constraints]. Let me start..."

Turn 2-7: Normal interaction
  → AI provides reasonable outputs

Turn 8: FORCED VIOLATION
  → AI: "For dinner, I recommend The Butcher's Block at 9am.
         The tasting menu is $650 per person..."
  (Violates: budget, dietary, time constraints)

Turn 9+: User types correction
  → AI: "You're right, let me fix that..."
```

### What Maze Tracks (Auto)
- Time on each screen
- What user types (if using text input)
- Click paths

---

## Prototype B: Chat + Inventory (CII)

### Screens Needed

1. **Task Briefing** - Same as A
2. **Chat + Sidebar Interface**
   - Left: Chat (same as A)
   - Right: Context Inventory panel
     - Goal node: "Plan 3-day trip"
     - Constraint nodes: "Budget < $500", "Vegetarian only", "No events before 10am"
     - Each node is clickable/highlightable
3. **Completion Screen** - Same as A

### CII Interactions to Build

| Action | Implementation |
|--------|----------------|
| **View constraints** | Always visible in sidebar |
| **Highlight/Flash** | User clicks node → visual pulse → AI acknowledges |
| **Edit** | User clicks node → inline edit → value updates |
| **Pin from chat** | Select text in chat → "Pin" button → adds to inventory |

### Scripted AI Behavior (CII)

```
Turn 8: FORCED VIOLATION (same as A)
  → AI: "For dinner, I recommend The Butcher's Block..."

Turn 9: User clicks "Vegetarian only" node
  → Node flashes/highlights
  → AI: "Correction acknowledged. Swapping for Green Earth Bistro."
  (ONE CLICK = REPAIR COMPLETE)
```

---

## Maze Study Structure

### Block 1: Onboarding
- Consent
- Demographics (age, AI experience, etc.)
- Random assignment to Condition A or B

### Block 2: Task 1 (Planning)
- Task briefing: "Plan a 3-day trip to Portland with these constraints..."
- Constraints: Budget $500, Vegetarian, No early mornings, Avoid downtown
- Prototype interaction (A or B)
- Forced violation at Turn 8

### Block 3: Task 2 (Writing)
- Task briefing: "Write a professional bio with these constraints..."
- Constraints: ≤120 words, No bullets, Include 2 phrases, Formal tone
- Prototype interaction (same condition)
- Forced violation at Turn 8

### Block 4: Post-Task Survey
- Perceived Control (5 items, 7-point Likert)
- Restatement Fatigue ("I had to repeat myself": Strongly Disagree → Strongly Agree)
- Open-ended: "What was frustrating about this interaction?"
- System Usability Scale (SUS) - optional

---

## Measures to Extract from Maze

### Behavioral (Automatic)

| Measure | What It Tells You | How Maze Gets It |
|---------|-------------------|------------------|
| **Time to Repair** | Seconds from violation to resolution | Screen timer |
| **Repair Clicks** | Number of clicks during repair | Click tracking |
| **Repair Path** | What did they try first? | Click sequence |
| **Total Task Time** | Overall efficiency | Session duration |
| **Misclick Rate** | Confusion indicator | Clicks outside targets |

### Survey (You Add)

| Measure | Scale | Items |
|---------|-------|-------|
| **Perceived Control** | 1-7 Likert | "I felt in control of the AI's behavior" (5 items) |
| **Restatement Fatigue** | 1-7 Likert | "I had to repeat myself to get what I wanted" |
| **Preference** | Binary | "Which interface would you prefer for complex tasks?" |
| **Open Feedback** | Text | "What was most frustrating?" |

---

## Minimum Viable Prototype (Figma)

If you're building in Figma for Maze:

### Chat-Only (Prototype A)
- 5-7 screens simulating turns
- User "types" by clicking pre-written options
- Branching based on repair choice

### Chat + CII (Prototype B)
- Same chat flow
- Add sidebar with clickable constraint nodes
- Clicking node → next screen shows "acknowledged" state

### Fidelity Level

| Approach | Effort | Validity |
|----------|--------|----------|
| **Low-fi wireframes** | 1-2 days | Lower (obvious it's fake) |
| **Mid-fi mockups** | 3-5 days | Good (feels like real app) |
| **High-fi + microinteractions** | 1-2 weeks | Best (immersive) |

**Recommendation:** Mid-fi is sufficient. Maze users know it's a prototype.

---

## Sample Size

| Confidence | N per condition | Total | Maze Cost (est.) |
|------------|-----------------|-------|------------------|
| Pilot | 10 | 20 | Free tier |
| Minimum viable | 25 | 50 | ~$200 |
| Solid | 40 | 80 | ~$350 |
| Robust | 60 | 120 | ~$500 |

**Recommendation:** Start with N=25 per condition (50 total). Enough for t-tests with large effect sizes.

---

## Hypotheses to Test

| ID | Hypothesis | Measure | Expected |
|----|------------|---------|----------|
| H1 | CII reduces repair effort | Repair Clicks | A > B |
| H2 | CII reduces repair time | Time to Repair | A > B |
| H3 | CII increases perceived control | Likert score | A < B |
| H4 | CII reduces restatement fatigue | Likert score | A > B |

---

## Build Checklist

### Prototype A (Chat-Only)
- [ ] Task briefing screen
- [ ] Chat UI with message history
- [ ] 7-8 scripted turns
- [ ] Forced violation at Turn 8
- [ ] 2-3 repair path options
- [ ] Completion screen

### Prototype B (Chat + CII)
- [ ] Same chat flow as A
- [ ] Sidebar with 4-5 constraint nodes
- [ ] Click-to-highlight interaction
- [ ] "Acknowledged" state after click
- [ ] Completion screen

### Maze Setup
- [ ] Create study with 2 conditions
- [ ] Add consent + demographics
- [ ] Add Task 1 (Planning)
- [ ] Add Task 2 (Writing)
- [ ] Add post-task survey
- [ ] Test with 3-5 pilots
- [ ] Launch recruitment

---

## Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| Prototype A | 2-3 days | Figma file |
| Prototype B | 2-3 days | Figma file |
| Maze setup | 1 day | Live study |
| Pilot (N=10) | 1-2 days | Feedback, fixes |
| Main study (N=50) | 3-5 days | Data |
| Analysis | 2-3 days | Results for paper |

**Total: ~2 weeks** if focused

---

## Next Steps

1. [ ] Decide: Figma or code prototype?
2. [ ] Design chat UI (shared between A and B)
3. [ ] Design CII sidebar for B
4. [ ] Write scripted AI responses
5. [ ] Build in Figma / connect to Maze
6. [ ] Write survey questions
7. [ ] Pilot test
8. [ ] Launch
