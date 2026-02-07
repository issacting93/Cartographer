#!/usr/bin/env python3
"""
Build Meta-Graph of Conversations.
Refactored to use Jaccard Similarity for linking.
"""

import json
import glob
import networkx as nx
from pathlib import Path

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", 
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "im"
}

def get_tokens(text):
    """Normalize and tokenize text, removing stopwords."""
    words = text.lower().replace(".", " ").replace(",", " ").split()
    return set(w for w in words if w.isalpha() and w not in STOPWORDS)

def build_meta_graph():
    base_dir = Path(__file__).parent.parent.parent
    graphs_dir = base_dir / "data/atlas_canonical/graphs"
    output_path = base_dir / "data/atlas_canonical/meta_graph.json"
    
    files = glob.glob(str(graphs_dir / "*.json"))
    print(f"Scanning {len(files)} files...")

    conversations = []
    
    for fpath in files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            
            conv_id = data.get("id") or Path(fpath).stem
            # Find Conversation node
            root = next((n for n in data.get("nodes", []) if n.get("node_type") == "Conversation"), {})
            
            # Extract all constraint texts
            constraints = [n.get("text", "") for n in data.get("nodes", []) if n.get("node_type") == "Constraint"]
            all_text = " ".join(constraints)
            tokens = get_tokens(all_text)
            
            conversations.append({
                "id": conv_id,
                "filename": Path(fpath).name,
                "source": root.get("source", "unknown"),
                "system": root.get("system", "unknown"),
                "stability": root.get("stability_class", "unknown"),
                "constraint_count": len(constraints),
                "turn_count": len([n for n in data.get("nodes", []) if n.get("node_type") == "Turn"]),
                "tokens": tokens  # Store tokens for comparison
            })
            
        except Exception as e:
            print(f"Skipping {fpath}: {e}")

    # Build Graph
    G = nx.Graph()
    
    for c in conversations:
        # Save node without the tokens (too heavy for JSON output)
        attrs = {k: v for k, v in c.items() if k != "tokens"}
        attrs["color"] = "#ef4444" if "chatbot_arena" in c["source"].lower() else "#3b82f6"
        G.add_node(c["id"], **attrs)
        
    print("Computing similarities...")
    # O(N^2) naive comparison - for 744 files it's ~270k comparisons, which is fine (sub-second)
    links_count = 0
    
    for i in range(len(conversations)):
        for j in range(i + 1, len(conversations)):
            c1 = conversations[i]
            c2 = conversations[j]
            
            # Skip if either has no constraints
            if not c1["tokens"] or not c2["tokens"]:
                continue
                
            # Jaccard Similarity of constraints
            intersection = len(c1["tokens"].intersection(c2["tokens"]))
            union = len(c1["tokens"].union(c2["tokens"]))
            
            if union > 0:
                jaccard = intersection / union
                # Threshold: 0.2 means 20% word overlap
                if jaccard > 0.2:
                    G.add_edge(c1["id"], c2["id"], weight=jaccard, type="semantic")
                    links_count += 1

    # Add categorical links? (e.g. same source + same stability class)
    # Let's keep it semantic-only for now to avoid the "Everything is connected" hairball.

    print(f"Built graph with {links_count} semantic links.")
    
    # Export
    d3_data = {
        "nodes": [d for n, d in G.nodes(data=True)],
        "links": [{"source": u, "target": v, "weight": d["weight"]} for u, v, d in G.edges(data=True)]
    }
    
    with open(output_path, 'w') as f:
        json.dump(d3_data, f, indent=2)
        
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    build_meta_graph()
