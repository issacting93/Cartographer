# Section 8: Results

## 8.1 Method 1: The Passive Attractor (Log Analysis)

Our analysis of $N=562$ interaction traces reveals a strong structural bias toward low-agency states.

### Trajectory Dominance
Hierarchical clustering confirms that **83.3% of feature variance** is explained by trajectory characteristics rather than static role labels. This validates the "Agency as Trajectory" hypothesis: users drift into roles based on the interaction's momentum.

### The "StraightPath" Baseline
The most common pattern ($28.1\%$) is the *StraightPath_Calm_Stable* trajectory. In this state, the user acts as a "Provider" ($R \to 1$) and the system as an "Expert" ($R \to 5$). This represents the path of least resistance: the user minimizes constraint specification to meaningful maintain flow.

### The Facilitator Null Result
The "Null Result" of the Learning-Facilitator pattern ($0.1\%$) provides strong evidence that current interfaces actively discourage Socratic interaction.

## 8.2 Method 2: The Efficacy of Repair (Maze Experiment)

*Note: Results below are from preliminary validation (N=80).*

### Repair Friction
Participants in the **Inventory** condition spent significantly fewer turns correcting the model ($M=0.35$) compared to the **Chat-Only** baseline ($M=3.82$). The **Restatement Burden** dropped from $42\%$ (nearly half of user input spent policing the model) to just $4\%$ with the inventory.

| Metric | Chat-Only | Inventory | Effect |
|--------|-----------|-----------|--------|
| Repair Turns | $3.82 \pm 1.2$ | $0.35 \pm 0.5$ | $p < .001$ |
| Time-to-Correct | $45.2s$ | $4.1s$ | $p < .001$ |
| Perceived Control | $2.1 / 5$ | $4.6 / 5$ | $p < .001$ |

## 8.3 Qualitative Analysis: The Physics of Repair

### Case Study A: The Passive Attractor (Trace `wc-294`)
A user requests a Python script with rate limiting. At Turn 6, they ask for a recursive version. The model provides the recursion but drops the rate-limiting logic (Context Drift).
> **User (T7):** "Wait, where did the rate limit go?"
> **AI (T7):** "Apologies..." *(hallucinates fix)*
> **User (T8):** "No, that's blocking the main loop."
> **AI (T8):** "You are correct..." *(breaks recursion)*
> **User (T9):** "Whatever, the first version was fine."

**Analysis:** This illustrates **Agency Collapse**. The cognitive cost of repairing the complex state exceeded the value of the constraint, leading the user to abandon their goal.

### Case Study B: Instrumental Repair (Trace `cii-04`)
In the Inventory condition, a user set the constraint `[Diet: Vegan]`. The model suggested a steakhouse.
> **AI (T15):** "For dinner, I recommend 'The Butcher's Block'..."
> **User (T16):** *[Clicks 'Diet: Vegan' node]*
> **AI (T16):** "Correction acknowledged. Swapping for 'Green Earth Bistro'."

**Analysis:** The repair cost was near-zero (~2s). By "pointing" to an existing truth rather than restating it, the user maintained the constraint without breaking flow.
