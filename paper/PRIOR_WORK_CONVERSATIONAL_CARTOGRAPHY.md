# Prior Work: Conversational Cartography (Trajectory Analysis)

**Source:** `issacting93/Convo-topo`
**Date:** January 2026
**Subject:** Empirical Analysis of Relational-Affective Trajectories in Human-AI Conversation

This document summarizes the foundational findings from the "Conversational Cartography" project, which established the graph-structural approach to analyzing human-AI interaction. This work serves as the precursor to the current "Agency Collapse" and "Interactional Cartography" research.

---

## Executive Summary

The "Conversational Cartography" study analyzed **562 validated conversations** (Chatbot Arena, WildChat, OASST) using hierarchical and K-means clustering on **trajectory features** (spatial movement and emotional intensity) rather than static categorical labels.

The central finding: **Trajectory features account for 83.3% of cluster separation**, while categorical features (topic, purpose, role labels) account for only 16.7%. This demonstrates that **how conversations unfold through relational-affective space matters more than what they are ostensibly about.**

## Key Findings

### 1. Dynamics Over Categories
Hierarchical clustering revealed that **83.3% of feature importance** comes from trajectory characteristics:
*   **Spatial Trajectory (50.4%):** Path characteristics (straightness, length), final positioning, and movement patterns.
*   **Emotional Intensity (32.9%):** PAD-based intensity variation, peaks/valleys, and temporal trends.
*   **Categorical Features (16.7%):** Interaction patterns, roles, and purpose labels.

### 2. The "Same Role, Different Journey" Phenomenon
Conversations with **identical role classifications** (e.g., Information-Seeker → Expert-System) exhibited **41x to 82x variance differences** in affective trajectories.
*   **Example:** Two "Information-Seeker" conversations could be fundamentally different: one a "Detached Browsing" session (functional, flat trajectory) and the other an "Adversarial Testing" session (volatile, high-peaks trajectory).
*   **Implication:** Role labels predict the *destination* (final position) of a conversation, but not the *journey* (trajectory).

### 3. Relational Positioning Patterns
The analysis identified **7-9 distinct relational positioning patterns**, clustering conversations not by topic but by their movement through "interaction space":
1.  **StraightPath_Calm_Stable_Functional_QA (28.1%):** The most common pattern; efficient, low-emotion Q&A.
2.  **StraightPath_Functional_ProblemSolving (24.2%):** Deeper drift into functional territory, moderate intensity.
3.  **Valley_Volatile_Functional_QA (11.1%):** High variation but functional; suggests "learning" or "refinement".
4.  **StraightPath_SocialEmergent (6.4%):** Rare "social" interactions where the AI moves out of the functional quadrant.

### 4. Functional Dominance
**~72% of conversations** clustered in the Functional/Structured quadrant. This reflects a "sociotechnical construction" of AI as an instrumental tool, with the "Social-Emergent" quadrant remaining largely empty (<3%).

### 5. Temporal Anomaly Detection
Trajectory analysis proved effective at detecting interaction anomalies invisible to aggregate metrics.
*   **Breakdown Detection:** Sudden spikes in emotional intensity (PAD > 0.7) often signaled model breakdown or user frustration, even when the conversation was labeled "successful".
*   **Adversarial Detection:** "Rollercoaster" trajectories with frequent peaks and valleys characterized adversarial testing behavior.

## Methodology

The study utilized a **Conversational Cartography Pipeline**:
1.  **Classification:** GPT-4-based labelling of Human/AI roles (Social Role Theory) and interaction patterns.
2.  **PAD Scoring:** Per-turn scoring of Pleasure, Arousal, Dominance.
3.  **Trajectory Mapping:** Mapping conversations as paths in a 2D relational space (Functional ↔ Social / Aligned ↔ Divergent).
4.  **Clustering:** Unsupervised clustering (Hierarchical & K-means) on the extracted trajectory features.

## Feature Importance (Top Predictors)

1.  **max_intensity (7.37%):** Peak emotional moments are the strongest discriminator.
2.  **path_straightness (6.94%):** "Meandering" vs. "Direct" paths distinguish exploration from execution.
3.  **final_x (6.84%):** The final relational position matters, but less than the path taken.


---

## Evolution of Research: From Trajectories to Collapse

The current research ("Agency Collapse" and "Interactional Cartography") builds directly upon these findings but reframes the problem from **relational experience** to **structural governance**.

### Comparative Analysis

| Feature | Prior Work (Conversational Cartography) | Current Work (Agency Collapse) |
| :--- | :--- | :--- |
| **Primary Unit** | **Trajectory** (Path in relational space) | **Collapse** (Structural failure state) |
| **Key Metric** | **PAD Variance** (Emotional volatility) | **Agency Tax** (Repair effort relative to violations) |
| **Core Phenomenon** | "Same Role, Different Journey" | "The Repair Loop" |
| **Method** | Clustering on *affective* features (PAD) | Clustering on *structural* features (Repair, Stance, Specificity) |
| **New Visualization** | **Trajectory Mapping** (2D Cartesian) | **Polar Layout** (Clockwise Spiral) |
| **Key Finding** | Trajectories reveal hidden dynamics invisible to role labels | 50.4% of sustained conversations end in structural failure |
| **Theoretical Basis** | Social Role Theory (Attributes) | Conversation Analysis (Repair) & Grounding Theory |

### How Current Work Builds on Prior Work

1.  **From Symptom to Mechanism (The "Repair Labor" Insight):**
    *   **Prior Work:** Observed that "Adversarial" conversations have high volatility (Peaks/Valleys in PAD).
    *   **Current Work:** Reinterprets this volatility not as emotional instability, but as the **phenomenological surface of structural repair**. The "peaks" in emotional intensity are the user's escalating attempts to correct the system. We move from *symptom-based clustering* (affect) to *mechanism-based clustering* (structure).

2.  **From Descriptive to Diagnostic:**
    *   **Prior Work:** Treated roles (Information-Seeker, Expert) as stable **analytic anchors** to categorize interaction types.
    *   **Current Work:** Demonstrates that these anchors **erode under interactional load**. The "Detached" user in Convo-topo (Cluster 1) is re-diagnosed as the "Passive Accepter" (Cluster 1 in Agency Collapse) who has surrendered control because the governance structure failed.

3.  **From "User Experience" to "Governance":**
    *   **Prior Work:** Framed the problem as "experiential quality" (How does it feel?).
    *   **Current Work:** Frames the problem as **governance failure** (Who is in control?). UX degradation is shown to be downstream of the inability to maintain binding constraints.


---

## Theoretical Integration: The Research Arc

The progression from *Conversational Cartography* to *Agency Collapse* represents a shift from **phenomenology** (what interaction feels like) to **mechanism** (why it breaks).

### Three Layers of Analysis

We conceptualize this as a three-layer research program:

1.  **Layer 1: Detection (Conversational Cartography)**
    *   **Goal:** Map the terrain of interaction.
    *   **Finding:** Conversations exhibit distinct *trajectories* that role labels cannot explain.
    *   **Key Signal:** Affective volatility (PAD peaks/valleys).
    *   **Metric:** Volatility Variance.

2.  **Layer 2: Diagnosis (Agency Collapse)**
    *   **Goal:** Identify the causal mechanism of instability.
    *   **Finding:** Trajectory volatility is the downstream effect of a broken **Repair Loop**.
    *   **Key Signal:** Structural failure (Violations, Failed Repairs).
    *   **Metric:** Agency Tax (Repair Effort / Violations).

3.  **Layer 3: Intervention (Task-Constraint Architecture)**
    *   **Goal:** Fix the structural flaw.
    *   **Hypothesis:** Externalizing state (Context Inventory) reduces repair load and stabilizes the trajectory.
    *   **Key Signal:** Restoration of control.
    *   **Metric:** Repair Success Rate.

### Reinterpreting PAD: Affect as Labor

In this integrated view, the **emotional intensity (PAD)** measured in *Conversational Cartography* is reinterpreted as a **dependent variable** of governance failure in *Agency Collapse*.

*   **Then:** High Arousal/Dominance = "Adversarial User" or "Volatile Interaction."
*   **Now:** High Arousal/Dominance = **High Agency Tax.** The user is exerting effort to force the system back on track. The "emotionality" is actually **repair labor** under friction.

---

## Cluster Lineage: From Symptom to Diagnosis

We can now explicitly map the phenomenological clusters from Prior Work to the meaningful structural clusters in Current Work:

| Convo-topo Cluster (Symptom) | Agency Collapse Cluster (Mechanism) | The Connection |
| :--- | :--- | :--- |
| **Valley_Volatile (11%)**<br>*"High variance, frequent peaks/valleys"* | **Repair Failure (Cluster 0/3)**<br>*"High repair count, low success"* | The "volatility" is the visible signature of the Repair Loop. Users fight the system (peaks), fail (valleys), and fight again. |
| **StraightPath_Calm (28%)**<br>*"Flat trajectory, low intensity"* | **Passive Acceptance (Cluster 1)**<br>*"Low repair, high passivity"* | The "calmness" is often resignation. Users accept default outputs to avoid the cost of repair (Moral Hazard of Fluency). |
| **StraightPath_Functional (24%)**<br>*"Stable, goal-directed"* | **Task Maintained (Cluster 2)**<br>*"Low drift, effective repair"* | The ideal state. Constraints are respected, or repairs work immediately, requiring no "emotional" escalation. |

**Conclusion:** *Conversational Cartography* identified the *where* of breakdown (the volatile clusters); *Agency Collapse* explains the *why* (the repair trap).


