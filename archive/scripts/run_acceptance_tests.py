#!/usr/bin/env python3
"""
Acceptance Tests: No-Leakage Gates (v2)
========================================
Verifies that evidence features are independent of classification labels.

Test A: Predict labels from evidence features (should NOT be near-perfect)
Test B: Predict evidence from labels (should NOT be near-perfect)
Test C: Feature screening (flag high correlations)

Plus: Ablation study with strict feature-set discipline.

Usage:
  python3 scripts/run_acceptance_tests.py
"""

import json
import csv
import os
import sys
import numpy as np
import statistics
from pathlib import Path
from collections import Counter

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
EVIDENCE_CSV = PROJECT_ROOT / "data" / "v2_unified" / "evidence_features.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "reports"

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

LABEL_FEATURES = [
    'human_seeker', 'human_provider', 'human_collaborator',
    'human_director', 'human_expressor', 'human_peer',
    'ai_expert', 'ai_facilitator', 'ai_advisor',
    'ai_constructor', 'ai_social', 'ai_peer',
    'pattern_qa', 'pattern_collaborative', 'pattern_storytelling',
    'pattern_advisory', 'pattern_casual',
    'tone_playful', 'tone_neutral', 'tone_serious', 'tone_supportive',
    'purpose_info', 'purpose_entertainment', 'purpose_relationship',
    'purpose_self_expression',
]


def load_data():
    """Load evidence features and classification labels."""
    evidence_data = {}
    with open(EVIDENCE_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence_data[row['conv_id']] = row

    label_data = {}
    for fpath in sorted(CANONICAL_DIR.glob('*.json')):
        conv_id = fpath.stem
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            c = data.get('classification', {})
            if not c:
                continue

            hr = (c.get('humanRole') or {}).get('distribution', {})
            ar = (c.get('aiRole') or {}).get('distribution', {})

            labels = {}
            labels['human_seeker'] = hr.get('information-seeker', 0)
            labels['human_provider'] = hr.get('provider', 0)
            labels['human_collaborator'] = hr.get('collaborator', 0)
            labels['human_director'] = hr.get('director', 0)
            labels['human_expressor'] = hr.get('social-expressor', 0)
            labels['human_peer'] = hr.get('relational-peer', 0)
            labels['ai_expert'] = ar.get('expert-system', 0)
            labels['ai_facilitator'] = ar.get('learning-facilitator', 0)
            labels['ai_advisor'] = ar.get('advisor', 0)
            labels['ai_constructor'] = ar.get('co-constructor', 0)
            labels['ai_social'] = ar.get('social-facilitator', 0)
            labels['ai_peer'] = ar.get('relational-peer', 0)

            pattern = (c.get('interactionPattern') or {}).get('category', '')
            labels['pattern_qa'] = 1.0 if pattern == 'question-answer' else 0.0
            labels['pattern_collaborative'] = 1.0 if pattern == 'collaborative' else 0.0
            labels['pattern_storytelling'] = 1.0 if pattern == 'storytelling' else 0.0
            labels['pattern_advisory'] = 1.0 if pattern == 'advisory' else 0.0
            labels['pattern_casual'] = 1.0 if pattern == 'casual-chat' else 0.0

            tone = (c.get('emotionalTone') or {}).get('category', '')
            labels['tone_playful'] = 1.0 if tone == 'playful' else 0.0
            labels['tone_neutral'] = 1.0 if tone == 'neutral' else 0.0
            labels['tone_serious'] = 1.0 if tone == 'serious' else 0.0
            labels['tone_supportive'] = 1.0 if tone == 'supportive' else 0.0

            purpose = (c.get('conversationPurpose') or {}).get('category', '')
            labels['purpose_info'] = 1.0 if purpose == 'information-seeking' else 0.0
            labels['purpose_entertainment'] = 1.0 if purpose == 'entertainment' else 0.0
            labels['purpose_relationship'] = 1.0 if purpose == 'relationship-building' else 0.0
            labels['purpose_self_expression'] = 1.0 if purpose == 'self-expression' else 0.0

            labels['dominant_human_role'] = max(hr, key=hr.get) if hr else 'unknown'
            labels['dominant_ai_role'] = max(ar, key=ar.get) if ar else 'unknown'

            label_data[conv_id] = labels
        except Exception:
            pass

    common_ids = sorted(set(evidence_data.keys()) & set(label_data.keys()))
    print(f"  Common conversations: {len(common_ids)}")

    evidence_matrix = np.array([
        [float(evidence_data[cid].get(col, 0)) for col in EVIDENCE_COLS]
        for cid in common_ids
    ])

    label_matrix = np.array([
        [float(label_data[cid].get(col, 0)) for col in LABEL_FEATURES]
        for cid in common_ids
    ])

    dominant_human = [label_data[cid]['dominant_human_role'] for cid in common_ids]
    dominant_ai = [label_data[cid]['dominant_ai_role'] for cid in common_ids]

    return common_ids, evidence_matrix, label_matrix, dominant_human, dominant_ai


def test_a_predict_labels_from_evidence(evidence_matrix, dominant_human, dominant_ai):
    """Can we predict classification labels from evidence features?"""
    print(f"\n{'=' * 60}")
    print("TEST A: Predict labels from evidence features")
    print(f"{'=' * 60}")

    scaler = StandardScaler()
    X = scaler.fit_transform(evidence_matrix)
    results = {}

    for label_name, labels in [('Human Role', dominant_human), ('AI Role', dominant_ai)]:
        le = LabelEncoder()
        y = le.fit_transform(labels)
        class_counts = Counter(y)

        valid_classes = [c for c, count in class_counts.items() if count >= 5]
        mask = np.isin(y, valid_classes)
        X_filtered = X[mask]
        y_filtered = y[mask]

        n_valid_classes = len(set(y_filtered))
        if n_valid_classes < 2:
            print(f"\n  {label_name}: Too few classes for CV")
            continue

        chance = 1.0 / n_valid_classes
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        n_folds = min(5, min(Counter(y_filtered).values()))
        if n_folds < 2:
            continue

        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores = cross_val_score(rf, X_filtered, y_filtered, cv=cv, scoring='accuracy')
        mean_acc = scores.mean()
        std_acc = scores.std()

        status = "PASS" if mean_acc < 0.60 else "WARNING" if mean_acc < 0.80 else "FAIL (LEAKAGE)"
        results[label_name] = {
            'accuracy': mean_acc, 'std': std_acc, 'chance': chance,
            'n_classes': n_valid_classes, 'status': status,
        }

        print(f"\n  {label_name} ({n_valid_classes} classes, chance={chance:.1%}):")
        print(f"    Accuracy: {mean_acc:.1%} +/- {std_acc:.1%}")
        print(f"    Status: {status}")

    return results


def test_b_predict_evidence_from_labels(label_matrix, evidence_matrix):
    """Can we predict evidence features from label features?"""
    print(f"\n{'=' * 60}")
    print("TEST B: Predict evidence from labels")
    print(f"{'=' * 60}")

    X = StandardScaler().fit_transform(label_matrix)
    results = {}

    for i, col_name in enumerate(EVIDENCE_COLS):
        y = evidence_matrix[:, i]
        if np.std(y) < 1e-10:
            continue
        rf = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
        scores = cross_val_score(rf, X, y, cv=5, scoring='r2')
        r2 = max(0, scores.mean())
        status = "PASS" if r2 < 0.30 else "CAUTION" if r2 < 0.50 else "WARNING" if r2 < 0.80 else "FAIL"
        results[col_name] = {'r2': r2, 'status': status}

    sorted_results = sorted(results.items(), key=lambda x: x[1]['r2'], reverse=True)
    print(f"\n  {'Feature':<30s} {'R2':>8s}  {'Status'}")
    print(f"  {'-'*30} {'-'*8}  {'-'*10}")
    for name, r in sorted_results[:15]:
        print(f"  {name:<30s} {r['r2']:8.3f}  {r['status']}")

    n_warning = sum(1 for _, r in results.items() if r['status'] in ('WARNING', 'FAIL'))
    n_caution = sum(1 for _, r in results.items() if r['status'] == 'CAUTION')
    print(f"\n  Summary: {n_warning} warnings, {n_caution} cautions, "
          f"{len(results) - n_warning - n_caution} pass")

    return results


def test_c_correlation_screening(evidence_matrix, label_matrix):
    """Screen for high correlations between evidence and label features."""
    print(f"\n{'=' * 60}")
    print("TEST C: Correlation screening (|r| > 0.5)")
    print(f"{'=' * 60}")

    flagged = []
    for i, ev_col in enumerate(EVIDENCE_COLS):
        for j, lab_col in enumerate(LABEL_FEATURES):
            ev = evidence_matrix[:, i]
            lab = label_matrix[:, j]
            if np.std(ev) < 1e-10 or np.std(lab) < 1e-10:
                continue
            r = np.corrcoef(ev, lab)[0, 1]
            if abs(r) > 0.5:
                flagged.append((ev_col, lab_col, r))

    flagged.sort(key=lambda x: abs(x[2]), reverse=True)

    if flagged:
        print(f"\n  Found {len(flagged)} high correlations:")
        for ev_col, lab_col, r in flagged[:20]:
            print(f"    {ev_col:30s} <-> {lab_col:25s}  r={r:+.3f}")
    else:
        print("\n  No correlations above |r| > 0.5. PASS.")

    return flagged


def run_ablation(evidence_matrix, label_matrix, k=7):
    """Ablation: evidence-only vs labels-only vs combined."""
    print(f"\n{'=' * 60}")
    print(f"ABLATION STUDY (K={k})")
    print(f"{'=' * 60}")

    subsets = {
        'Evidence-only': StandardScaler().fit_transform(evidence_matrix),
        'Labels-only': StandardScaler().fit_transform(label_matrix),
        'Combined': StandardScaler().fit_transform(np.hstack([evidence_matrix, label_matrix])),
    }

    results = {}
    for name, features in subsets.items():
        for method_name, Clusterer in [('KMeans', KMeans), ('Hierarchical', AgglomerativeClustering)]:
            if method_name == 'KMeans':
                clusterer = Clusterer(n_clusters=k, random_state=42, n_init=10)
            else:
                clusterer = Clusterer(n_clusters=k)

            labels = clusterer.fit_predict(features)
            sil = silhouette_score(features, labels)
            db = davies_bouldin_score(features, labels)
            ch = calinski_harabasz_score(features, labels)

            key = f"{name} ({method_name})"
            results[key] = {
                'silhouette': sil, 'davies_bouldin': db,
                'calinski_harabasz': ch, 'n_features': features.shape[1],
            }

            print(f"\n  {key} ({features.shape[1]} features):")
            print(f"    Silhouette:        {sil:.4f}")
            print(f"    Davies-Bouldin:    {db:.4f} (lower=better)")
            print(f"    Calinski-Harabasz: {ch:.1f} (higher=better)")

    return results


def evidence_feature_importance(evidence_matrix, k=7):
    """Run RF feature importance on evidence-only clustering."""
    print(f"\n{'=' * 60}")
    print("EVIDENCE-ONLY FEATURE IMPORTANCE (5-fold CV)")
    print(f"{'=' * 60}")

    scaled = StandardScaler().fit_transform(evidence_matrix)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_importances = []
    fold_accuracies = []

    for train_idx, test_idx in skf.split(scaled, cluster_labels):
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(scaled[train_idx], cluster_labels[train_idx])
        fold_importances.append(rf.feature_importances_)
        fold_accuracies.append(rf.score(scaled[test_idx], cluster_labels[test_idx]))

    importances = np.array(fold_importances)
    mean_imp = importances.mean(axis=0)
    std_imp = importances.std(axis=0)

    print(f"\n  RF accuracy: {np.mean(fold_accuracies):.1%} +/- {np.std(fold_accuracies):.1%}")
    print(f"\n  {'Feature':<30s} {'Importance':>12s} {'Std':>8s}")
    print(f"  {'-'*30} {'-'*12} {'-'*8}")

    sorted_idx = np.argsort(mean_imp)[::-1]
    for idx in sorted_idx:
        print(f"  {EVIDENCE_COLS[idx]:<30s} {mean_imp[idx]:12.4f} {std_imp[idx]:8.4f}")

    categories = {
        'Divergence (Ch.A)': ['div_mean', 'div_variance', 'div_trend', 'div_max_spike', 'div_range'],
        'Expressiveness (Ch.B)': ['expr_mean', 'expr_variance', 'expr_trend', 'expr_range', 'expr_shift'],
        'Dynamics (Ch.C)': ['repair_rate', 'constraint_pressure', 'hedge_assert_ratio',
                            'ai_refusal_rate', 'goal_drift_mean', 'goal_drift_variance',
                            'goal_stability', 'length_ratio'],
        'Affect Proxy': ['affect_mean', 'affect_variance', 'affect_trend', 'affect_range',
                         'affect_max', 'affect_min', 'affect_peak_count', 'affect_valley_count',
                         'valence_mean', 'valence_variance', 'valence_trend'],
        'Structure': ['n_messages_log'],
    }

    print(f"\n  Category breakdown:")
    for cat_name, cat_cols in categories.items():
        cat_imp = sum(mean_imp[EVIDENCE_COLS.index(c)] for c in cat_cols if c in EVIDENCE_COLS)
        print(f"    {cat_name:<25s} {cat_imp:6.1%}")

    return mean_imp, std_imp, cluster_labels


def main():
    print("=" * 60)
    print("ACCEPTANCE TESTS + EVALUATION (v2 Unified)")
    print("=" * 60)

    print("\n  Loading data...")
    common_ids, evidence_matrix, label_matrix, dominant_human, dominant_ai = load_data()

    evidence_matrix = np.nan_to_num(evidence_matrix, nan=0.0, posinf=10.0, neginf=-10.0)
    label_matrix = np.nan_to_num(label_matrix, nan=0.0, posinf=1.0, neginf=0.0)

    test_a_results = test_a_predict_labels_from_evidence(evidence_matrix, dominant_human, dominant_ai)
    test_b_results = test_b_predict_evidence_from_labels(label_matrix, evidence_matrix)
    test_c_flagged = test_c_correlation_screening(evidence_matrix, label_matrix)

    ablation_results = run_ablation(evidence_matrix, label_matrix, k=7)
    mean_imp, std_imp, cluster_labels = evidence_feature_importance(evidence_matrix, k=7)

    # Write report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / 'acceptance_report.md'
    with open(report_path, 'w') as f:
        f.write("# Acceptance Test Report (v2 Unified)\n\n")
        f.write(f"**Corpus:** {len(common_ids)} conversations (canonical, deduped, English)\n\n")

        f.write("## Test A: Label prediction from evidence\n\n")
        f.write("| Target | Accuracy | Chance | Status |\n|---|---|---|---|\n")
        for name, r in test_a_results.items():
            f.write(f"| {name} | {r['accuracy']:.1%} +/- {r['std']:.1%} | {r['chance']:.1%} | {r['status']} |\n")

        f.write("\n## Test B: Evidence prediction from labels (top 10)\n\n")
        f.write("| Feature | R2 | Status |\n|---|---|---|\n")
        sorted_b = sorted(test_b_results.items(), key=lambda x: x[1]['r2'], reverse=True)
        for name, r in sorted_b[:10]:
            f.write(f"| {name} | {r['r2']:.3f} | {r['status']} |\n")

        f.write(f"\n## Test C: Correlation screening\n\n")
        f.write(f"Flagged {len(test_c_flagged)} pairs with |r| > 0.5\n\n")
        if test_c_flagged:
            f.write("| Evidence | Label | r |\n|---|---|---|\n")
            for ev, lab, r in test_c_flagged[:10]:
                f.write(f"| {ev} | {lab} | {r:+.3f} |\n")

        f.write(f"\n## Ablation Results\n\n")
        f.write("| Feature Set | Silhouette | DB | CH |\n|---|---|---|---|\n")
        for name, r in ablation_results.items():
            f.write(f"| {name} | {r['silhouette']:.4f} | {r['davies_bouldin']:.4f} | {r['calinski_harabasz']:.1f} |\n")

        f.write(f"\n*Generated by run_acceptance_tests.py*\n")

    # Also save structured JSON for programmatic consumption
    json_path = OUTPUT_DIR / 'acceptance_results.json'
    json_data = {
        'n_conversations': len(common_ids),
        'test_a': {name: {'accuracy': float(r['accuracy']), 'std': float(r['std']),
                          'chance': float(r['chance']), 'n_classes': r['n_classes'],
                          'status': r['status']}
                   for name, r in test_a_results.items()},
        'test_b': {name: {'r2': float(r['r2']), 'status': r['status']}
                   for name, r in test_b_results.items()},
        'test_c_flagged_count': len(test_c_flagged),
        'test_c_flagged': [{'evidence': ev, 'label': lab, 'r': float(r)}
                           for ev, lab, r in test_c_flagged[:20]],
        'ablation': {name: {'silhouette': float(r['silhouette']),
                            'davies_bouldin': float(r['davies_bouldin']),
                            'calinski_harabasz': float(r['calinski_harabasz']),
                            'n_features': int(r['n_features'])}
                     for name, r in ablation_results.items()},
        'evidence_feature_importance': {
            EVIDENCE_COLS[i]: float(mean_imp[i]) for i in range(len(EVIDENCE_COLS))
        },
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"\n\nReport written to {report_path}")
    print(f"JSON data written to {json_path}")


if __name__ == '__main__':
    main()
