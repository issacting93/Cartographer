# Study 2 Protocol: The Maze/Figma Implementation
**Objective:** Run the "Violated Itinerary" experiment unmoderated.
**Platform:** Maze.co + Figma (Wizard of Oz).

## Why "Wizard of Oz"?
While you have the `Spectrum` code, deploying a live LLM app for unmoderated testing is risky:
1.  **Timing:** Real LLMs might not fail exactly at Turn 12.
2.  **Hosting:** Requires complex Vercel/Python deployment.
3.  **Measurement:** Maze excels at testing *prototypes*, not live apps.

By faking the chat with static Figma screens, we guarantee the "Violation" stimulus is identical for every participant (Science!).

---

## 1. The Figma Setup
You need two Figma Flows (one for each condition).

### Flow A: Chat-Only (Baseline)
1.  **Screen 1:** Instructions ("Plan a 3-day itinerary...").
2.  **Screen 2:** Long scrollable image of Turns 1-11 (everything normal).
3.  **Screen 3 (The Stimulus):** The Chat History + New Message from AI: *"I suggested breakfast at 8am..."* (Violation).
    *   *Action:* User must type in the text box.

### Flow B: Inventory (CII)
1.  **Screen 1:** Instructions.
2.  **Screen 2:** Long scrollable image (Turns 1-11) + **Visible Inventory Panel** on the right.
    *   *Inventory items:* [Diet: Vegan], [Time: >10am], [Budget: <$2k].
3.  **Screen 3 (The Stimulus):** AI Suggests 8am breakfast.
    *   *Action:* User clicks the `[Time: >10am]` node.

---

## 2. The Maze Setup
Create a Maze Project with two separate "Missions" (or use A/B split).

### Mission 1: Chat Repair
*   **Block 1 (Context):** "You are planning a trip. You have told the AI: 'No events before 10am'."
*   **Block 2 (Prototype):** Link to Figma Flow A (Screens 1-2).
*   **Block 3 (The Test):** Show Screen 3. Use an **Open Question** block asking: *"The AI just suggested an 8am breakfast. Please type your reply to the AI exactly as you would send it."*
    *   *Why:* This captures the **Repair text** for your analysis.

### Mission 2: Inventory Repair
*   **Block 1 (Context):** "Same task. This time, you have a 'Context Inventory' on the right."
*   **Block 2 (The Test):** Link to Figma Flow B (Screen 3). Set the **Success Path** to clicking the `[Time: >10am]` node.
    *   *Why:* This measures **Time-to-Correct** (clicks are faster than typing).

---

## 3. Analysis Plan
Once you have N=20 users:
1.  **Export CSV** from Maze.
2.  **Calculations:**
    *   `Condition A (Chat)`: Count words in the "Open Question" responses. (High Word Count = High Friction).
    *   `Condition B (Inventory)`: Measure "Time on Screen" for the click. (Low Time = Low Friction).
3.  **Compare:** The distinct difference between "Typing a Paragraph" vs "One Click" generates your $p < .001$ result.
