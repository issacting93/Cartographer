import json
import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Paths
GRAPHS_DIR = "/Users/zac/Documents/Documents-it/Obsidian-Notes/Conferences/CUI_2026/CUI-Project/data/atlas_v2_production/graphs"
OUTPUT_DIR = "/Users/zac/Documents/Documents-it/Obsidian-Notes/Conferences/CUI_2026/CUI-Project/data/atlas_v2_production/visualizations"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "relational_friction_heatmap.png")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def analyze_friction():
    records = []
    
    graph_files = glob.glob(os.path.join(GRAPHS_DIR, "*.json"))
    print(f"Analyzing {len(graph_files)} graphs...")

    for file_path in graph_files:
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                continue
            
            nodes = data.get("nodes", [])
            
            # Map turns to their mode violations
            turn_mode_violations = {}
            # Map turns to their constraint violations
            turn_constraint_violations = {}
            
            for node in nodes:
                ntype = node.get("node_type")
                
                if ntype == "InteractionMode":
                    if node.get("is_violation"):
                        t_idx = node.get("turn_index")
                        v_type = node.get("violation_type")
                        turn_mode_violations[t_idx] = v_type
                
                if ntype == "ViolationEvent":
                    # Constraint violations have a constraint_id that isn't 'mode'
                    if node.get("constraint_id") != "mode":
                        t_idx = node.get("turn_index")
                        turn_constraint_violations[t_idx] = True

            # Calculate co-occurrence
            # We look for turns where BOTH happened
            for t_idx, m_violation in turn_mode_violations.items():
                has_c_violation = turn_constraint_violations.get(t_idx, False)
                records.append({
                    "mode_violation": m_violation,
                    "has_constraint_violation": "Constraint Violated" if has_c_violation else "Constraint Intact"
                })

    if not records:
        print("No records found.")
        return

    df = pd.DataFrame(records)
    
    # Create pivot table for heatmap
    pivot = df.groupby(["mode_violation", "has_constraint_violation"]).size().unstack(fill_value=0)
    
    # Normalize by row to see "If X mode violation happens, what % lead to constraint violation?"
    pivot_norm = pivot.div(pivot.sum(axis=1), axis=0) * 100

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_norm, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': '% Occurrence'})
    
    plt.title("Relational Friction: Correlation between Mode & Constraint Violations", fontsize=14, pad=20)
    plt.xlabel("Constraint Outcome", fontsize=12)
    plt.ylabel("Mode Violation Type", fontsize=12)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Heatmap saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_friction()
