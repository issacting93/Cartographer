#!/usr/bin/env python3
"""
Compute every number cited in the short paper, save to JSON.
Single source of truth. No machine learning, no clustering — just counting.

Outputs: data/v2_unified/reports/verified_stats.json
"""

import json
import statistics
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def iter_valid_graphs():
    """Iterate over graph JSON files, skipping error-named ones."""
    for f in sorted(GRAPHS_DIR.glob('*.json')):
        if '-error' in f.stem:
            continue
        yield f


def compute_stats():
    """
    Walk every graph and count:
    - How many instructions (constraints) exist
    - How many were violated / followed / ambiguous
    - How quickly violations happen
    - How many users tried to correct the AI
    - How often corrections worked
    - How long users persisted after violations
    - How much of the conversation was spent on repair
    """

    n_graphs = 0
    n_with_constraints = 0

    # Constraint outcomes
    total_constraints = 0
    violated = 0
    followed = 0       # ACTIVE in state_history AND never violated
    ambiguous = 0      # never violated, never acknowledged

    # Timing
    turns_until_violated = []

    # Repair
    total_violation_events = 0
    repaired_events = 0
    convs_with_repair = 0

    # Repair density
    total_repair_turns = 0
    total_turns_in_constrained = 0

    # Patience
    patience_abandoned = []
    patience_survived = []

    # CA-grounded metrics (Clark & Brennan 1991, Schegloff 1977)
    grounding_demonstration = 0  # ACKNOWLEDGE_CONSTRAINT (understanding demonstration)
    grounding_token = 0          # ACCEPT_CONSTRAINT (acknowledgment token)
    grounding_unmarked = 0       # SILENT_COMPLY (unmarked compliance)
    self_repair_count = 0   # SELF_REPAIR (Schegloff SISR)
    total_assistant_turns = 0
    repair_org = Counter()  # SISR / OISR / OIOR

    # Collapse
    collapse_file = PROJECT_ROOT / "data" / "features_llm_collapse.json"

    for f in iter_valid_graphs():
        with open(f) as fh:
            g = json.load(fh)
        n_graphs += 1

        nodes = g.get('nodes', [])
        links = g.get('links', [])

        constraints = [n for n in nodes if n.get('node_type') == 'Constraint']
        if not constraints:
            continue

        n_with_constraints += 1

        turns = sorted(
            [n for n in nodes if n.get('node_type') == 'Turn'],
            key=lambda x: x.get('turn_index', 0)
        )
        total_turns_in_constrained += len(turns)

        violations = [
            n for n in nodes
            if n.get('node_type') == 'ViolationEvent'
            and n.get('violation_type') == 'constraint_violation'
        ]

        # --- Count constraint outcomes ---
        for c in constraints:
            total_constraints += 1
            state = c.get('current_state', '')
            tv = c.get('times_violated', 0)

            if state == 'VIOLATED' or tv > 0:
                violated += 1

                # How quickly was it violated?
                c_viols = [v for v in violations if v.get('constraint_id') == c.get('constraint_id')]
                if c_viols:
                    first_turn = min(v.get('turn_index', 999) for v in c_viols)
                    intro = c.get('introduced_at', 0)
                    turns_until_violated.append(first_turn - intro)

            elif state == 'SURVIVED':
                # Was the AI ever aware of this constraint?
                history = c.get('state_history', [])
                states_in_history = [
                    entry[1] if isinstance(entry, (list, tuple)) and len(entry) >= 2 else None
                    for entry in history
                ]
                if 'ACTIVE' in states_in_history:
                    followed += 1
                else:
                    ambiguous += 1

        # --- Count violation events and repairs ---
        conv_violations = 0
        conv_repaired = 0
        for v in violations:
            total_violation_events += 1
            conv_violations += 1
            if v.get('was_repaired'):
                repaired_events += 1
                conv_repaired += 1

        # --- Count repair attempts (user turns with REPAIR_INITIATE) ---
        turn_to_moves = {t.get('id'): [] for t in turns}
        for link in links:
            if link.get('edge_type') == 'HAS_MOVE':
                src = link.get('source')
                if src in turn_to_moves:
                    turn_to_moves[src].append(link.get('target'))

        move_dict = {n.get('id'): n for n in nodes if n.get('node_type') == 'Move'}

        has_repair_attempt = False
        for turn in turns:
            m_ids = turn_to_moves.get(turn.get('id'), [])
            m_types = [move_dict[m].get('move_type') for m in m_ids if m in move_dict]

            is_repair_turn = any(t in ('REPAIR_INITIATE', 'ESCALATE', 'REPAIR_FAIL') for t in m_types)
            if is_repair_turn:
                total_repair_turns += 1
                has_repair_attempt = True

        if has_repair_attempt:
            convs_with_repair += 1

        # --- CA-grounded metrics ---
        for n in nodes:
            if n.get('node_type') != 'Move':
                continue
            mt = n.get('move_type', '')
            # Grounding evidence (Clark & Brennan 1991)
            if mt == 'ACKNOWLEDGE_CONSTRAINT':
                grounding_demonstration += 1
            elif mt == 'ACCEPT_CONSTRAINT':
                grounding_token += 1
            elif mt == 'SILENT_COMPLY':
                grounding_unmarked += 1
            # Self-repair (Schegloff SISR)
            if mt == 'SELF_REPAIR':
                self_repair_count += 1
            # Repair organization
            ro = n.get('repair_organization')
            if ro:
                repair_org[ro] += 1

        # Count assistant turns for self-repair rate
        total_assistant_turns += sum(
            1 for t in turns if t.get('role') == 'assistant'
        )

        # --- Patience: how long do users stick around after first violation? ---
        if violations:
            first_v_turn = min(v.get('turn_index', 0) for v in violations)
            max_turn = max(t.get('turn_index', 0) for t in turns) if turns else 0
            patience = max(0, max_turn - first_v_turn)

            all_violated = all(c.get('current_state') in ('VIOLATED', 'ABANDONED') for c in constraints)
            if all_violated:
                patience_abandoned.append(patience)
            else:
                patience_survived.append(patience)

    # --- Collapse ---
    collapse = {}
    if collapse_file.exists():
        with open(collapse_file) as f:
            collapse_data = json.load(f)
        n_collapse = sum(1 for x in collapse_data if x.get('collapse'))
        n_total = len(collapse_data)
        collapse = {
            'n_conversations': n_total,
            'n_collapse': n_collapse,
            'collapse_rate_pct': round(n_collapse / n_total * 100, 1) if n_total else 0,
        }

    # --- Compute derived numbers ---
    turn_0_violations = sum(1 for t in turns_until_violated if t == 0)
    turn_dist = Counter(turns_until_violated)
    repair_density = total_repair_turns / total_turns_in_constrained if total_turns_in_constrained else 0

    results = {
        # Corpus
        'n_graphs': n_graphs,
        'n_with_constraints': n_with_constraints,

        # Constraint outcomes
        'total_constraints': total_constraints,
        'violated': violated,
        'followed': followed,
        'ambiguous': ambiguous,
        'pct_violated': round(violated / total_constraints * 100, 1),
        'pct_followed': round(followed / total_constraints * 100, 1),
        'pct_ambiguous': round(ambiguous / total_constraints * 100, 1),

        # Timing
        'median_turns_to_violation': statistics.median(turns_until_violated) if turns_until_violated else None,
        'mean_turns_to_violation': round(statistics.mean(turns_until_violated), 2) if turns_until_violated else None,
        'turn_0_violations': turn_0_violations,
        'pct_turn_0': round(turn_0_violations / len(turns_until_violated) * 100, 1) if turns_until_violated else 0,
        'turns_until_violated_distribution': {str(k): v for k, v in sorted(turn_dist.items())},

        # Repair
        'total_violation_events': total_violation_events,
        'repaired_events': repaired_events,
        'repair_success_pct': round(repaired_events / total_violation_events * 100, 2) if total_violation_events else 0,
        'convs_with_repair_attempts': convs_with_repair,
        'pct_convs_with_repair': round(convs_with_repair / n_with_constraints * 100, 1) if n_with_constraints else 0,

        # Repair density
        'total_repair_turns': total_repair_turns,
        'total_turns_in_constrained': total_turns_in_constrained,
        'repair_density_pct': round(repair_density * 100, 2),

        # Patience
        'patience_abandoned': {
            'n': len(patience_abandoned),
            'mean': round(statistics.mean(patience_abandoned), 1) if patience_abandoned else 0,
            'median': round(statistics.median(patience_abandoned), 1) if patience_abandoned else 0,
        },
        'patience_survived': {
            'n': len(patience_survived),
            'mean': round(statistics.mean(patience_survived), 1) if patience_survived else 0,
            'median': round(statistics.median(patience_survived), 1) if patience_survived else 0,
        },

        # Collapse
        'agency_collapse': collapse,

        # CA-grounded metrics (Clark & Brennan 1991)
        'grounding_evidence_distribution': {
            'demonstration': grounding_demonstration,
            'token': grounding_token,
            'unmarked': grounding_unmarked,
        },
        'pct_demonstration_grounding': round(
            grounding_demonstration / max(1, grounding_demonstration + grounding_token + grounding_unmarked) * 100, 1
        ),
        'self_repair_count': self_repair_count,
        'self_repair_rate_pct': round(
            self_repair_count / max(1, total_assistant_turns) * 100, 2
        ),
        'total_assistant_turns_in_constrained': total_assistant_turns,
        'repair_organization_distribution': dict(repair_org),
    }

    return results


def main():
    print("Computing verified statistics...")
    results = compute_stats()

    # Print summary
    print(f"\n  Graphs: {results['n_graphs']}")
    print(f"  With constraints: {results['n_with_constraints']}")
    print(f"  Total constraints: {results['total_constraints']}")
    print(f"    Violated: {results['violated']} ({results['pct_violated']}%)")
    print(f"    Followed: {results['followed']} ({results['pct_followed']}%)")
    print(f"    Ambiguous: {results['ambiguous']} ({results['pct_ambiguous']}%)")
    print(f"  Median turns to violation: {results['median_turns_to_violation']}")
    print(f"  Turn 0 violations: {results['turn_0_violations']} ({results['pct_turn_0']}%)")
    print(f"  Repair success: {results['repaired_events']}/{results['total_violation_events']} ({results['repair_success_pct']}%)")
    print(f"  Users who tried repair: {results['convs_with_repair_attempts']}/{results['n_with_constraints']} ({results['pct_convs_with_repair']}%)")
    print(f"  Repair density: {results['repair_density_pct']}% of turns")
    print(f"  Patience (abandoned): mean {results['patience_abandoned']['mean']} turns")
    print(f"  Patience (survived): mean {results['patience_survived']['mean']} turns")
    if results['agency_collapse']:
        print(f"  Agency Collapse: {results['agency_collapse']['collapse_rate_pct']}%")

    # CA metrics
    ge = results['grounding_evidence_distribution']
    print(f"\n  --- CA-Grounded Metrics (Clark & Brennan 1991) ---")
    print(f"  Grounding evidence: demonstration={ge['demonstration']}, token={ge['token']}, unmarked={ge['unmarked']}")
    print(f"  Understanding demonstrations: {results['pct_demonstration_grounding']}%")
    print(f"  Self-repair (SISR): {results['self_repair_count']} ({results['self_repair_rate_pct']}% of assistant turns)")
    print(f"  Repair organization: {results['repair_organization_distribution']}")

    out = OUTPUT_DIR / "verified_stats.json"
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out}")


if __name__ == '__main__':
    main()
