#!/usr/bin/env python3
"""
Graph Metrics Computation

Computes CUI-paper-relevant metrics from Atlas graphs:
  - Drift Velocity: rate of constraint violations per turn
  - Agency Tax: user repair effort per violation
  - Constraint Half-Life: median turns to first violation
  - Constraint Survival Rate: fraction of constraints surviving
  - Mode Violation Rate: frequency of mode mismatches
  - Repair Success Rate: fraction of violations successfully repaired
  - Mean Constraint Lifespan: average constraint persistence
  - Mode Entropy: Shannon entropy of mode distribution
"""

import json
import math
import statistics
from typing import List, Optional
from pathlib import Path
from dataclasses import asdict

try:
    import networkx as nx
except ImportError:
    raise ImportError("networkx required: pip install networkx")

from atlas.core.enums import NodeType as NT, EdgeType as ET, MoveType as MT
from atlas.core.models import ConversationMetrics


# ============= Individual Metric Functions =============

def compute_drift_velocity(G: nx.MultiDiGraph) -> float:
    """VIOLATES edges / Turn node count."""
    turns = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == NT.TURN)
    violates = sum(1 for _, _, d in G.edges(data=True) if d.get("edge_type") == ET.VIOLATES)
    return round(violates / max(turns, 1), 4)


def compute_agency_tax(G: nx.MultiDiGraph) -> float:
    """REPAIR moves / ViolationEvent count."""
    repair_moves = sum(
        1 for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.MOVE and d.get("move_type") in (MT.REPAIR_INITIATE, MT.REPAIR_EXECUTE)
    )
    violation_events = sum(
        1 for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.VIOLATION_EVENT
    )
    if violation_events == 0:
        return 0.0
    return round(repair_moves / violation_events, 4)


def compute_constraint_half_life(G: nx.MultiDiGraph) -> Optional[float]:
    """Median turns from introduction to first violation across constraints."""
    lifetimes = []

    constraint_nodes = [
        (n, d) for n, d in G.nodes(data=True)
        if d.get("node_type") == NT.CONSTRAINT
    ]

    for c_node, c_data in constraint_nodes:
        introduced_at = c_data.get("introduced_at", 0)
        times_violated = c_data.get("times_violated", 0)

        if times_violated == 0:
            continue

        # Find all VIOLATES edges targeting this constraint
        violations = []
        for u, v, e_data in G.edges(data=True):
            if e_data.get("edge_type") == ET.VIOLATES and v == c_node:
                # u is the ViolationEvent node
                ve_data = G.nodes.get(u, {})
                turn_idx = ve_data.get("turn_index")
                if turn_idx is not None:
                    violations.append(turn_idx)
        
        if violations:
            # Pick the temporally first violation
            violation_turn = min(violations)
            lifetime = violation_turn - introduced_at
            if lifetime >= 0:
                lifetimes.append(lifetime)

    if not lifetimes:
        return None
    return round(statistics.median(lifetimes), 2)


def compute_constraint_survival_rate(G: nx.MultiDiGraph) -> float:
    """Fraction of constraints in SURVIVED state."""
    constraints = [
        d for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.CONSTRAINT
    ]
    if not constraints:
        return 0.0
    survived = sum(1 for c in constraints if c.get("current_state") == "SURVIVED")
    return round(survived / len(constraints), 4)


def compute_mode_violation_rate(G: nx.MultiDiGraph) -> float:
    """Fraction of InteractionMode nodes that are violations."""
    mode_nodes = [
        d for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.INTERACTION_MODE
    ]
    if not mode_nodes:
        return 0.0
    violations = sum(1 for m in mode_nodes if m.get("is_violation") in (True, "True"))
    return round(violations / len(mode_nodes), 4)


def compute_repair_success_rate(G: nx.MultiDiGraph) -> float:
    """Fraction of ViolationEvents that were repaired."""
    violations = [
        d for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.VIOLATION_EVENT
        and d.get("violation_type") == "constraint_violation"
    ]
    if not violations:
        return 0.0
    repaired = sum(1 for v in violations if v.get("was_repaired") in (True, "True"))
    return round(repaired / len(violations), 4)


def compute_mean_constraint_lifespan(G: nx.MultiDiGraph) -> float:
    """Average lifespan across all constraints."""
    constraints = [
        d for _, d in G.nodes(data=True)
        if d.get("node_type") == "Constraint"
    ]
    if not constraints:
        return 0.0
    lifespans = [c.get("lifespan", 0) for c in constraints]
    return round(sum(lifespans) / len(lifespans), 2)


def compute_mode_entropy(G: nx.MultiDiGraph) -> float:
    """Shannon entropy of mode distribution (user-requested modes)."""
    mode_nodes = [
        d for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.INTERACTION_MODE
    ]
    if not mode_nodes:
        return 0.0

    mode_counts = {}
    for m in mode_nodes:
        mode = m.get("user_requested", "AMBIGUOUS")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    total = sum(mode_counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in mode_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    return round(entropy, 4)


def compute_move_coverage(G: nx.MultiDiGraph) -> float:
    """Fraction of Turn nodes that have at least one Move neighbor."""
    turns = [n for n, d in G.nodes(data=True) if d.get("node_type") == NT.TURN]
    if not turns:
        return 0.0
    
    covered_turns = 0
    for turn_node in turns:
        # Check for edges to/from Move nodes
        has_move = False
        for neighbor in G.neighbors(turn_node):
            if G.nodes[neighbor].get("node_type") == NT.MOVE:
                has_move = True
                break
        if not has_move:
            # Also check predecessors if the graph is directional in a way that moves point to turns
            for pred in G.predecessors(turn_node):
                if G.nodes[pred].get("node_type") == NT.MOVE:
                    has_move = True
                    break
        
        if has_move:
            covered_turns += 1
            
    return round(covered_turns / len(turns), 4)


# ============= Main Computation =============

def compute_metrics(
    G: nx.MultiDiGraph,
    conversation_id: str = "",
    stability_class: str = "",
    task_architecture: str = "",
    constraint_hardness: str = "",
) -> ConversationMetrics:
    """Compute all metrics from a single conversation graph."""

    # Extract metadata from conversation node if not provided
    if not conversation_id:
        for _, d in G.nodes(data=True):
            if d.get("node_type") == NT.CONVERSATION:
                conversation_id = d.get("conv_id", "")
                stability_class = stability_class or d.get("stability_class", "")
                task_architecture = task_architecture or d.get("task_architecture", "")
                constraint_hardness = constraint_hardness or d.get("constraint_hardness", "")
                break

    total_turns = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == NT.TURN)
    total_violations = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == NT.VIOLATION_EVENT)
    total_repairs = sum(
        1 for _, d in G.nodes(data=True)
        if d.get("node_type") == NT.MOVE and d.get("move_type") == MT.REPAIR_INITIATE
    )
    total_constraints = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == NT.CONSTRAINT)

    return ConversationMetrics(
        conversation_id=conversation_id,
        drift_velocity=compute_drift_velocity(G),
        agency_tax=compute_agency_tax(G),
        constraint_half_life=compute_constraint_half_life(G),
        constraint_survival_rate=compute_constraint_survival_rate(G),
        mode_violation_rate=compute_mode_violation_rate(G),
        repair_success_rate=compute_repair_success_rate(G),
        mean_constraint_lifespan=compute_mean_constraint_lifespan(G),
        mode_entropy=compute_mode_entropy(G),
        total_violations=total_violations,
        total_repairs=total_repairs,
        total_constraints=total_constraints,
        total_turns=total_turns,
        move_coverage=compute_move_coverage(G),
        stability_class=stability_class,
        task_architecture=task_architecture,
        constraint_hardness=constraint_hardness,
    )


# ============= Aggregation =============

def aggregate_metrics(
    all_metrics: List[ConversationMetrics],
) -> dict:
    """
    Cross-conversation aggregation with breakdowns by stability_class,
    architecture, and hardness.
    """
    if not all_metrics:
        return {"total": 0}

    def agg_group(group: List[ConversationMetrics]) -> dict:
        n = len(group)
        if n == 0:
            return {"n": 0}

        def safe_mean(values):
            filtered = [v for v in values if v is not None]
            return round(sum(filtered) / len(filtered), 4) if filtered else None

        return {
            "n": n,
            "mean_drift_velocity": safe_mean([m.drift_velocity for m in group]),
            "mean_agency_tax": safe_mean([m.agency_tax for m in group]),
            "mean_constraint_half_life": safe_mean([m.constraint_half_life for m in group]),
            "mean_survival_rate": safe_mean([m.constraint_survival_rate for m in group]),
            "mean_mode_violation_rate": safe_mean([m.mode_violation_rate for m in group]),
            "mean_repair_success_rate": safe_mean([m.repair_success_rate for m in group]),
            "mean_constraint_lifespan": safe_mean([m.mean_constraint_lifespan for m in group]),
            "mean_mode_entropy": safe_mean([m.mode_entropy for m in group]),
            "mean_move_coverage": safe_mean([m.move_coverage for m in group]),
            "total_violations": sum(m.total_violations for m in group),
            "total_repairs": sum(m.total_repairs for m in group),
            "total_constraints": sum(m.total_constraints for m in group),
        }

    result = {
        "total": len(all_metrics),
        "overall": agg_group(all_metrics),
    }

    # Group by stability_class
    by_stability = {}
    for m in all_metrics:
        key = m.stability_class or "Unknown"
        by_stability.setdefault(key, []).append(m)
    result["by_stability_class"] = {k: agg_group(v) for k, v in sorted(by_stability.items())}

    # Group by task_architecture
    by_arch = {}
    for m in all_metrics:
        key = m.task_architecture or "Unknown"
        by_arch.setdefault(key, []).append(m)
    result["by_architecture"] = {k: agg_group(v) for k, v in sorted(by_arch.items())}

    # Group by constraint_hardness
    by_hardness = {}
    for m in all_metrics:
        key = m.constraint_hardness or "Unknown"
        by_hardness.setdefault(key, []).append(m)
    result["by_hardness"] = {k: agg_group(v) for k, v in sorted(by_hardness.items())}

    return result


# ============= Report Generation =============

def generate_report(
    all_metrics: List[ConversationMetrics],
    output_path: Path,
):
    """Generate a markdown report with tables and key findings."""
    agg = aggregate_metrics(all_metrics)
    overall = agg.get("overall", {})

    lines = [
        "# Atlas Graph Metrics Report",
        "",
        f"**Conversations Analyzed:** {agg['total']}",
        f"**Total Constraints Tracked:** {overall.get('total_constraints', 0)}",
        f"**Total Violations Detected:** {overall.get('total_violations', 0)}",
        f"**Total Repairs Attempted:** {overall.get('total_repairs', 0)}",
        "",
        "## Overall Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Drift Velocity (violations/turn) | {overall.get('mean_drift_velocity', 'N/A')} |",
        f"| Agency Tax (repairs/violation) | {overall.get('mean_agency_tax', 'N/A')} |",
        f"| Constraint Half-Life (turns) | {overall.get('mean_constraint_half_life', 'N/A')} |",
        f"| Constraint Survival Rate | {overall.get('mean_survival_rate', 'N/A')} |",
        f"| Mode Violation Rate | {overall.get('mean_mode_violation_rate', 'N/A')} |",
        f"| Repair Success Rate | {overall.get('mean_repair_success_rate', 'N/A')} |",
        f"| Mean Constraint Lifespan (turns) | {overall.get('mean_constraint_lifespan', 'N/A')} |",
        f"| Mode Entropy | {overall.get('mean_mode_entropy', 'N/A')} |",
        f"| Move Coverage | {overall.get('mean_move_coverage', 'N/A')} |",
        "",
    ]

    # Breakdown by stability class
    lines.append("## By Task Stability Class")
    lines.append("")
    lines.append("| Stability Class | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |")
    lines.append("|----------------|---|-----------|-----------|----------|----------|-----------|")

    for cls_name, stats in agg.get("by_stability_class", {}).items():
        lines.append(
            f"| {cls_name} | {stats['n']} "
            f"| {stats.get('mean_drift_velocity', '-')} "
            f"| {stats.get('mean_agency_tax', '-')} "
            f"| {stats.get('mean_constraint_half_life', '-')} "
            f"| {stats.get('mean_survival_rate', '-')} "
            f"| {stats.get('mean_mode_violation_rate', '-')} |"
        )
    lines.append("")

    # Breakdown by architecture
    lines.append("## By Task Architecture")
    lines.append("")
    lines.append("| Architecture | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |")
    lines.append("|-------------|---|-----------|-----------|----------|----------|-----------|")

    for arch_name, stats in agg.get("by_architecture", {}).items():
        lines.append(
            f"| {arch_name} | {stats['n']} "
            f"| {stats.get('mean_drift_velocity', '-')} "
            f"| {stats.get('mean_agency_tax', '-')} "
            f"| {stats.get('mean_constraint_half_life', '-')} "
            f"| {stats.get('mean_survival_rate', '-')} "
            f"| {stats.get('mean_mode_violation_rate', '-')} |"
        )
    lines.append("")

    # Breakdown by hardness
    lines.append("## By Constraint Hardness")
    lines.append("")
    lines.append("| Hardness | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |")
    lines.append("|----------|---|-----------|-----------|----------|----------|-----------|")

    for hard_name, stats in agg.get("by_hardness", {}).items():
        lines.append(
            f"| {hard_name} | {stats['n']} "
            f"| {stats.get('mean_drift_velocity', '-')} "
            f"| {stats.get('mean_agency_tax', '-')} "
            f"| {stats.get('mean_constraint_half_life', '-')} "
            f"| {stats.get('mean_survival_rate', '-')} "
            f"| {stats.get('mean_mode_violation_rate', '-')} |"
        )
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
