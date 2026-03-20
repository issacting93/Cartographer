#!/usr/bin/env python3
"""
Enrich Atlas Graph JSONs with PAD and SRT Classification Data
==============================================================
Reads graph JSONs from public/atlas_suite/data/graphs/,
looks up matching conversations in data/v2_unified/conversations/,
and adds:
  - PAD scores (pleasure, arousal, dominance, emotionalIntensity) to Turn nodes
  - SRT classification (humanRole, aiRole distributions + 8 dimensions) to Conversation nodes
  - Message content to Turn nodes (for transcript display)

Usage:
    python3 scripts/enrich_graphs.py [--dry-run]
"""

import json
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHS_DIR = PROJECT_ROOT / "public" / "atlas_suite" / "data" / "graphs"
CONVERSATIONS_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"


def find_conversation(graph_filename: str):
    """Find the v2_unified conversation matching a graph filename."""
    conv_id = graph_filename.replace(".json", "")
    conv_path = CONVERSATIONS_DIR / f"{conv_id}.json"
    if conv_path.exists():
        with open(conv_path) as f:
            return json.load(f)
    return None


def enrich_graph(graph_data: dict, conv_data: dict) -> dict:
    """Add PAD to Turn nodes and SRT to Conversation node."""
    messages = conv_data.get("messages", [])
    classification = conv_data.get("classification", {})

    # Index messages by position (turn_index = message index)
    msg_by_idx = {i: m for i, m in enumerate(messages)}

    for node in graph_data.get("nodes", []):
        # Enrich Turn nodes with PAD + content
        if node.get("node_type") == "Turn":
            turn_idx = node.get("turn_index")
            if turn_idx is not None and turn_idx in msg_by_idx:
                msg = msg_by_idx[turn_idx]
                pad = msg.get("pad", {})
                if pad:
                    node["pad_pleasure"] = pad.get("pleasure", pad.get("p", 0.5))
                    node["pad_arousal"] = pad.get("arousal", pad.get("a", 0.5))
                    node["pad_dominance"] = pad.get("dominance", pad.get("d", 0.5))
                    node["pad_intensity"] = pad.get("emotionalIntensity", 0.0)
                # Add full content for transcript display
                content = msg.get("content", "")
                node["content"] = content

        # Enrich Conversation node with SRT classification
        if node.get("node_type") == "Conversation" and classification:
            # Role distributions
            human_role = classification.get("humanRole", {})
            ai_role = classification.get("aiRole", {})
            if human_role.get("distribution"):
                node["human_role_dist"] = human_role["distribution"]
                node["human_role_confidence"] = human_role.get("confidence", 0)
            if ai_role.get("distribution"):
                node["ai_role_dist"] = ai_role["distribution"]
                node["ai_role_confidence"] = ai_role.get("confidence", 0)

            # 8 categorical dimensions
            for dim in ["interactionPattern", "powerDynamics", "emotionalTone",
                        "engagementStyle", "knowledgeExchange", "conversationPurpose",
                        "topicDepth", "turnTaking"]:
                dim_data = classification.get(dim, {})
                if dim_data.get("category"):
                    node[f"srt_{dim}"] = dim_data["category"]
                    node[f"srt_{dim}_conf"] = dim_data.get("confidence", 0)

    return graph_data


def main():
    parser = argparse.ArgumentParser(description="Enrich Atlas Graph JSONs")
    parser.add_argument('--dry-run', action='store_true', help="Preview changes")
    parser.add_argument('--graphs-div', type=Path, default=GRAPHS_DIR, help="Directory containing graph JSONs")
    parser.add_argument('--conversations-dir', type=Path, default=CONVERSATIONS_DIR, help="Directory containing conversation JSONs")
    args = parser.parse_args()

    graph_files = sorted(args.graphs_div.glob("*.json"))
    print(f"Graphs directory: {args.graphs_div}")
    print(f"Conversations directory: {args.conversations_dir}")
    print(f"Found {len(graph_files)} graph files")

    enriched = 0
    skipped = 0
    already_enriched = 0

    for gf in graph_files:
        if "-error" in gf.name:
            skipped += 1
            continue

        # Load graph
        with open(gf) as f:
            graph_data = json.load(f)

        # Check if already enriched
        turns = [n for n in graph_data.get("nodes", []) if n.get("node_type") == "Turn"]
        if turns and turns[0].get("pad_pleasure") is not None:
            already_enriched += 1
            continue

        # Find matching conversation
        conv_id = gf.name.replace(".json", "")
        conv_path = args.conversations_dir / f"{conv_id}.json"
        
        if not conv_path.exists():
            skipped += 1
            continue
            
        with open(conv_path) as f:
            conv_data = json.load(f)

        # Enrich
        graph_data = enrich_graph(graph_data, conv_data)

        if not args.dry_run:
            with open(gf, 'w') as f:
                json.dump(graph_data, f, indent=2, default=str)

        enriched += 1

    print(f"\nDone!")
    print(f"  Enriched: {enriched}")
    print(f"  Already enriched: {already_enriched}")
    print(f"  Skipped (no match or error): {skipped}")
    if args.dry_run:
        print("  (DRY RUN - no files written)")


if __name__ == "__main__":
    main()
