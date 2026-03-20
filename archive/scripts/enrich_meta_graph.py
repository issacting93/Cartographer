#!/usr/bin/env python3
"""
Enrich meta_graph.json with SRT + PAD summary data per conversation node.

Reads individual graph JSONs (already enriched with PAD/SRT) and adds:
  - dominant_human_role, dominant_ai_role (top role by weight)
  - human_role_dist, ai_role_dist (full distributions)
  - interaction_pattern, emotional_tone, power_dynamics, engagement_style
  - mean_pleasure, mean_arousal, mean_dominance (PAD averages)
  - drift_velocity (violations / turns)
  - violation_count, repair_count

Usage:
    python3 scripts/enrich_meta_graph.py
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
META_GRAPH = PROJECT_ROOT / "public" / "atlas_suite" / "data" / "meta_graph.json"
GRAPHS_DIR = PROJECT_ROOT / "public" / "atlas_suite" / "data" / "graphs"


def get_dominant(dist):
    """Return the role with highest weight from a distribution dict."""
    if not dist:
        return None
    return max(dist.items(), key=lambda x: x[1])[0]


def enrich_node(node):
    """Look up the graph JSON for this node and extract SRT + PAD summary."""
    filename = node.get("filename")
    if not filename:
        return node

    graph_path = GRAPHS_DIR / filename
    if not graph_path.exists():
        return node

    with open(graph_path) as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])

    # Find Conversation node for SRT data
    conv = next((n for n in nodes if n.get("node_type") == "Conversation"), None)
    if conv:
        # Role distributions
        h_dist = conv.get("human_role_dist")
        a_dist = conv.get("ai_role_dist")
        if h_dist:
            node["human_role_dist"] = h_dist
            node["dominant_human_role"] = get_dominant(h_dist)
        if a_dist:
            node["ai_role_dist"] = a_dist
            node["dominant_ai_role"] = get_dominant(a_dist)

        # SRT categorical dimensions
        for dim in ["interactionPattern", "powerDynamics", "emotionalTone",
                     "engagementStyle", "knowledgeExchange", "conversationPurpose",
                     "topicDepth", "turnTaking"]:
            val = conv.get(f"srt_{dim}")
            if val:
                node[dim] = val

    # PAD summary from Turn nodes
    turns = [n for n in nodes if n.get("node_type") == "Turn"]
    pad_turns = [t for t in turns if t.get("pad_pleasure") is not None]

    if pad_turns:
        node["mean_pleasure"] = round(sum(t["pad_pleasure"] for t in pad_turns) / len(pad_turns), 3)
        node["mean_arousal"] = round(sum(t["pad_arousal"] for t in pad_turns) / len(pad_turns), 3)
        node["mean_dominance"] = round(sum(t["pad_dominance"] for t in pad_turns) / len(pad_turns), 3)
        node["mean_intensity"] = round(
            sum(t.get("pad_intensity", 0) for t in pad_turns) / len(pad_turns), 3)

        # Human vs AI dominance
        human_turns = [t for t in pad_turns if t.get("role") == "user"]
        ai_turns = [t for t in pad_turns if t.get("role") in ("assistant", "model")]
        if human_turns:
            node["human_mean_dominance"] = round(
                sum(t["pad_dominance"] for t in human_turns) / len(human_turns), 3)
        if ai_turns:
            node["ai_mean_dominance"] = round(
                sum(t["pad_dominance"] for t in ai_turns) / len(ai_turns), 3)

    # Violation and repair counts
    violations = [n for n in nodes if n.get("node_type") == "ViolationEvent"]
    repairs = [n for n in nodes if n.get("node_type") == "Move"
               and n.get("move_type", "").startswith("REPAIR")]

    node["violation_count"] = len(violations)
    node["repair_count"] = len(repairs)

    if turns:
        node["drift_velocity"] = round(len(violations) / len(turns), 3)
    else:
        node["drift_velocity"] = 0

    return node


def main():
    with open(META_GRAPH) as f:
        data = json.load(f)

    print(f"Enriching {len(data['nodes'])} meta-graph nodes...")

    enriched = 0
    for i, node in enumerate(data["nodes"]):
        before_keys = len(node)
        data["nodes"][i] = enrich_node(node)
        if len(data["nodes"][i]) > before_keys:
            enriched += 1

    with open(META_GRAPH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Done! Enriched {enriched} / {len(data['nodes'])} nodes")

    # Print a sample
    sample = next((n for n in data["nodes"] if n.get("dominant_human_role")), None)
    if sample:
        print(f"\nSample node: {sample['id']}")
        for k in ["dominant_human_role", "dominant_ai_role", "interactionPattern",
                   "emotionalTone", "powerDynamics", "mean_pleasure", "mean_arousal",
                   "mean_dominance", "drift_velocity", "violation_count"]:
            print(f"  {k}: {sample.get(k, '—')}")


if __name__ == "__main__":
    main()
