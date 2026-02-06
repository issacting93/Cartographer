#!/usr/bin/env python3
"""
Atlas Graph Constructor

Builds a NetworkX MultiDiGraph per conversation from Move, Mode, and
Constraint Tracker annotations.

Node types (6): Conversation, Turn, Move, Constraint, InteractionMode, ViolationEvent
Edge types (10): CONTAINS, HAS_MOVE, INTRODUCES, RATIFIES, VIOLATES, REPAIRS,
                 OPERATES_IN, TRIGGERS, NEXT, ABANDONS

Export formats: JSON (node-link for D3.js) and GEXF (for Gephi).
"""

import json
from typing import List, Optional, Tuple
from pathlib import Path

try:
    import networkx as nx
except ImportError:
    raise ImportError("networkx required: pip install networkx")

from atlas.core.enums import NodeType as NT, EdgeType as ET, MoveType as MT, ConstraintState as CS
from atlas.core.models import (
    Conversation, Turn, Move, Constraint, 
    ViolationEvent, InteractionModeAnnotation
)
from atlas.utils import (
    ConversationConstraintTrack,
    ModeAnnotation
)
from atlas.graph.validators import validate_graph_schema


# ============= Helpers =============

def state_at_turn(state_history: List[Tuple[int, str]], t: int) -> Optional[str]:
    """Find the effective constraint state at turn t."""
    last = None
    for h_turn, h_state in state_history:
        if h_turn > t:
            break
        last = h_state
    return last


# ============= Node Constructors =============

def add_conversation_node(
    G: nx.MultiDiGraph,
    conv_id: str,
    metadata: dict,
):
    """Add the root Conversation node."""
    conv = Conversation(
        conv_id=conv_id,
        source=metadata.get("source", ""),
        domain=metadata.get("domain", ""),
        total_turns=metadata.get("total_turns", 0),
        stability_class=metadata.get("stability_class"),
        task_architecture=metadata.get("task_architecture"),
        constraint_hardness=metadata.get("constraint_hardness"),
        task_goal=metadata.get("task_goal", "")[:200],
    )
    G.add_node(f"conv_{conv_id}", node_type=NT.CONVERSATION, **conv.model_dump())


def add_turn_nodes(
    G: nx.MultiDiGraph,
    conv_id: str,
    messages_with_moves: List[dict],
):
    """Add Turn nodes with CONTAINS edges from Conversation and NEXT edges."""
    conv_node = f"conv_{conv_id}"
    prev_turn_node = None

    for msg in messages_with_moves:
        turn_idx = msg.get("turn_index", 0)
        role = msg.get("role", "user")
        content = msg.get("content", "")

        turn_node = f"t_{conv_id}_{turn_idx}"

        turn = Turn(
            turn_index=turn_idx,
            role=role,
            content_length=len(content),
            content_preview=" ".join(content[:120].split()),
            move_count=len(msg.get("moves", [])),
        )
        G.add_node(turn_node, node_type=NT.TURN, **turn.model_dump())

        G.add_edge(conv_node, turn_node, edge_type=ET.CONTAINS, order=turn_idx)

        if prev_turn_node:
            G.add_edge(prev_turn_node, turn_node, edge_type=ET.NEXT, order=turn_idx)

        prev_turn_node = turn_node


def add_move_nodes(
    G: nx.MultiDiGraph,
    conv_id: str,
    messages_with_moves: List[dict],
):
    """Add Move nodes with HAS_MOVE edges from their parent Turn."""
    for msg in messages_with_moves:
        turn_idx = msg.get("turn_index", 0)
        turn_node = f"t_{conv_id}_{turn_idx}"
        moves = msg.get("moves", [])

        for seq, move in enumerate(moves):
            move_node = f"m_{conv_id}_{turn_idx}_{seq}"

            m = Move(
                move_type=move.get("move_type", MT.GENERATE_OUTPUT),
                text_span=move.get("text_span", "")[:120],
                confidence=move.get("confidence", 0.0),
                method=move.get("method", ""),
                actor=move.get("actor", ""),
            )
            G.add_node(move_node, node_type=NT.MOVE, **m.model_dump())

            G.add_edge(turn_node, move_node, edge_type=ET.HAS_MOVE, sequence=seq)


def add_constraint_nodes(
    G: nx.MultiDiGraph,
    conv_id: str,
    constraint_track: ConversationConstraintTrack,
    messages_with_moves: List[dict],
):
    """
    Add Constraint nodes and link them to introducing Moves via INTRODUCES edges.
    Also add ABANDONS edges where applicable.
    """
    for c in constraint_track.constraints:
        constraint_node = f"c_{conv_id}_{c.constraint_id}"

        constraint = Constraint(
            constraint_id=c.constraint_id,
            text=c.text[:200],
            hardness=c.hardness,
            current_state=c.current_state,
            state_history=c.state_history,
            introduced_at=c.introduced_at,
            times_violated=c.times_violated,
            times_repaired=c.times_repaired,
            lifespan=c.lifespan,
        )
        G.add_node(constraint_node, node_type=NT.CONSTRAINT, **constraint.model_dump())

        # Link to introducing Move (PROPOSE_CONSTRAINT in the introduction turn)
        intro_turn = c.introduced_at
        turn_node = f"t_{conv_id}_{intro_turn}"

        # Find the PROPOSE_CONSTRAINT move in that turn
        for msg in messages_with_moves:
            if msg.get("turn_index") == intro_turn:
                for seq, move in enumerate(msg.get("moves", [])):
                    if move.get("move_type") == MT.PROPOSE_CONSTRAINT:
                        move_node = f"m_{conv_id}_{intro_turn}_{seq}"
                        if G.has_node(move_node):
                            G.add_edge(move_node, constraint_node, edge_type=ET.INTRODUCES)
                break

        # Link ABANDON moves
        for entry in (c.state_history or []):
            if not entry or len(entry) < 2:
                continue
            turn_idx, state = entry
            if state == CS.ABANDONED:
                # Find ABANDON_CONSTRAINT move in that turn
                for msg in messages_with_moves:
                    if msg.get("turn_index") == turn_idx:
                        for seq, move in enumerate(msg.get("moves", [])):
                            if move.get("move_type") == MT.ABANDON_CONSTRAINT:
                                move_node = f"m_{conv_id}_{turn_idx}_{seq}"
                                if G.has_node(move_node):
                                    G.add_edge(move_node, constraint_node, edge_type=ET.ABANDONS)
                                break
                        break


def add_violation_events(
    G: nx.MultiDiGraph,
    conv_id: str,
    constraint_track: ConversationConstraintTrack,
    messages_with_moves: List[dict],
    violation_idx_start: int = 0
) -> int:
    """
    Add ViolationEvent nodes for both constraint violations and mode violations.
    Link to triggering Turn (TRIGGERS) and violated Constraint (VIOLATES).
    Link repair Moves via REPAIRS edge.
    """
    violation_idx = violation_idx_start

    for c in constraint_track.constraints:
        constraint_node = f"c_{conv_id}_{c.constraint_id}"
        violation_ord = 0

        for entry in (c.state_history or []):
            if not entry or len(entry) < 2:
                continue
            turn_idx, state = entry
            if state != CS.VIOLATED:
                continue

            violation_ord += 1
            ve_node = f"v_{conv_id}_{violation_idx}"
            violation_idx += 1

            # Check if this violation was later repaired
            was_repaired = False
            for later_entry in (c.state_history or []):
                if not later_entry or len(later_entry) < 2:
                    continue
                later_turn, later_state = later_entry
                if later_turn > turn_idx and later_state in (CS.REPAIRED, CS.ACTIVE):
                    was_repaired = True
                    break

            ve = ViolationEvent(
                violation_idx=violation_idx,
                turn_index=turn_idx,
                constraint_id=c.constraint_id,
                violation_type="constraint_violation",
                was_repaired=was_repaired,
                violation_ord=violation_ord,
            )
            G.add_node(ve_node, node_type=NT.VIOLATION_EVENT, **ve.model_dump())

            # TRIGGERS edge from the turn
            turn_node = f"t_{conv_id}_{turn_idx}"
            if G.has_node(turn_node):
                G.add_edge(turn_node, ve_node, edge_type=ET.TRIGGERS)

            # VIOLATES edge from the violation event to the constraint
            if G.has_node(constraint_node):
                G.add_edge(ve_node, constraint_node, edge_type=ET.VIOLATES, 
                           violation_ord=violation_ord, at_turn=turn_idx)

            # REPAIRS edge from repair turns
            if was_repaired:
                for msg in messages_with_moves:
                    msg_idx = msg.get("turn_index", 0)
                    if msg_idx <= turn_idx:
                        continue
                    has_repair = False
                    for move in msg.get("moves", []):
                        if move and move.get("move_type") in (MT.REPAIR_INITIATE, MT.REPAIR_EXECUTE):
                            repair_turn = f"t_{conv_id}_{msg_idx}"
                            if G.has_node(repair_turn):
                                G.add_edge(repair_turn, ve_node, edge_type=ET.REPAIRS)
                            has_repair = True
                            break
                    if has_repair:
                        break

    return violation_idx


def add_mode_violation_events(
    G: nx.MultiDiGraph,
    conv_id: str,
    mode_annotations: List[ModeAnnotation],
    violation_start_idx: int,
    messages_with_moves: List[dict],
):
    """Add ViolationEvent nodes for mode violations."""
    idx = violation_start_idx

    for ann in mode_annotations:
        if not ann.violation_type:
            continue

        ve_node = f"v_{conv_id}_{idx}"
        idx += 1
        ve = ViolationEvent(
            violation_idx=idx - 1,
            turn_index=ann.turn_index,
            constraint_id="mode",
            violation_type=ann.violation_type,
            was_repaired=False,  # Mode violations currently don't track repair
            violation_ord=1,
        )
        # Store the raw annotation data as well
        node_data = ve.model_dump()
        node_data.update({
            "user_requested": ann.user_requested,
            "ai_enacted": ann.ai_enacted,
            "confidence": ann.confidence,
            "method": ann.method
        })
        G.add_node(ve_node, node_type=NT.VIOLATION_EVENT, **node_data)

        # TRIGGERS edge from the AI turn
        # The AI turn is the first assistant turn at or after ann.turn_index + 1
        ai_turn_idx = None
        for msg in messages_with_moves:
            if msg.get("turn_index", -1) > ann.turn_index and msg.get("role") == "assistant":
                ai_turn_idx = msg.get("turn_index")
                break
        
        if ai_turn_idx is not None:
            ai_turn_node = f"t_{conv_id}_{ai_turn_idx}"
            if G.has_node(ai_turn_node):
                G.add_edge(ai_turn_node, ve_node, edge_type=ET.TRIGGERS)


def add_mode_nodes(
    G: nx.MultiDiGraph,
    conv_id: str,
    mode_annotations: List[ModeAnnotation],
):
    """Add InteractionMode nodes and OPERATES_IN edges."""
    for ann in mode_annotations:
        mode_node = f"mode_{conv_id}_{ann.turn_index}"

        G.add_node(mode_node, node_type=NT.INTERACTION_MODE, **ann.model_dump())

        # OPERATES_IN from user turn
        user_turn = f"t_{conv_id}_{ann.turn_index}"
        if G.has_node(user_turn):
            G.add_edge(user_turn, mode_node, edge_type=ET.OPERATES_IN)

        # OPERATES_IN from assistant turn
        ai_turn = f"t_{conv_id}_{ann.turn_index + 1}"
        if G.has_node(ai_turn):
            G.add_edge(ai_turn, mode_node, edge_type=ET.OPERATES_IN)


# ============= RATIFIES Edge =============

def add_ratification_edges(
    G: nx.MultiDiGraph,
    conv_id: str,
    messages_with_moves: List[dict],
    constraint_track: ConversationConstraintTrack,
):
    """Add RATIFIES edges from RATIFY_CONSTRAINT and ACCEPT_CONSTRAINT moves to constraints."""
    for msg in messages_with_moves:
        turn_idx = msg.get("turn_index", 0)
        for seq, move in enumerate(msg.get("moves", [])):
            if move and move.get("move_type") in (MT.RATIFY_CONSTRAINT, MT.ACCEPT_CONSTRAINT):
                move_node = f"m_{conv_id}_{turn_idx}_{seq}"
                if not G.has_node(move_node):
                    continue
                # Link to ratifiable constraints
                for c in constraint_track.constraints:
                    c_node = f"c_{conv_id}_{c.constraint_id}"
                    if G.has_node(c_node):
                        s = state_at_turn(c.state_history or [], turn_idx)
                        if s in (CS.STATED, CS.ACTIVE):
                            G.add_edge(move_node, c_node, edge_type=ET.RATIFIES)


# ============= Main Build Function =============

def build_graph(
    conversation_id: str,
    messages_with_moves: List[dict],
    constraint_track: ConversationConstraintTrack,
    mode_annotations: List[ModeAnnotation],
    task_classification: dict,
) -> nx.MultiDiGraph:
    """
    Build the full Atlas graph for one conversation.

    Args:
        conversation_id: Unique conversation identifier
        messages_with_moves: Output of move_classifier.classify_moves()
        constraint_track: Output of constraint_tracker.build_constraint_tracker()
        mode_annotations: Output of mode_detector.detect_mode_violations()
        task_classification: Full entry from all_task_enriched.json

    Returns:
        NetworkX MultiDiGraph with all nodes and edges.
    """
    G = nx.MultiDiGraph()

    # Build metadata dict
    cls = task_classification.get("classification", {})
    tax = task_classification.get("taxonomy", {})
    metadata = {
        "source": task_classification.get("source", ""),
        "domain": task_classification.get("domain", ""),
        "total_turns": task_classification.get("total_turns", 0),
        "stability_class": cls.get("stability_class", ""),
        "task_architecture": tax.get("architecture", ""),
        "constraint_hardness": tax.get("constraint_hardness", ""),
        "task_goal": cls.get("task_goal", ""),
    }

    # 1. Conversation node
    add_conversation_node(G, conversation_id, metadata)

    # 2. Turn nodes
    add_turn_nodes(G, conversation_id, messages_with_moves)

    # 3. Move nodes
    add_move_nodes(G, conversation_id, messages_with_moves)

    # 4. Constraint nodes
    add_constraint_nodes(G, conversation_id, constraint_track, messages_with_moves)

    # 5. Violation events (constraint)
    next_violation_idx = add_violation_events(G, conversation_id, constraint_track, messages_with_moves)

    # 6. Mode nodes
    add_mode_nodes(G, conversation_id, mode_annotations)

    # 7. Mode violation events
    add_mode_violation_events(G, conversation_id, mode_annotations, next_violation_idx, messages_with_moves)

    # 8. Ratification edges
    add_ratification_edges(G, conversation_id, messages_with_moves, constraint_track)

    # 9. Final schema validation
    validate_graph_schema(G)
    
    # 10. Invariants
    assert_graph_invariants(G, conversation_id)

    return G


# ============= Invariants =============

def assert_graph_invariants(G: nx.MultiDiGraph, conv_id: str):
    """Catch structural bugs during construction."""
    conv_node = f"conv_{conv_id}"
    assert G.has_node(conv_node), f"Missing root conversation node: {conv_node}"

    # Every Turn must be contained by Conversation
    for n, a in G.nodes(data=True):
        if a.get("node_type") == "Turn":
            incoming = [(u, v, d) for u, v, d in G.in_edges(n, data=True) if d.get("edge_type") == "CONTAINS"]
            assert any(u == conv_node for u, _, _ in incoming), f"Turn {n} not CONTAINS by {conv_node}"

    # Every Move must have a HAS_MOVE from a Turn
    for n, a in G.nodes(data=True):
        if a.get("node_type") == "Move":
            incoming = [(u, v, d) for u, v, d in G.in_edges(n, data=True) if d.get("edge_type") == "HAS_MOVE"]
            assert incoming, f"Move {n} has no HAS_MOVE incoming"

    # Every ViolationEvent should VIOLATE something (constraint or mode)
    for n, a in G.nodes(data=True):
        if a.get("node_type") == "ViolationEvent":
            out_violates = [(u, v, d) for u, v, d in G.out_edges(n, data=True) if d.get("edge_type") == "VIOLATES"]
            if a.get("constraint_id") != "mode":
                assert out_violates, f"Constraint ViolationEvent {n} has no VIOLATES edge"
            
            # Every violation must be TRIGGERED by a Turn
            in_triggers = [(u, v, d) for u, v, d in G.in_edges(n, data=True) if d.get("edge_type") == "TRIGGERS"]
            assert in_triggers, f"ViolationEvent {n} has no TRIGGERS incoming"


# ============= Export =============

def export_graph_json(G: nx.MultiDiGraph, output_path: Path):
    """Export graph to JSON node-link format for D3.js."""
    data = nx.node_link_data(G)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def export_graph_gexf(G: nx.MultiDiGraph, output_path: Path):
    """Export graph to GEXF format for Gephi."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # GEXF doesn't handle all Python types; convert to strings
    G_clean = G.copy()
    for node, attrs in G_clean.nodes(data=True):
        for k, v in attrs.items():
            if v is None:
                attrs[k] = ""
            elif isinstance(v, bool):
                attrs[k] = str(v)
            elif isinstance(v, (list, dict)):
                attrs[k] = json.dumps(v)

    for u, v, k, attrs in G_clean.edges(data=True, keys=True):
        for key, val in attrs.items():
            if val is None:
                attrs[key] = ""
            elif isinstance(val, bool):
                attrs[key] = str(val)
            elif isinstance(val, (list, dict)):
                attrs[key] = json.dumps(val)

    nx.write_gexf(G_clean, str(output_path))


def export_graph(G: nx.MultiDiGraph, output_path: Path, fmt: str = "json"):
    """Export graph in the specified format."""
    if fmt == "json":
        export_graph_json(G, output_path)
    elif fmt == "gexf":
        export_graph_gexf(G, output_path.with_suffix(".gexf"))
    elif fmt == "both":
        export_graph_json(G, output_path)
        export_graph_gexf(G, output_path.with_suffix(".gexf"))


# ============= Graph Summary =============

def graph_summary(G: nx.MultiDiGraph) -> dict:
    """Return a summary of graph structure for debugging."""
    node_types = {}
    for _, attrs in G.nodes(data=True):
        nt = attrs.get("node_type", "unknown")
        node_types[nt] = node_types.get(nt, 0) + 1

    edge_types = {}
    for _, _, attrs in G.edges(data=True):
        et = attrs.get("edge_type", "unknown")
        edge_types[et] = edge_types.get(et, 0) + 1

    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "node_types": node_types,
        "edge_types": edge_types,
    }
