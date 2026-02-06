"""
Atlas: Interactional Cartography Pipeline

A graph-structural method for diagnosing governance failure in human-AI conversation.
Transforms linear chat logs into heterogeneous MultiDiGraphs (NetworkX) that map
constraint lifecycles, repair trajectories, and interaction mode violations.

Pipeline stages:
    1. Move Classification   (move_classifier.py)   — hybrid regex + LLM
    2. Mode Detection         (mode_detector.py)     — regex + LLM fallback
    3. Constraint Tracking    (constraint_tracker.py) — deterministic state machine
    4. Graph Construction     (build_atlas_graph.py)  — NetworkX MultiDiGraph
    5. Metrics Computation    (graph_metrics.py)      — drift velocity, agency tax, etc.

Entry point:
    python -m atlas.run_pipeline --help

Graph schema:
    6 node types: Conversation, Turn, Move, Constraint, ViolationEvent, InteractionMode
    8+ edge types: NEXT, CONTAINS, HAS_MOVE, VIOLATES, REPAIRS, TRIGGERS, OPERATES_IN, RATIFIES
"""
