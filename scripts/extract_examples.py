#!/usr/bin/env python3
"""
Extract Representative Examples

Finds the most representative conversations (closest to cluster centroid)
for each archetype to serve as qualitative examples in the report.

Usage: python scripts/extract_examples.py
"""

import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances_argmin_min

# Feature columns used for clustering (must match cluster.py)
FEATURES = [
    'repair_count',
    'specificity_delta',
    'stance_delta',
    'politeness_delta',
    'passive_rate',
    'constraint_count',
    'verbatim_repeats',
    'mean_user_length',
]

def load_data(clustered_path: Path):
    """Load clustered data."""
    with open(clustered_path, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def get_original_filepath(conv_id: str, source_dir: Path) -> Path:
    """Find the original JSON file."""
    # Assuming flat directory structure as per features_llm.py usage
    # Try direct match
    p = source_dir / f"{conv_id}.json"
    if p.exists():
        return p
    
    # Try searching (slow, but robust)
    found = list(source_dir.glob(f"**/{conv_id}.json"))
    if found:
        return found[0]
    return None

def format_conversation(filepath: Path) -> str:
    """Format a conversation JSON into readable text."""
    if not filepath or not filepath.exists():
        return "[File not found]"
    
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    transcript = []
    messages = data if isinstance(data, list) else data.get('messages', [])
    
    # Limit to reasonable length
    for msg in messages[:20]: # First 20 turns
        role = msg.get('role', 'unknown').upper()
        content = msg.get('content', '')
        # Truncate long messages
        if len(content) > 300:
            content = content[:300] + "... [truncated]"
        transcript.append(f"**{role}**: {content}")
        
    return "\n\n".join(transcript)

def main():
    parser = argparse.ArgumentParser(description="Extract representative examples")
    parser.add_argument("--clustered", "-c", required=True, help="Clustered data JSON")
    parser.add_argument("--stats", "-s", required=True, help="Cluster stats CSV (for centroids)")
    parser.add_argument("--source", "-d", required=True, help="Source directory of conversation JSONs")
    parser.add_argument("--archetypes", "-a", required=True, help="Archetypes JSON map")
    parser.add_argument("--output", "-o", required=True, help="Output markdown file")
    args = parser.parse_args()
    
    print("Loading data...")
    df = load_data(Path(args.clustered))
    stats_df = pd.read_csv(args.stats)
    with open(args.archetypes, 'r') as f:
        archetype_list = json.load(f)
    archetype_map = {item['cluster']: item['archetype'] for item in archetype_list}
    
    source_dir = Path(args.source)
    
    # Prepare features
    X = df[FEATURES].values
    X = np.nan_to_num(X, nan=0.0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    md_output = "# Qualitative Examples of Agency Collapse Archetypes\n\n"
    md_output += "Representative conversations selected by minimum Euclidean distance to cluster centroids.\n\n"
    
    print("Finding representatives...")
    
    for cluster_id in sorted(df['cluster'].unique()):
        # Get archetype name
        archetype = archetype_map.get(cluster_id, f"Cluster {cluster_id}")
        
        # Get centroid features
        cluster_row = stats_df[stats_df['cluster'] == cluster_id]
        if cluster_row.empty:
            continue
            
        # Get points in this cluster
        cluster_mask = df['cluster'] == cluster_id
        cluster_indices = np.where(cluster_mask)[0]
        
        if len(cluster_indices) == 0:
            continue
            
        cluster_X = X_scaled[cluster_indices]
        
        # Calculate centroid of *this* cluster in scaled space
        centroid = cluster_X.mean(axis=0).reshape(1, -1)
        
        # Find closest point
        distances = np.linalg.norm(cluster_X - centroid, axis=1)
        closest_idx_in_cluster = np.argmin(distances)
        global_idx = cluster_indices[closest_idx_in_cluster]
        
        representative = df.iloc[global_idx]
        conv_id = representative['conversation_id']
        dist = distances[closest_idx_in_cluster]
        
        print(f"Cluster {cluster_id} ({archetype}): Closest is {conv_id} (dist={dist:.2f})")
        
        # Get Transcript
        original_file = get_original_filepath(conv_id, source_dir)
        transcript = format_conversation(original_file)
        
        md_output += f"## Archetype: {archetype} (Cluster {cluster_id})\n"
        md_output += f"**Representative ID:** `{conv_id}`\n"
        md_output += f"**Collapse:** {representative.get('collapse', 'Unknown')}\n"
        md_output += f"**Stats:** Repair={representative.get('repair_count')}, Passive={representative.get('passive_rate'):.2f}, StanceΔ={representative.get('stance_delta'):.2f}\n\n"
        md_output += "### Transcript Snippet\n\n"
        md_output += transcript + "\n\n"
        md_output += "---\n\n"
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(md_output)
        
    print(f"✅ Saved qualitative examples to {output_path}")

if __name__ == "__main__":
    main()
