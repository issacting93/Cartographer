#!/usr/bin/env python3
"""
Graph Schema Validation for Atlas 2.0.
Uses Pydantic models to enforce node and edge integrity.
"""
import networkx as nx
from typing import List, Dict, Any
from atlas.core.models import (
    Conversation, Turn, Move, Constraint, 
    ViolationEvent, InteractionModeAnnotation
)
from atlas.core.enums import NodeType

MODEL_MAP = {
    NodeType.CONVERSATION: Conversation,
    NodeType.TURN: Turn,
    NodeType.MOVE: Move,
    NodeType.CONSTRAINT: Constraint,
    NodeType.VIOLATION_EVENT: ViolationEvent,
    NodeType.INTERACTION_MODE: InteractionModeAnnotation,
}

def validate_graph_schema(G: nx.MultiDiGraph):
    """
    Validate every node in G against its corresponding Pydantic model.
    Checks edge integrity (source/target existence).
    """
    errors = []
    node_ids = set()

    # 1. Validate Nodes
    for n, data in G.nodes(data=True):
        node_ids.add(n)
        node_type = data.get("node_type")
        
        if not node_type:
            errors.append(f"Node {n} is missing 'node_type'")
            continue
            
        model = MODEL_MAP.get(node_type)
        if not model:
            errors.append(f"Node {n} has unknown node_type: {node_type}")
            continue
            
        try:
            # Validate properties excluding 'id' which is used as node key
            node_props = {k: v for k, v in data.items() if k != "id"}
            model(**node_props)
        except Exception as e:
            errors.append(f"Node {n} failed {node_type} validation: {e}")

    # 2. Validate Edges
    for u, v, key, data in G.edges(data=True, keys=True):
        if u not in node_ids:
            errors.append(f"Edge ({u} -> {v}) references missing source node: {u}")
        if v not in node_ids:
            errors.append(f"Edge ({u} -> {v}) references missing target node: {v}")
        
        if not data.get("edge_type"):
            errors.append(f"Edge ({u} -> {v}, key={key}) is missing 'edge_type'")

    if errors:
        raise ValueError("Graph schema validation failed:\n" + "\n".join(errors))
    
    return True
