#!/usr/bin/env python3
"""Export canonical Atlas data into a single dashboard_data.json for the findings dashboard."""

import json
import glob
import os
from collections import defaultdict

BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'atlas_canonical')
METRICS_DIR = os.path.join(BASE, 'metrics')
GRAPHS_DIR = os.path.join(BASE, 'graphs')
OUTPUT = os.path.join(BASE, 'dashboard_data.json')


def load_json(path):
    with open(path) as f:
        return json.load(f)


def scan_graphs():
    """Scan all graph JSONs for node-level constraint and violation data."""
    constraint_states = defaultdict(int)  # SURVIVED / VIOLATED
    violation_timing = defaultdict(int)   # turn_index -> count (constraint violations only)
    mode_violation_types = defaultdict(int)  # UNSOLICITED_ADVICE etc
    mode_by_source = defaultdict(lambda: defaultdict(int))  # source -> type -> count
    total_constraint_violations = 0
    total_mode_violations = 0
    repair_moves = 0  # Count of REPAIR_INITIATE + REPAIR_EXECUTE moves

    for path in sorted(glob.glob(os.path.join(GRAPHS_DIR, '*.json'))):
        data = load_json(path)
        nodes = data.get('nodes', [])

        # Find source from Conversation node
        source = 'Unknown'
        for n in nodes:
            if n.get('node_type') == 'Conversation':
                source = n.get('source', 'Unknown')
                break

        # Process Constraint nodes
        for n in nodes:
            if n.get('node_type') == 'Constraint':
                state = n.get('current_state', '')
                if state == 'SURVIVED':
                    constraint_states['SURVIVED'] += 1
                elif state == 'VIOLATED':
                    constraint_states['VIOLATED'] += 1
                elif state == 'ACTIVE':
                    # Still active at end = survived
                    constraint_states['SURVIVED'] += 1

        # Process ViolationEvent nodes
        for n in nodes:
            if n.get('node_type') == 'ViolationEvent':
                vtype = n.get('violation_type', '')
                constraint_id = n.get('constraint_id', '')
                turn = n.get('turn_index', 0)

                if constraint_id == 'mode' or vtype in ('UNSOLICITED_ADVICE', 'PREMATURE_EXECUTION', 'EXECUTION_AVOIDANCE'):
                    # Mode violation
                    total_mode_violations += 1
                    mode_violation_types[vtype] += 1
                    mode_by_source[source][vtype] += 1
                else:
                    # Constraint violation
                    total_constraint_violations += 1
                    violation_timing[turn] += 1
        # Count repair moves (REPAIR_INITIATE / REPAIR_EXECUTE)
        for n in nodes:
            if n.get('node_type') == 'Move' and n.get('move_type', '').startswith('REPAIR_'):
                repair_moves += 1

    return {
        'constraint_states': dict(constraint_states),
        'violation_timing': dict(sorted(violation_timing.items())),
        'mode_violation_types': dict(sorted(mode_violation_types.items(), key=lambda x: -x[1])),
        'mode_by_source': {k: dict(v) for k, v in mode_by_source.items()},
        'total_constraint_violations': total_constraint_violations,
        'total_mode_violations': total_mode_violations,
        'repair_moves': repair_moves,
    }


def build_per_conversation(all_metrics):
    """Build per-conversation array for scatter plots."""
    return [
        {
            'id': m['conversation_id'],
            'drift': m['drift_velocity'],
            'tax': m['agency_tax'],
            'survival': m['constraint_survival_rate'],
            'class': m['stability_class'],
            'arch': m['task_architecture'],
            'turns': m['total_turns'],
            'violations': m['total_violations'],
            'constraints': m['total_constraints'],
            'mode_violation_rate': m['mode_violation_rate'],
        }
        for m in all_metrics
    ]


def main():
    aggregate = load_json(os.path.join(METRICS_DIR, 'aggregate.json'))
    all_metrics = load_json(os.path.join(METRICS_DIR, 'all_metrics.json'))
    graph_data = scan_graphs()

    total_constraints = aggregate['overall']['total_constraints']
    survived = graph_data['constraint_states'].get('SURVIVED', 0)
    violated = graph_data['constraint_states'].get('VIOLATED', 0)
    constraint_violations = graph_data['total_constraint_violations']
    repair_moves = graph_data['repair_moves']
    # Use aggregate total_repairs (54) as the canonical repair count
    # repair_moves from graphs counts REPAIR_INITIATE + REPAIR_EXECUTE move nodes
    repairs = aggregate['overall']['total_repairs']

    # Build KPIs
    survival_rate = survived / total_constraints if total_constraints > 0 else 0
    repair_rate = repairs / constraint_violations if constraint_violations > 0 else 0

    kpis = {
        'constraint_survival': {
            'value': round(survival_rate * 100, 1),
            'detail': f'{survived}/{total_constraints}',
            'label': 'Constraint Survival',
        },
        'turn_half_life': {
            'value': round(aggregate['overall']['mean_constraint_half_life'], 2),
            'label': 'Turn Half-Life',
        },
        'repair_rate': {
            'value': round(repair_rate * 100, 1),
            'detail': f'{repairs}/{constraint_violations} constraint violations',
            'label': 'Repair Rate',
        },
        'mode_violation_rate': {
            'value': round(aggregate['overall']['mean_mode_violation_rate'] * 100, 1),
            'label': 'Mode Violation Rate',
        },
    }

    # Build architecture radar data
    arch_keys = ['Analysis', 'Generation', 'Information Seeking', 'Planning', 'Transformation']
    metrics_for_radar = ['mean_drift_velocity', 'mean_agency_tax', 'mean_survival_rate',
                         'mean_mode_violation_rate', 'mean_move_coverage']
    by_arch = {}
    for arch in arch_keys:
        if arch in aggregate['by_architecture']:
            a = aggregate['by_architecture'][arch]
            by_arch[arch] = {
                'n': a['n'],
                'drift_velocity': a['mean_drift_velocity'],
                'agency_tax': a['mean_agency_tax'],
                'survival_rate': a['mean_survival_rate'],
                'mode_violation_rate': a['mean_mode_violation_rate'],
                'move_coverage': a['mean_move_coverage'],
                'constraint_half_life': a['mean_constraint_half_life'],
                'total_violations': a['total_violations'],
                'total_constraints': a['total_constraints'],
            }

    # Build stability class table data
    by_class = {}
    for cls, data in aggregate['by_stability_class'].items():
        by_class[cls] = {
            'n': data['n'],
            'drift_velocity': data['mean_drift_velocity'],
            'agency_tax': data['mean_agency_tax'],
            'survival_rate': data['mean_survival_rate'],
            'mode_violation_rate': data['mean_mode_violation_rate'],
            'constraint_half_life': data['mean_constraint_half_life'],
            'total_violations': data['total_violations'],
            'total_repairs': data['total_repairs'],
            'total_constraints': data['total_constraints'],
        }

    output = {
        'kpis': kpis,
        'violation_timing': graph_data['violation_timing'],
        'constraint_states': graph_data['constraint_states'],
        'mode_violation_types': graph_data['mode_violation_types'],
        'mode_by_source': graph_data['mode_by_source'],
        'total_constraint_violations': constraint_violations,
        'total_mode_violations': graph_data['total_mode_violations'],
        'repair_attempts': repairs,
        'repair_moves_from_graphs': repair_moves,
        'total_repairs_from_aggregate': aggregate['overall']['total_repairs'],
        'by_architecture': by_arch,
        'by_stability_class': by_class,
        'per_conversation': build_per_conversation(all_metrics),
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'Wrote {OUTPUT}')
    print(f'  Constraints: {total_constraints} (survived={survived}, violated={violated})')
    print(f'  Constraint violations: {constraint_violations}, repairs (aggregate): {repairs}, repair moves (graphs): {repair_moves}')
    print(f'  Mode violations: {graph_data["total_mode_violations"]}')
    print(f'  Survival rate: {survival_rate*100:.1f}%')
    print(f'  Repair rate: {repair_rate*100:.1f}%')


def embed():
    """Embed dashboard_data.json into dashboard.html for offline use."""
    if not os.path.exists(OUTPUT):
        main()
    with open(OUTPUT) as f:
        data = json.load(f)
    data_json = json.dumps(data, separators=(',', ':'))

    html_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    with open(html_path) as f:
        html = f.read()

    import re
    html = re.sub(
        r'<script id="embedded-data">.*?</script>',
        '<script id="embedded-data">\nconst EMBEDDED_DATA = ' + data_json + ';\n</script>',
        html,
        flags=re.DOTALL,
    )

    with open(html_path, 'w') as f:
        f.write(html)
    print(f'Embedded {len(data_json)} bytes into {html_path}')


if __name__ == '__main__':
    import sys
    if '--embed' in sys.argv:
        embed()
    else:
        main()
