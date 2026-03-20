#!/usr/bin/env python3
import json
import statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 60)
    print("COMPUTING CASCADE & LITERATURE STATS")
    print("=" * 60)

    total_constrained_convs = 0
    cascade_entries = 0
    cascade_collapses = 0
    total_repair_turns = 0
    total_turns_constrained = 0
    
    patience_abandoned = []
    patience_survived = []
    
    for f in sorted(GRAPHS_DIR.glob('*.json')):
        if '-error' in f.stem:
            continue
        with open(f) as fh:
            g = json.load(fh)
            
        nodes = g.get('nodes', [])
        edges = g.get('links', [])
        
        constraints = [n for n in nodes if n.get('node_type') == 'Constraint']
        if not constraints:
            continue
            
        total_constrained_convs += 1
        
        turns = sorted(
            [n for n in nodes if n.get('node_type') == 'Turn'], 
            key=lambda x: x.get('turn_index', 0)
        )
        total_turns_constrained += len(turns)
        
        # Build turn-to-moves mapping
        turn_to_moves = {t.get('id'): [] for t in turns}
        for edge in edges:
            if edge.get('edge_type') == 'HAS_MOVE':
                source = edge.get('source')
                target = edge.get('target')
                if source in turn_to_moves:
                    turn_to_moves[source].append(target)
                    
        move_dict = {n.get('id'): n for n in nodes if n.get('node_type') == 'Move'}
        
        # 1. Detect Cascades
        consecutive_repair_turns = 0
        in_cascade = False
        cascaded_this_conv = False
        escape_counter = 0
        escaped_this_conv = False
        
        for turn in turns:
            t_id = turn.get('id')
            m_ids = turn_to_moves.get(t_id, [])
            m_types = [move_dict[m].get('move_type') for m in m_ids if m in move_dict]
            
            has_trouble = any(t in ['REPAIR_INITIATE', 'ESCALATE', 'REPAIR_FAIL'] for t in m_types)
            if has_trouble:
                total_repair_turns += 1
                consecutive_repair_turns += 1
                escape_counter = 0
                if consecutive_repair_turns >= 5 and not in_cascade:
                    in_cascade = True
                    cascaded_this_conv = True
            else:
                consecutive_repair_turns = 0
                if in_cascade:
                    escape_counter += 1
                    if escape_counter >= 3:
                        in_cascade = False
                        escaped_this_conv = True

        if cascaded_this_conv:
            cascade_entries += 1
            if not escaped_this_conv:
                cascade_collapses += 1
                
        # 2. Patience computation
        viols = [n.get('turn_index', 0) for n in nodes if n.get('node_type') == 'ViolationEvent']
        if viols:
            first_violation_turn = min(viols)
            max_turn = max([t.get('turn_index', 0) for t in turns]) if turns else 0
            p_val = max(0, max_turn - first_violation_turn)
            
            # Check abandonment
            # If all constraints ended up ABANDONED or VIOLATED, it's abandonment.
            final_states = [c.get('current_state') for c in constraints]
            is_abandoned = all(s in ['ABANDONED', 'VIOLATED'] for s in final_states)
            
            if is_abandoned:
                patience_abandoned.append(p_val)
            else:
                patience_survived.append(p_val)
            
    # Compile stats
    entry_rate = cascade_entries / total_constrained_convs if total_constrained_convs > 0 else 0
    collapse_rate = cascade_collapses / cascade_entries if cascade_entries > 0 else 0
    escape_prob = 1.0 - collapse_rate if cascade_entries > 0 else 0
    density = total_repair_turns / total_turns_constrained if total_turns_constrained > 0 else 0
    mean_p_ab = statistics.mean(patience_abandoned) if patience_abandoned else 0
    mean_p_surv = statistics.mean(patience_survived) if patience_survived else 0
    
    stats = {
        "n_constrained_convs": total_constrained_convs,
        "total_repair_turns": total_repair_turns,
        "total_turns_constrained": total_turns_constrained,
        "repair_density": round(density, 4),
        "cascade_entries": cascade_entries,
        "cascade_entry_rate": round(entry_rate, 4),
        "cascade_collapses": cascade_collapses,
        "cascade_collapse_rate": round(collapse_rate, 4),
        "escape_probability": round(escape_prob, 4),
        "patience": {
            "mean_abandonment_turns": round(mean_p_ab, 2),
            "mean_persistence_turns": round(mean_p_surv, 2),
            "abandonment_cases": len(patience_abandoned),
            "persistence_cases": len(patience_survived)
        }
    }

    print(json.dumps(stats, indent=2))
    
    out_path = OUTPUT_DIR / "cascade_stats.json"
    with open(out_path, 'w') as f:
        json.dump(stats, f, indent=2)
        
    print(f"Saved cascade stats to {out_path}")

if __name__ == "__main__":
    main()
