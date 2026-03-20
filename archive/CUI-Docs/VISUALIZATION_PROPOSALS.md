# Visualization Proposals: Integrating JSKG Data into CUI Paper

To strengthen the paper's empirical validity, we should update Figure 1 and Figure 2 to incorporate the findings from the O*NET 19k-task analysis.

---

## 1. Updated Figure 1: The Context Cliff (v2)
**Original**: Shows violation probability vs. turn number.
**Proposed Update**: Overlay the **"Object Moat"** variable.
- **Visual**: Two lines instead of one.
    - **Line A (Low Moat/Digital)**: Gradual cliff.
    - **Line B (High Moat/Human-Physical)**: Steep, early cliff (Turns 2-4).
- **Insight**: Demonstrates that "Context Collapse" is accelerated when the AI is blind to the object of work.

---

## 2. Updated Figure 2: The Agency Tax Map (v2)
**Original**: Repair effort vs. conversation length.
**Proposed Update**: Use the **Bimodal Distribution** (The Hollow Middle) as a background heatmap.
- **Visual**: Scatter plot of repair effort, where the background shows two high-density zones:
    - **Zone 1 (The Tech Tail)**: High repair effort for complex digital planning.
    - **Zone 2 (The Human Moat)**: Constant high repair effort for human-centric tasks.
- **Insight**: Shows that the "Tax" isn't a single line; it clusters where task state is most volatile.

---

## 3. New Figure: The Drift Risk Heatmap
**Proposed New Figure**: A 2D heatmap based on the JSKG synthesis.
- **X-Axis**: Action Potential (JSKG)
- **Y-Axis**: Object Constraint (JSKG)
- **Z-Color**: Predicted Role Drift (Atlas)
- **Insight**: High Action + High Constraint = **Immediate Role Collapse**. This provides the "mathematical" justification for why the Context Inventory Interface exists.

---

### Implementation Note:
I can help generate the data structures (JSON/CSV) for these plots so you can render them in your preferred plotting tool (Seaborn/Plotly).
