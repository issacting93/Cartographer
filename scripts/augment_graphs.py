#!/usr/bin/env python3
"""
Augment existing Atlas graphs with CA-grounded move types.

STRATEGY: Read existing graphs, add the 3 new move types and metadata
to Move nodes WITHOUT replacing existing LLM-detected violations.

1. For each graph, iterate Turn nodes and their associated Move nodes
2. Read the full message content from cached moves
3. Run ONLY the new detectors:
   - detect_acknowledge_constraint() → ACKNOWLEDGE_CONSTRAINT + grounding_evidence="demonstration"
   - detect_self_repair() → SELF_REPAIR + repair_organization="SISR"
   - SILENT_COMPLY inference → grounding_evidence="unmarked"
4. Tag existing ACCEPT_CONSTRAINT moves with grounding_evidence="token"
5. Tag existing REPAIR_INITIATE/ESCALATE with repair_organization
6. Add new Move nodes to the graph
7. Save updated graph

No LLM calls. No rebuild. All existing data preserved.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from atlas.move_classifier import (
    detect_acknowledge_constraint,
    detect_self_repair,
    classify_repair_organization,
    ACCEPT_PATTERNS,
)
from atlas.core.enums import MoveType as MT

CACHE_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "cache"
GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"


def load_cached_messages(conv_id: str) -> list:
    """Load cached moves file (has full message content)."""
    f = CACHE_DIR / "moves" / f"{conv_id}.json"
    if not f.exists():
        return []
    with open(f) as fh:
        return json.load(fh)


def augment_graph(graph_path: Path) -> bool:
    """Augment a single graph with CA-grounded move types. Returns True if modified."""
    with open(graph_path) as f:
        g = json.load(f)

    conv_id = graph_path.stem
    nodes = g.get("nodes", [])
    links = g.get("links", [])

    # Load message content from cache
    messages = load_cached_messages(conv_id)
    if not messages:
        return False

    # Build turn_index → content lookup
    turn_content = {}
    for msg in messages:
        ti = msg.get("turn_index", msg.get("turn_index"))
        if ti is not None:
            turn_content[ti] = {
                "content": msg.get("content", ""),
                "role": msg.get("role", ""),
            }

    # Index existing nodes
    move_nodes = [n for n in nodes if n.get("node_type") == "Move"]
    turn_nodes = [n for n in nodes if n.get("node_type") == "Turn"]

    # Build turn_index → list of move nodes
    turn_to_moves = defaultdict(list)
    for link in links:
        if link.get("edge_type") == "HAS_MOVE":
            src = link.get("source")
            tgt = link.get("target")
            turn_to_moves[src].append(tgt)

    move_by_id = {n.get("id"): n for n in move_nodes}
    turn_by_id = {n.get("id"): n for n in turn_nodes}

    modified = False
    new_nodes = []
    new_links = []

    # Track prev_had_propose for SILENT_COMPLY inference
    sorted_turns = sorted(turn_nodes, key=lambda t: t.get("turn_index", 0))
    prev_had_propose = False

    for turn_node in sorted_turns:
        turn_id = turn_node.get("id")
        turn_idx = turn_node.get("turn_index", 0)
        role = turn_node.get("role", "")
        msg_data = turn_content.get(turn_idx, {})
        content = msg_data.get("content", "")

        if not content:
            # Fallback to content_preview if available
            content = turn_node.get("content_preview", "")

        # Get existing moves for this turn
        existing_move_ids = turn_to_moves.get(turn_id, [])
        existing_move_types = set()
        for mid in existing_move_ids:
            m = move_by_id.get(mid)
            if m:
                existing_move_types.add(m.get("move_type", ""))

        # Count existing moves for sequence numbering
        next_seq = len(existing_move_ids)

        if role == "user":
            # Check if user proposed a constraint
            has_propose = "PROPOSE_CONSTRAINT" in existing_move_types

            # Tag existing REPAIR_INITIATE / ESCALATE with repair_organization
            for mid in existing_move_ids:
                m = move_by_id.get(mid)
                if m and m.get("move_type") in ("REPAIR_INITIATE", "ESCALATE"):
                    if not m.get("repair_organization"):
                        org = classify_repair_organization(content)
                        m["repair_organization"] = org
                        if m.get("move_type") == "ESCALATE":
                            m["repair_organization"] = "OIOR"
                        modified = True

            prev_had_propose = has_propose

        elif role == "assistant":
            # 1. Tag existing ACCEPT_CONSTRAINT with grounding_evidence="token"
            for mid in existing_move_ids:
                m = move_by_id.get(mid)
                if m and m.get("move_type") == "ACCEPT_CONSTRAINT":
                    if not m.get("grounding_evidence"):
                        m["grounding_evidence"] = "token"
                        modified = True

            # 2. Detect ACKNOWLEDGE_CONSTRAINT (understanding demonstration)
            if "ACKNOWLEDGE_CONSTRAINT" not in existing_move_types:
                ack_moves = detect_acknowledge_constraint(content)
                if ack_moves:
                    ack = ack_moves[0]
                    move_id = f"m_{conv_id}_{turn_idx}_{next_seq}"
                    new_nodes.append({
                        "id": move_id,
                        "node_type": "Move",
                        "move_type": "ACKNOWLEDGE_CONSTRAINT",
                        "text_span": ack.text_span,
                        "confidence": ack.confidence,
                        "method": ack.method,
                        "actor": ack.actor,
                        "grounding_evidence": "demonstration",
                    })
                    new_links.append({
                        "source": turn_id,
                        "target": move_id,
                        "edge_type": "HAS_MOVE",
                        "sequence": next_seq,
                    })
                    next_seq += 1
                    modified = True

            # 3. Detect SELF_REPAIR (only if no REPAIR_INITIATE pending)
            repair_initiated = any(
                move_by_id.get(mid, {}).get("move_type") in ("REPAIR_INITIATE", "ESCALATE")
                for mid in existing_move_ids
            )
            # Check previous turn for user repair initiation
            prev_turn_idx = turn_idx - 1
            prev_turn_id = f"t_{conv_id}_{prev_turn_idx}"
            prev_move_ids = turn_to_moves.get(prev_turn_id, [])
            repair_from_prev = any(
                move_by_id.get(mid, {}).get("move_type") in ("REPAIR_INITIATE", "ESCALATE")
                for mid in prev_move_ids
            )

            if "SELF_REPAIR" not in existing_move_types and not repair_from_prev:
                sr_moves = detect_self_repair(content)
                if sr_moves:
                    sr = sr_moves[0]
                    move_id = f"m_{conv_id}_{turn_idx}_{next_seq}"
                    new_nodes.append({
                        "id": move_id,
                        "node_type": "Move",
                        "move_type": "SELF_REPAIR",
                        "text_span": sr.text_span,
                        "confidence": sr.confidence,
                        "method": sr.method,
                        "actor": sr.actor,
                        "repair_organization": "SISR",
                    })
                    new_links.append({
                        "source": turn_id,
                        "target": move_id,
                        "edge_type": "HAS_MOVE",
                        "sequence": next_seq,
                    })
                    next_seq += 1
                    modified = True

            # 4. Infer SILENT_COMPLY
            has_accept_or_ack = bool(
                existing_move_types & {"ACCEPT_CONSTRAINT", "ACKNOWLEDGE_CONSTRAINT"}
            )
            # Also check newly added ACKNOWLEDGE_CONSTRAINT
            if any(n.get("move_type") == "ACKNOWLEDGE_CONSTRAINT"
                   for n in new_nodes if n.get("id", "").startswith(f"m_{conv_id}_{turn_idx}_")):
                has_accept_or_ack = True

            if (not has_accept_or_ack and prev_had_propose
                    and "SILENT_COMPLY" not in existing_move_types):
                move_id = f"m_{conv_id}_{turn_idx}_{next_seq}"
                new_nodes.append({
                    "id": move_id,
                    "node_type": "Move",
                    "move_type": "SILENT_COMPLY",
                    "text_span": "[unmarked compliance — no grounding evidence]",
                    "confidence": 0.7,
                    "method": "inferred",
                    "actor": "assistant",
                    "grounding_evidence": "unmarked",
                })
                new_links.append({
                    "source": turn_id,
                    "target": move_id,
                    "edge_type": "HAS_MOVE",
                    "sequence": next_seq,
                })
                next_seq += 1
                modified = True

            # Reset propose tracking (only applies to immediate next assistant turn)
            prev_had_propose = False

    if modified:
        g["nodes"].extend(new_nodes)
        g["links"].extend(new_links)
        with open(graph_path, "w") as f:
            json.dump(g, f, indent=2)

    return modified


def main():
    graph_files = sorted(GRAPHS_DIR.glob("*.json"))
    print(f"Found {len(graph_files)} graph files")

    augmented = 0
    unchanged = 0
    errors = 0

    for gf in graph_files:
        if "-error" in gf.stem:
            continue
        try:
            if augment_graph(gf):
                augmented += 1
            else:
                unchanged += 1
            if (augmented + unchanged) % 200 == 0:
                print(f"  Processed {augmented + unchanged}...")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error on {gf.stem}: {e}")

    print(f"\nDone: {augmented} augmented, {unchanged} unchanged, {errors} errors")


if __name__ == "__main__":
    main()
