#!/usr/bin/env python3
"""
Export full N=2577 dashboard data by merging:
  - v2_unified/conversations/*.json  → SRT roles, PAD affect
  - v2_unified/atlas/graphs/*.json   → violations, moves, constraints
  - task_classified/all_task_classified.json → stability class (983 convs)
  - atlas_canonical/metrics/aggregate.json  → architecture breakdown (744 convs)

Outputs:
  - public/atlas_suite/data/dashboard_data.json
  - public/atlas_suite/data/meta_graph.json
"""

import json
import os
import glob
from collections import defaultdict, Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CONV_DIR = PROJECT / "data" / "v2_unified" / "conversations"
GRAPH_DIR = PROJECT / "data" / "v2_unified" / "atlas" / "graphs"
TASK_CLASSIFIED = PROJECT / "data" / "task_classified" / "all_task_classified.json"
CANON_METRICS = PROJECT / "data" / "atlas_canonical" / "metrics"
OUTPUT_DIR = PROJECT / "public" / "atlas_suite" / "data"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_dominant(dist):
    if not dist:
        return None
    return max(dist.items(), key=lambda x: x[1])[0]


def extract_conv_data(conv):
    """Extract SRT + PAD from a v2_unified conversation JSON."""
    c = conv.get("classification", {})
    messages = conv.get("messages", [])

    # SRT roles
    human_role = c.get("humanRole", {})
    ai_role = c.get("aiRole", {})
    h_dist = human_role.get("distribution", {})
    a_dist = ai_role.get("distribution", {})

    # SRT dimensions
    dims = {}
    for dim in ["interactionPattern", "powerDynamics", "emotionalTone",
                 "engagementStyle", "knowledgeExchange", "conversationPurpose",
                 "topicDepth", "turnTaking"]:
        val = c.get(dim, {})
        if isinstance(val, dict):
            dims[dim] = val.get("category", "")
        elif isinstance(val, str):
            dims[dim] = val

    # PAD from messages
    pad_values = [m["pad"] for m in messages if m.get("pad")]
    mean_pleasure = mean_arousal = mean_dominance = mean_intensity = None
    human_mean_dom = ai_mean_dom = None

    if pad_values:
        # Handle both "pleasure" and "p" keys
        mean_pleasure = round(sum(p.get("pleasure", p.get("p", 0)) for p in pad_values) / len(pad_values), 3)
        mean_arousal = round(sum(p.get("arousal", p.get("a", 0)) for p in pad_values) / len(pad_values), 3)
        mean_dominance = round(sum(p.get("dominance", p.get("d", 0)) for p in pad_values) / len(pad_values), 3)
        mean_intensity = round(sum(p.get("emotionalIntensity", 0) for p in pad_values) / len(pad_values), 3)

    # Human vs AI dominance
    human_pads = [m["pad"] for m in messages if m.get("pad") and m.get("role") == "user"]
    ai_pads = [m["pad"] for m in messages if m.get("pad") and m.get("role") in ("assistant", "model")]

    if human_pads:
        human_mean_dom = round(sum(p.get("dominance", p.get("d", 0)) for p in human_pads) / len(human_pads), 3)
    if ai_pads:
        ai_mean_dom = round(sum(p.get("dominance", p.get("d", 0)) for p in ai_pads) / len(ai_pads), 3)

    return {
        "human_role_dist": h_dist,
        "ai_role_dist": a_dist,
        "dominant_human_role": get_dominant(h_dist),
        "dominant_ai_role": get_dominant(a_dist),
        "mean_pleasure": mean_pleasure,
        "mean_arousal": mean_arousal,
        "mean_dominance": mean_dominance,
        "mean_intensity": mean_intensity,
        "human_mean_dominance": human_mean_dom,
        "ai_mean_dominance": ai_mean_dom,
        "n_messages": len(messages),
        **dims,
    }


def scan_graph(path):
    """Extract violation/constraint/repair data from a graph JSON."""
    data = load_json(path)
    nodes = data.get("nodes", [])

    conv_node = next((n for n in nodes if n.get("node_type") == "Conversation"), {})
    source = conv_node.get("source", "unknown")

    turns = [n for n in nodes if n.get("node_type") == "Turn"]
    constraints = [n for n in nodes if n.get("node_type") == "Constraint"]
    violations = [n for n in nodes if n.get("node_type") == "ViolationEvent"]
    repairs = [n for n in nodes if n.get("node_type") == "Move" and n.get("move_type", "").startswith("REPAIR")]
    modes = [n for n in nodes if n.get("node_type") == "InteractionMode"]

    # Constraint states
    survived = sum(1 for c in constraints if c.get("current_state") in ("SURVIVED", "ACTIVE"))
    violated = sum(1 for c in constraints if c.get("current_state") == "VIOLATED")

    # Mode violations vs constraint violations
    mode_violations = []
    constraint_violations = []
    for v in violations:
        vtype = v.get("violation_type", "")
        if v.get("constraint_id") == "mode" or vtype in ("UNSOLICITED_ADVICE", "PREMATURE_EXECUTION", "EXECUTION_AVOIDANCE"):
            mode_violations.append(v)
        else:
            constraint_violations.append(v)

    return {
        "source": source,
        "turn_count": len(turns),
        "constraint_count": len(constraints),
        "survived": survived,
        "violated": violated,
        "violation_count": len(violations),
        "mode_violation_count": len(mode_violations),
        "constraint_violation_count": len(constraint_violations),
        "repair_count": len(repairs),
        "mode_violations": mode_violations,
        "constraint_violations": constraint_violations,
        "drift_velocity": round(len(violations) / len(turns), 4) if turns else 0,
        "mode_violation_rate": round(len(mode_violations) / len(turns), 4) if turns else 0,
    }


def main():
    print("Loading task_classified stability data...")
    tc_data = load_json(TASK_CLASSIFIED)
    stability_lookup = {}
    for item in tc_data:
        cid = item["id"]
        cls = item.get("classification", {})
        stability_lookup[cid] = cls.get("stability_class", "")

    # Load atlas_canonical architecture data
    print("Loading atlas_canonical architecture data...")
    arch_lookup = {}
    canon_all = load_json(CANON_METRICS / "all_metrics.json")
    for m in canon_all:
        if m.get("task_architecture"):
            arch_lookup[m["conversation_id"]] = m["task_architecture"]

    # Process all conversations
    conv_files = sorted(glob.glob(str(CONV_DIR / "*.json")))
    print(f"Processing {len(conv_files)} conversations...")

    # Aggregate counters
    all_nodes = []
    per_conversation = []
    constraint_states = {"SURVIVED": 0, "VIOLATED": 0}
    violation_timing = defaultdict(int)
    mode_violation_types = defaultdict(int)
    mode_by_source = defaultdict(lambda: defaultdict(int))
    total_constraint_violations = 0
    total_mode_violations = 0
    total_repairs = 0
    stability_counts = Counter()
    arch_data = defaultdict(lambda: {
        "n": 0, "drift_sum": 0, "survival_sum": 0, "mvr_sum": 0,
        "total_violations": 0, "total_constraints": 0
    })
    stability_data = defaultdict(lambda: {
        "n": 0, "drift_sum": 0, "survival_sum": 0, "mvr_sum": 0,
        "total_violations": 0, "total_repairs": 0, "total_constraints": 0,
        "half_life_sum": 0, "half_life_count": 0
    })

    for conv_path in conv_files:
        cid = Path(conv_path).stem
        conv = load_json(conv_path)

        # SRT + PAD from conversation
        srt_pad = extract_conv_data(conv)

        # Graph data
        graph_path = GRAPH_DIR / f"{cid}.json"
        if graph_path.exists():
            gd = scan_graph(graph_path)
        else:
            gd = {
                "source": conv.get("source", "unknown"),
                "turn_count": len(conv.get("messages", [])) // 2,
                "constraint_count": 0, "survived": 0, "violated": 0,
                "violation_count": 0, "mode_violation_count": 0,
                "constraint_violation_count": 0, "repair_count": 0,
                "mode_violations": [], "constraint_violations": [],
                "drift_velocity": 0, "mode_violation_rate": 0,
            }

        # Stability + architecture
        stability = stability_lookup.get(cid, "")
        architecture = arch_lookup.get(cid, "")

        # Accumulate constraint states
        constraint_states["SURVIVED"] += gd["survived"]
        constraint_states["VIOLATED"] += gd["violated"]

        # Accumulate violation timing
        for v in gd["constraint_violations"]:
            turn = v.get("turn_index", 0)
            violation_timing[turn] += 1
        total_constraint_violations += gd["constraint_violation_count"]

        # Accumulate mode violations
        for v in gd["mode_violations"]:
            vtype = v.get("violation_type", "UNKNOWN")
            mode_violation_types[vtype] += 1
            mode_by_source[gd["source"]][vtype] += 1
        total_mode_violations += gd["mode_violation_count"]
        total_repairs += gd["repair_count"]

        # Stability aggregation
        if stability:
            stability_counts[stability] += 1
            sd = stability_data[stability]
            sd["n"] += 1
            sd["drift_sum"] += gd["drift_velocity"]
            sd["mvr_sum"] += gd["mode_violation_rate"]
            sd["total_violations"] += gd["violation_count"]
            sd["total_repairs"] += gd["repair_count"]
            sd["total_constraints"] += gd["constraint_count"]
            if gd["constraint_count"] > 0:
                sr = gd["survived"] / gd["constraint_count"]
                sd["survival_sum"] += sr

        # Architecture aggregation
        if architecture:
            ad = arch_data[architecture]
            ad["n"] += 1
            ad["drift_sum"] += gd["drift_velocity"]
            ad["mvr_sum"] += gd["mode_violation_rate"]
            ad["total_violations"] += gd["violation_count"]
            ad["total_constraints"] += gd["constraint_count"]
            if gd["constraint_count"] > 0:
                sr = gd["survived"] / gd["constraint_count"]
                ad["survival_sum"] += sr

        # Per-conversation record
        per_conversation.append({
            "id": cid,
            "drift": gd["drift_velocity"],
            "tax": 0,
            "survival": (gd["survived"] / gd["constraint_count"]) if gd["constraint_count"] > 0 else 0,
            "class": stability or "Unclassified",
            "arch": architecture or "Unclassified",
            "turns": gd["turn_count"],
            "violations": gd["violation_count"],
            "constraints": gd["constraint_count"],
            "mode_violation_rate": gd["mode_violation_rate"],
        })

        # Meta-graph node
        all_nodes.append({
            "id": cid,
            "filename": f"{cid}.json",
            "source": gd["source"],
            "stability": stability or "Unclassified",
            "architecture": architecture or "Unclassified",
            "constraint_count": gd["constraint_count"],
            "turn_count": gd["turn_count"],
            "violation_count": gd["violation_count"],
            "repair_count": gd["repair_count"],
            "drift_velocity": gd["drift_velocity"],
            **srt_pad,
        })

    # Build aggregate KPIs
    total_constraints = constraint_states["SURVIVED"] + constraint_states["VIOLATED"]
    survival_rate = constraint_states["SURVIVED"] / total_constraints if total_constraints > 0 else 0
    repair_rate = total_repairs / total_constraint_violations if total_constraint_violations > 0 else 0

    kpis = {
        "total_conversations": len(conv_files),
        "constraint_survival": {
            "value": round(survival_rate * 100, 1),
            "detail": f"{constraint_states['SURVIVED']}/{total_constraints}",
            "label": "Constraint Survival",
        },
        "turn_half_life": {
            "value": 2.5,  # from verified_stats.json
            "label": "Turn Half-Life",
        },
        "mode_violation_rate": {
            "value": round((sum(1 for pc in per_conversation if pc["mode_violation_rate"] > 0) / len(per_conversation)) * 100, 1),
            "label": "Mode Violation Rate",
        },
        "repair_rate": {
            "value": round(repair_rate * 100, 1),
            "detail": f"{total_repairs}/{total_constraint_violations}",
            "label": "Repair Rate",
        },
    }

    # Build by_architecture
    by_arch = {}
    for arch, ad in sorted(arch_data.items()):
        n = ad["n"]
        by_arch[arch] = {
            "n": n,
            "drift_velocity": round(ad["drift_sum"] / n, 4) if n else 0,
            "survival_rate": round(ad["survival_sum"] / n, 4) if n else 0,
            "mode_violation_rate": round(ad["mvr_sum"] / n, 4) if n else 0,
            "total_violations": ad["total_violations"],
            "total_constraints": ad["total_constraints"],
        }

    # Build by_stability_class
    by_class = {}
    for cls, sd in sorted(stability_data.items()):
        n = sd["n"]
        by_class[cls] = {
            "n": n,
            "drift_velocity": round(sd["drift_sum"] / n, 4) if n else 0,
            "survival_rate": round(sd["survival_sum"] / n, 4) if n else 0,
            "mode_violation_rate": round(sd["mvr_sum"] / n, 4) if n else 0,
            "total_violations": sd["total_violations"],
            "total_repairs": sd["total_repairs"],
            "total_constraints": sd["total_constraints"],
        }

    # Output dashboard_data.json
    dashboard = {
        "kpis": kpis,
        "violation_timing": dict(sorted(violation_timing.items())),
        "constraint_states": dict(constraint_states),
        "mode_violation_types": dict(sorted(mode_violation_types.items(), key=lambda x: -x[1])),
        "mode_by_source": {k: dict(v) for k, v in mode_by_source.items()},
        "total_constraint_violations": total_constraint_violations,
        "total_mode_violations": total_mode_violations,
        "total_repairs": total_repairs,
        "by_architecture": by_arch,
        "by_stability_class": by_class,
        "per_conversation": per_conversation,
    }

    dash_path = OUTPUT_DIR / "dashboard_data.json"
    with open(dash_path, "w") as f:
        json.dump(dashboard, f, indent=2)
    print(f"Wrote {dash_path}")

    # Output meta_graph.json
    meta = {"nodes": all_nodes, "links": []}
    meta_path = OUTPUT_DIR / "meta_graph.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Wrote {meta_path}")

    # Summary
    print(f"\n=== Summary ===")
    print(f"Conversations: {len(conv_files)}")
    print(f"With stability class: {sum(1 for n in all_nodes if n['stability'] != 'Unclassified')}")
    print(f"With architecture: {sum(1 for n in all_nodes if n['architecture'] != 'Unclassified')}")
    print(f"With SRT roles: {sum(1 for n in all_nodes if n.get('dominant_human_role'))}")
    print(f"With PAD affect: {sum(1 for n in all_nodes if n.get('mean_pleasure') is not None)}")
    print(f"Constraints: {total_constraints} (survived={constraint_states['SURVIVED']}, violated={constraint_states['VIOLATED']})")
    print(f"Mode violations: {total_mode_violations}")
    print(f"Stability: {dict(stability_counts)}")
    print(f"Architectures: {list(by_arch.keys())}")


if __name__ == "__main__":
    main()
