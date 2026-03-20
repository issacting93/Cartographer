import json
import numpy as np
from pathlib import Path
from collections import defaultdict

GRAPHS_DIR = Path("data/mental_health/graphs/graphs")

def main():
    files = sorted(GRAPHS_DIR.glob("*.json"))
    print(f"Analyzing {len(files)} graphs...")

    # Aggregators
    pad_scores = {"p": [], "a": [], "d": [], "intensity": []}
    human_roles = defaultdict(float)
    ai_roles = defaultdict(float)
    role_counts = 0
    
    dims = defaultdict(lambda: defaultdict(int))


    for fpath in files:
        with open(fpath) as f:
            g = json.load(f)
        
        # PAD Analysis (Turn nodes)
        for node in g.get("nodes", []):
            if node.get("node_type") == "Turn":
                if "pad_pleasure" in node:
                    pad_scores["p"].append(node["pad_pleasure"])
                    pad_scores["a"].append(node["pad_arousal"])
                    pad_scores["d"].append(node["pad_dominance"])
                    pad_scores["intensity"].append(node.get("pad_intensity", 0))

        # Role/SRT Analysis (Conversation node)
        # Note: SRT data is on the Conversation node
        conv_node = next((n for n in g.get("nodes", []) if n.get("node_type") == "Conversation"), None)
        if conv_node:
            # Roles (averaged distributions)
            if "human_role_dist" in conv_node:
                for role, score in conv_node["human_role_dist"].items():
                    human_roles[role] += score
                role_counts += 1
            
            if "ai_role_dist" in conv_node:
                for role, score in conv_node["ai_role_dist"].items():
                    ai_roles[role] += score
            
            # Dimensions
            for k, v in conv_node.items():
                if k.startswith("srt_") and not k.endswith("_conf"):
                    dim_name = k.replace("srt_", "")
                    dims[dim_name][v] += 1

    # --- MEAN SCORES ---
    print("\n=== PAD SCORES (Mean) ===")
    if pad_scores["p"]:
        print(f"Pleasure:  {np.mean(pad_scores['p']):.3f} (std: {np.std(pad_scores['p']):.3f})")
        print(f"Arousal:   {np.mean(pad_scores['a']):.3f} (std: {np.std(pad_scores['a']):.3f})")
        print(f"Dominance: {np.mean(pad_scores['d']):.3f} (std: {np.std(pad_scores['d']):.3f})")
        print(f"Intensity: {np.mean(pad_scores['intensity']):.3f}")
    else:
        print("No PAD data found.")

    print("\n=== HUMAN ROLES (Mean Probability) ===")
    if role_counts > 0:
        sorted_human = sorted(human_roles.items(), key=lambda x: x[1], reverse=True)
        for r, s in sorted_human:
            print(f"  {r}: {s/role_counts:.3f}")
    else:
        print("No Role data found.")

    print("\n=== AI ROLES (Mean Probability) ===")
    if role_counts > 0:
        sorted_ai = sorted(ai_roles.items(), key=lambda x: x[1], reverse=True)
        for r, s in sorted_ai:
            print(f"  {r}: {s/role_counts:.3f}")

    print("\n=== INTERACTION DIMENSIONS (Top Categories) ===")
    for dim, counts in dims.items():
        print(f"\n{dim}:")
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for cat, c in sorted_counts:
            print(f"  {cat}: {c} ({c/len(files)*100:.1f}%)")

if __name__ == "__main__":
    main()
