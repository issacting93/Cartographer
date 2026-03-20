#!/usr/bin/env python3
"""
Compute and save all key statistics to JSON for verified reporting.
This script is the SINGLE SOURCE OF TRUTH for numbers in the findings report.

Outputs: data/v2_unified/reports/verified_stats.json
"""

import json
import csv
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONV_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
EVIDENCE_CSV = PROJECT_ROOT / "data" / "v2_unified" / "evidence_features.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"


def iter_valid_graphs():
    """Iterate over valid graph JSON files, skipping error-named files."""
    for f in sorted(GRAPHS_DIR.glob('*.json')):
        if '-error' in f.stem:
            continue
        yield f


EVIDENCE_COLS = [
    'div_mean', 'div_variance', 'div_trend', 'div_max_spike', 'div_range',
    'expr_mean', 'expr_variance', 'expr_trend', 'expr_range', 'expr_shift',
    'repair_rate', 'constraint_pressure', 'hedge_assert_ratio',
    'ai_refusal_rate', 'goal_drift_mean', 'goal_drift_variance', 'goal_stability',
    'length_ratio',
    'affect_mean', 'affect_variance', 'affect_trend', 'affect_range',
    'affect_max', 'affect_min', 'affect_peak_count', 'affect_valley_count',
    'valence_mean', 'valence_variance', 'valence_trend',
    'n_messages_log',
]

CHANNEL_MAP = {
    'div_mean': 'Divergence', 'div_variance': 'Divergence', 'div_trend': 'Divergence',
    'div_max_spike': 'Divergence', 'div_range': 'Divergence',
    'expr_mean': 'Expressiveness', 'expr_variance': 'Expressiveness',
    'expr_trend': 'Expressiveness', 'expr_range': 'Expressiveness', 'expr_shift': 'Expressiveness',
    'repair_rate': 'Dynamics', 'constraint_pressure': 'Dynamics',
    'hedge_assert_ratio': 'Dynamics', 'ai_refusal_rate': 'Dynamics',
    'goal_drift_mean': 'Dynamics', 'goal_drift_variance': 'Dynamics', 'goal_stability': 'Dynamics',
    'length_ratio': 'Structure',
    'affect_mean': 'Affect', 'affect_variance': 'Affect', 'affect_trend': 'Affect',
    'affect_range': 'Affect', 'affect_max': 'Affect', 'affect_min': 'Affect',
    'affect_peak_count': 'Affect', 'affect_valley_count': 'Affect',
    'valence_mean': 'Affect', 'valence_variance': 'Affect', 'valence_trend': 'Affect',
    'n_messages_log': 'Structure',
}


def load_data():
    """Load conversations and evidence features."""
    convs = {}
    for f in sorted(CONV_DIR.glob('*.json')):
        with open(f) as fh:
            convs[f.stem] = json.load(fh)

    evidence = {}
    with open(EVIDENCE_CSV) as f:
        for row in csv.DictReader(f):
            evidence[row['conv_id']] = row

    return convs, evidence


def compute_role_pair_rf(convs, evidence):
    """
    Train RF to predict role-pair from evidence features.
    This is the CORRECT computation for the feature importance figure.
    Target: dominant_human_role + dominant_ai_role concatenated.
    """
    print("\n" + "=" * 60)
    print("COMPUTING: RF for role-pair prediction")
    print("=" * 60)

    common_ids = sorted(set(evidence.keys()) & set(convs.keys()))

    X_rows = []
    y_labels = []
    valid_ids = []

    for cid in common_ids:
        data = convs[cid]
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})
        if not hr or not ar:
            continue

        human_role = max(hr, key=hr.get)
        ai_role = max(ar, key=ar.get)
        role_pair = f"{human_role}|{ai_role}"

        row = [float(evidence[cid].get(col, 0)) for col in EVIDENCE_COLS]
        X_rows.append(row)
        y_labels.append(role_pair)
        valid_ids.append(cid)

    X = np.array(X_rows)
    X = np.nan_to_num(X, nan=0.0)

    # Filter to role pairs with >= 10 samples for stable CV
    pair_counts = Counter(y_labels)
    valid_pairs = {p for p, c in pair_counts.items() if c >= 10}
    mask = [y in valid_pairs for y in y_labels]

    X_filtered = X[mask]
    y_filtered = [y for y, m in zip(y_labels, mask) if m]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y_filtered)

    n_classes = len(set(y_encoded))
    chance = 1.0 / n_classes

    print(f"  N conversations: {len(X_filtered)}")
    print(f"  N role pairs (>= 10 samples): {n_classes}")
    print(f"  Chance level: {chance:.1%}")
    print(f"  Role pairs: {dict(Counter(y_filtered).most_common())}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_filtered)

    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(rf, X_scaled, y_encoded, cv=cv, scoring='accuracy')

    mean_acc = float(scores.mean())
    std_acc = float(scores.std())

    print(f"  RF accuracy: {mean_acc:.1%} +/- {std_acc:.1%}")

    # Now train on full data for feature importances
    rf.fit(X_scaled, y_encoded)
    importances = rf.feature_importances_

    feature_importance = {}
    for col, imp in zip(EVIDENCE_COLS, importances):
        feature_importance[col] = {
            'importance': float(imp),
            'channel': CHANNEL_MAP.get(col, 'Unknown'),
        }

    # Sort by importance, get top 15
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1]['importance'], reverse=True)
    top_15 = sorted_features[:15]

    print(f"\n  Top 15 features:")
    for name, data in top_15:
        print(f"    {name:30s} {data['importance']:.4f} ({data['channel']})")

    # Channel contributions
    channel_totals = defaultdict(float)
    total_importance = sum(imp for imp in importances)
    for col, imp in zip(EVIDENCE_COLS, importances):
        channel = CHANNEL_MAP.get(col, 'Unknown')
        channel_totals[channel] += imp

    channel_pcts = {ch: round(val / total_importance * 100, 1) for ch, val in channel_totals.items()}
    print(f"\n  Channel contributions:")
    for ch, pct in sorted(channel_pcts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {ch:20s} {pct:.1f}%")

    return {
        'target': 'role_pair',
        'n_conversations': len(X_filtered),
        'n_classes': n_classes,
        'chance_level': round(chance, 4),
        'rf_accuracy_mean': round(mean_acc, 4),
        'rf_accuracy_std': round(std_acc, 4),
        'cv_folds': 5,
        'n_estimators': 200,
        'feature_importance': {name: data for name, data in sorted_features},
        'top_15': [{'feature': name, 'importance': round(data['importance'], 4), 'channel': data['channel']} for name, data in top_15],
        'channel_contributions': channel_pcts,
    }


def compute_variance_ratio(convs, evidence):
    """Compute the IS→ES affect variance ratio from current data."""
    print("\n" + "=" * 60)
    print("COMPUTING: IS→ES Variance Ratio")
    print("=" * 60)

    is_es = []
    for cid, data in convs.items():
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})
        if not hr or not ar:
            continue
        if max(hr, key=hr.get) == 'information-seeker' and max(ar, key=ar.get) == 'expert-system':
            ev = evidence.get(cid, {})
            av = float(ev.get('affect_variance', 0))
            n_msgs = len(data.get('messages', []))
            if n_msgs >= 6 and av > 0:
                is_es.append({'conv_id': cid, 'affect_variance': av, 'n_messages': n_msgs})

    by_var = sorted(is_es, key=lambda x: x['affect_variance'])
    smooth = by_var[0]
    volatile = by_var[-1]
    ratio = volatile['affect_variance'] / smooth['affect_variance']

    print(f"  IS→ES pairs (>= 6 messages, variance > 0): {len(is_es)}")
    print(f"  Smoothest: {smooth['conv_id']} (variance: {smooth['affect_variance']:.10f})")
    print(f"  Most volatile: {volatile['conv_id']} (variance: {volatile['affect_variance']:.10f})")
    print(f"  Variance ratio: {ratio:,.0f}x")

    return {
        'n_is_es_pairs': len(is_es),
        'min_messages_filter': 6,
        'smooth_id': smooth['conv_id'],
        'smooth_variance': smooth['affect_variance'],
        'volatile_id': volatile['conv_id'],
        'volatile_variance': volatile['affect_variance'],
        'variance_ratio': round(ratio, 0),
        'variance_ratio_exact': ratio,
    }


def compute_corpus_stats(convs):
    """Compute basic corpus statistics."""
    print("\n" + "=" * 60)
    print("COMPUTING: Corpus Statistics")
    print("=" * 60)

    sources = Counter()
    lengths = []
    n_with_roles = 0

    human_roles = Counter()
    ai_roles = Counter()
    role_pairs = Counter()
    purposes = Counter()

    for cid, data in convs.items():
        src = data.get('source', 'unknown')
        if src == 'WildChat':
            src = 'wildchat'
        sources[src] += 1
        lengths.append(len(data.get('messages', [])))

        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})

        if hr and ar:
            n_with_roles += 1
            h = max(hr, key=hr.get)
            a = max(ar, key=ar.get)
            human_roles[h] += 1
            ai_roles[a] += 1
            role_pairs[f"{h}|{a}"] += 1

        purpose = (cls.get('conversationPurpose') or {}).get('category', '')
        if purpose:
            purposes[purpose] += 1

    instrumental_roles = {'information-seeker', 'director', 'provider', 'collaborator'}
    n_instrumental = sum(human_roles[r] for r in instrumental_roles)
    pct_instrumental = n_instrumental / n_with_roles * 100 if n_with_roles > 0 else 0

    import statistics as stats_mod
    median_len = stats_mod.median(lengths)
    mean_len = stats_mod.mean(lengths)

    print(f"  Total conversations: {len(convs)}")
    print(f"  With role classifications: {n_with_roles}")
    print(f"  Sources: {dict(sources)}")
    print(f"  Median length: {median_len}")
    print(f"  Mean length: {mean_len:.1f}")
    print(f"  Instrumental: {n_instrumental}/{n_with_roles} = {pct_instrumental:.1f}%")

    return {
        'total_conversations': len(convs),
        'conversations_with_roles': n_with_roles,
        'sources': dict(sources.most_common()),
        'median_length': median_len,
        'mean_length': round(mean_len, 1),
        'human_roles': dict(human_roles.most_common()),
        'ai_roles': dict(ai_roles.most_common()),
        'role_pairs': dict(role_pairs.most_common()),
        'purposes': dict(purposes.most_common()),
        'n_instrumental': n_instrumental,
        'pct_instrumental': round(pct_instrumental, 1),
        'n_expressive': n_with_roles - n_instrumental,
        'pct_expressive': round(100 - pct_instrumental, 1),
    }


def compute_constraint_stats():
    """
    Compute constraint/collapse stats from atlas_canonical graph data.
    These are the headline numbers: 71.5% failure, half-life, repair rate, collapse rate.
    """
    import statistics as stats_mod

    print("\n" + "=" * 60)
    print("COMPUTING: Constraint & Collapse Statistics (atlas_canonical)")
    print("=" * 60)

    COLLAPSE_FILE = PROJECT_ROOT / "data" / "features_llm_collapse.json"

    # --- Constraint survival/violation ---
    total_constraints = 0
    survived = 0
    violated = 0
    half_lives = []
    total_violation_events = 0
    repaired_events = 0
    n_graphs = 0
    per_conv_repair_rates = []

    for f in iter_valid_graphs():
        with open(f) as fh:
            g = json.load(fh)
        n_graphs += 1

        constraints = {}
        violations = []
        conv_violations = 0
        conv_repaired = 0

        for node in g['nodes']:
            nt = node.get('node_type', '')
            if nt == 'Constraint':
                total_constraints += 1
                state = node.get('current_state', '')
                if state == 'SURVIVED':
                    survived += 1
                elif state == 'VIOLATED':
                    violated += 1
                constraints[node.get('constraint_id', node.get('id'))] = node

            elif nt == 'ViolationEvent' and node.get('violation_type') == 'constraint_violation':
                total_violation_events += 1
                conv_violations += 1
                violations.append(node)
                if node.get('was_repaired'):
                    repaired_events += 1
                    conv_repaired += 1

        if conv_violations > 0:
            per_conv_repair_rates.append(conv_repaired / conv_violations)

        # Compute half-lives for violated constraints
        for c_id, c in constraints.items():
            if c.get('times_violated', 0) > 0:
                intro = c.get('introduced_at', 0)
                c_viols = [v for v in violations if v.get('constraint_id') == c.get('constraint_id')]
                if c_viols:
                    first_v_turn = min(v.get('turn_index', 999) for v in c_viols)
                    hl = first_v_turn - intro
                    if hl >= 0:
                        half_lives.append(hl)

    survival_rate = survived / total_constraints * 100 if total_constraints > 0 else 0
    violation_rate = violated / total_constraints * 100 if total_constraints > 0 else 0
    repair_event_rate = repaired_events / total_violation_events * 100 if total_violation_events > 0 else 0
    mean_per_conv_repair = stats_mod.mean(per_conv_repair_rates) * 100 if per_conv_repair_rates else 0
    median_half_life = stats_mod.median(half_lives) if half_lives else None
    mean_half_life = stats_mod.mean(half_lives) if half_lives else None

    print(f"  Graphs loaded: {n_graphs}")
    print(f"  Total constraints: {total_constraints}")
    print(f"  Survived: {survived} ({survival_rate:.1f}%)")
    print(f"  Violated: {violated} ({violation_rate:.1f}%)")
    print(f"  Half-life (median): {median_half_life} turns")
    print(f"  Half-life (mean): {mean_half_life:.2f} turns")
    print(f"  Turn-0 violations: {half_lives.count(0)} ({half_lives.count(0)/len(half_lives)*100:.1f}% of violated)")
    print(f"  Violation events: {total_violation_events}, repaired: {repaired_events}")
    print(f"  Repair rate (event-level): {repair_event_rate:.2f}%")
    print(f"  Repair rate (mean per-conv): {mean_per_conv_repair:.2f}%")

    # --- Agency Collapse ---
    collapse_result = {}
    if COLLAPSE_FILE.exists():
        with open(COLLAPSE_FILE) as f:
            collapse_data = json.load(f)
        n_collapse = sum(1 for x in collapse_data if x.get('collapse'))
        n_total = len(collapse_data)
        collapse_rate = n_collapse / n_total * 100 if n_total > 0 else 0
        print(f"\n  Collapse data: {n_total} conversations")
        print(f"  Agency Collapse: {n_collapse}/{n_total} = {collapse_rate:.1f}%")
        collapse_result = {
            'n_conversations': n_total,
            'n_collapse': n_collapse,
            'collapse_rate_pct': round(collapse_rate, 1),
        }
    else:
        print(f"\n  WARNING: {COLLAPSE_FILE} not found, skipping collapse stats")

    return {
        'source': 'atlas_canonical',
        'n_graphs': n_graphs,
        'total_constraints': total_constraints,
        'survived': survived,
        'violated': violated,
        'survival_rate_pct': round(survival_rate, 1),
        'violation_rate_pct': round(violation_rate, 1),
        'half_life_median': median_half_life,
        'half_life_mean': round(mean_half_life, 2) if mean_half_life else None,
        'turn_0_violations': half_lives.count(0),
        'turn_0_violation_pct': round(half_lives.count(0) / len(half_lives) * 100, 1) if half_lives else 0,
        'half_life_distribution': {str(k): half_lives.count(k) for k in sorted(set(half_lives))} if half_lives else {},
        'total_violation_events': total_violation_events,
        'repaired_events': repaired_events,
        'repair_rate_event_pct': round(repair_event_rate, 2),
        'repair_rate_per_conv_mean_pct': round(mean_per_conv_repair, 2),
        'agency_collapse': collapse_result,
    }


def compute_cascade_stats():
    """
    Compute cascade and repair density stats from atlas_canonical graph data.
    Reads graph JSONs directly — no pipeline re-run needed.
    """
    import statistics as stats_mod

    print("\n" + "=" * 60)
    print("COMPUTING: Cascade & Repair Density Statistics")
    print("=" * 60)

    total_constrained_convs = 0
    cascade_entries = 0
    cascade_collapses = 0
    total_repair_turns = 0
    total_turns_constrained = 0
    patience_abandoned = []
    patience_survived = []

    for f in iter_valid_graphs():
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
                if source in turn_to_moves:
                    turn_to_moves[source].append(edge.get('target'))

        move_dict = {n.get('id'): n for n in nodes if n.get('node_type') == 'Move'}

        # Cascade detection: 5+ consecutive turns with repair-related moves
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

        # Patience: turns from first violation to end
        viols = [n.get('turn_index', 0) for n in nodes if n.get('node_type') == 'ViolationEvent']
        if viols:
            first_violation_turn = min(viols)
            max_turn = max([t.get('turn_index', 0) for t in turns]) if turns else 0
            p_val = max(0, max_turn - first_violation_turn)

            final_states = [c.get('current_state') for c in constraints]
            is_abandoned = all(s in ['ABANDONED', 'VIOLATED'] for s in final_states)

            if is_abandoned:
                patience_abandoned.append(p_val)
            else:
                patience_survived.append(p_val)

    entry_rate = cascade_entries / total_constrained_convs if total_constrained_convs > 0 else 0
    collapse_rate = cascade_collapses / cascade_entries if cascade_entries > 0 else 0
    escape_prob = 1.0 - collapse_rate if cascade_entries > 0 else 0
    density = total_repair_turns / total_turns_constrained if total_turns_constrained > 0 else 0

    print(f"  Constrained conversations: {total_constrained_convs}")
    print(f"  Repair turns / total turns: {total_repair_turns}/{total_turns_constrained} = {density:.4f}")
    print(f"  Cascade entries: {cascade_entries} ({entry_rate:.1%})")
    print(f"  Cascade collapses: {cascade_collapses} ({collapse_rate:.1%})")
    print(f"  Escape probability: {escape_prob:.1%}")
    print(f"  Patience (abandoned): N={len(patience_abandoned)}, mean={stats_mod.mean(patience_abandoned) if patience_abandoned else 0:.1f}")
    print(f"  Patience (survived): N={len(patience_survived)}, mean={stats_mod.mean(patience_survived) if patience_survived else 0:.1f}")

    return {
        'n_constrained_convs': total_constrained_convs,
        'total_repair_turns': total_repair_turns,
        'total_turns_constrained': total_turns_constrained,
        'repair_density': round(density, 4),
        'cascade_entries': cascade_entries,
        'cascade_entry_rate': round(entry_rate, 4),
        'cascade_collapses': cascade_collapses,
        'cascade_collapse_rate': round(collapse_rate, 4),
        'escape_probability': round(escape_prob, 4),
        'patience': {
            'mean_abandonment_turns': round(stats_mod.mean(patience_abandoned), 2) if patience_abandoned else 0,
            'median_abandonment_turns': round(stats_mod.median(patience_abandoned), 2) if patience_abandoned else 0,
            'mean_persistence_turns': round(stats_mod.mean(patience_survived), 2) if patience_survived else 0,
            'median_persistence_turns': round(stats_mod.median(patience_survived), 2) if patience_survived else 0,
            'abandonment_cases': len(patience_abandoned),
            'persistence_cases': len(patience_survived),
        },
    }


def compute_mode_violation_stats():
    """
    Compute mode violation stats from atlas_canonical graph data.
    """
    print("\n" + "=" * 60)
    print("COMPUTING: Mode Violation Statistics")
    print("=" * 60)

    total_mode_pairs = 0
    total_violations = 0
    violation_types = Counter()

    for f in iter_valid_graphs():
        with open(f) as fh:
            g = json.load(fh)

        for node in g.get('nodes', []):
            if node.get('node_type') == 'InteractionMode':
                total_mode_pairs += 1
                if node.get('is_violation') in (True, 'True', 'true'):
                    total_violations += 1
                    vtype = node.get('violation_type', 'Unknown')
                    if vtype:
                        violation_types[vtype] += 1

    violation_rate = total_violations / total_mode_pairs * 100 if total_mode_pairs > 0 else 0

    print(f"  Total mode pairs: {total_mode_pairs}")
    print(f"  Total violations: {total_violations} ({violation_rate:.1f}%)")
    for vtype, count in violation_types.most_common():
        pct = count / total_violations * 100 if total_violations > 0 else 0
        print(f"    {vtype}: {count} ({pct:.1f}%)")

    return {
        'total_mode_pairs': total_mode_pairs,
        'total_violations': total_violations,
        'violation_rate_pct': round(violation_rate, 1),
        'violation_types': {k: {'count': v, 'pct': round(v / total_violations * 100, 1) if total_violations > 0 else 0} for k, v in violation_types.most_common()},
    }


def main():
    print("=" * 60)
    print("COMPUTING VERIFIED STATISTICS")
    print("=" * 60)

    convs, evidence = load_data()
    print(f"  Loaded {len(convs)} conversations, {len(evidence)} evidence records")

    results = {}
    results['corpus'] = compute_corpus_stats(convs)
    results['variance_ratio'] = compute_variance_ratio(convs, evidence)
    results['rf_role_pair'] = compute_role_pair_rf(convs, evidence)
    results['constraints'] = compute_constraint_stats()
    results['cascade'] = compute_cascade_stats()
    results['mode_violations'] = compute_mode_violation_stats()

    output_path = OUTPUT_DIR / "verified_stats.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"SAVED: {output_path}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
