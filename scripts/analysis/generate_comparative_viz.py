#!/usr/bin/env python3
"""
Generate Comparative Visualization
----------------------------------
Correlates Structural Features (Repair Count) with Phenomenological Features (PAD Volatility)
and generates an interactive HTML scatterplot.

Usage:
    python3 scripts/analysis/generate_comparative_viz.py
"""

import json
import statistics
from pathlib import Path
import math

INPUT_DIR = Path("data/atlas_with_pad")
OUTPUT_HTML = Path("public/comparative_diagnostics.html")

def calculate_volatility(pad_scores):
    """
    Calculate trajectory volatility (mean Euclidean distance between consecutive PAD points).
    """
    if len(pad_scores) < 2:
        return 0.0
        
    distances = []
    for i in range(len(pad_scores) - 1):
        p1 = pad_scores[i]
        p2 = pad_scores[i+1]
        
        # Euclidean distance in 3D PAD space
        dist = math.sqrt(
            (p1['pleasure'] - p2['pleasure'])**2 +
            (p1['arousal'] - p2['arousal'])**2 +
            (p1['dominance'] - p2['dominance'])**2
        )
        distances.append(dist)
        
    return statistics.mean(distances) if distances else 0.0

def analyze_conversation(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        nodes = data.get("nodes", [])
        
        # 1. Structural Features (Repair Count)
        # Count ViolationEvent nodes where was_repaired=False (or just total violations)
        violation_nodes = [n for n in nodes if n.get("node_type") == "ViolationEvent"]
        repair_count = len(violation_nodes)
        
        # 2. Phenomenological Features (Volatility)
        turn_nodes = [n for n in nodes if n.get("node_type") == "Turn"]
        turn_nodes.sort(key=lambda x: x.get("turn_index", 0))
        
        pad_scores = []
        for turn in turn_nodes:
            pad = turn.get("pad_attributes")
            if pad:
                pad_scores.append(pad)
                
        volatility = calculate_volatility(pad_scores)
        
    # Metadata
        conv_node = next((n for n in nodes if n.get("node_type") == "Conversation"), {})
        
        return {
            "id": conv_node.get("conv_id", file_path.stem),
            "repair_count": repair_count,
            "volatility": volatility,
            "source": conv_node.get("source", "unknown"),
            "total_turns": len(turn_nodes),
            "turns": [
                {
                    "index": t.get("turn_index"),
                    "role": t.get("role"),
                    "pad": t.get("pad_attributes")
                }
                for t in turn_nodes if t.get("pad_attributes")
            ]
        }
        
    except Exception as e:
        print(f"Error analyzing {file_path.name}: {e}")
        return None

def main():
    if not INPUT_DIR.exists():
        print(f"Input directory {INPUT_DIR} does not exist. Run bridge_pad_scoring.py first.")
        return

    files = list(INPUT_DIR.glob("*.json"))
    print(f"Analyzing {len(files)} files...")
    
    data_points = []
    for f in files:
        result = analyze_conversation(f)
        if result:
            data_points.append(result)
            
    if not data_points:
        print("No data points found.")
        return

    # Output full JSON data as JS variable for dashboard (avoids CORS)
    output_js = Path("public/dashboard_data.js")
    with open(output_js, 'w') as f:
        f.write("const DASHBOARD_DATA = ")
        json.dump(data_points, f)
        f.write(";")
    print(f"✅ Generated data: {output_js}")

    # Generate legacy HTML (optional, or we can just point to the new dashboard)
    # keeping the legacy one for now but pointing out the new data source


if __name__ == "__main__":
    main()
