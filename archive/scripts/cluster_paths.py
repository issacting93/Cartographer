#!/usr/bin/env python3
"""
Path Clustering (v2)
=====================
Clusters conversations using evidence-only features to avoid v1 circularity.
Uses k-means/hierarchical clustering with silhouette optimization.

CRITICAL: Clusters on EVIDENCE-ONLY features (not role-derived) to avoid
the v1 Spatial-Role Circularity blocker (R^2=1.0).

Also removes length-confounded features (n_messages_log, affect_peak_count,
affect_valley_count) which dominate clustering with a trivial short/long split.

Usage:
  python3 scripts/cluster_paths.py [--k N]
"""

import json
import os
import sys
import argparse
import statistics
import numpy as np
import csv
from pathlib import Path
from collections import defaultdict, Counter

from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
EVIDENCE_CSV = PROJECT_ROOT / "data" / "v2_unified" / "evidence_features.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "reports"

# All evidence columns
ALL_EVIDENCE_COLS = [
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

# Length-confounded features to exclude from clustering
# n_messages_log: conversation length directly
# affect_peak_count, affect_valley_count: count features that scale with length
# affect_max, affect_min, affect_range: extreme-value features biased by length
LENGTH_CONFOUNDED = {
    'n_messages_log', 'affect_peak_count', 'affect_valley_count',
    'affect_range', 'affect_max', 'affect_min',
}

# Clean evidence columns (no length confounds, no role-derived)
EVIDENCE_COLS = [c for c in ALL_EVIDENCE_COLS if c not in LENGTH_CONFOUNDED]


def load_evidence_features():
    """Load evidence features from CSV."""
    data = {}
    with open(EVIDENCE_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row['conv_id']] = row
    return data


def find_optimal_k(X_scaled, max_k=10):
    """Find optimal K using silhouette score."""
    scores = {}
    for k in range(2, min(max_k + 1, len(X_scaled))):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        if len(set(labels)) > 1:
            scores[k] = silhouette_score(X_scaled, labels)
    return scores


def gap_statistic(X_scaled, max_k=10, n_ref=20):
    """Compute gap statistic to test for meaningful cluster structure."""
    gaps = []
    s_k = []
    for k in range(1, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        W_k = km.inertia_

        ref_W = []
        rng = np.random.RandomState(42)
        for _ in range(n_ref):
            X_ref = rng.uniform(X_scaled.min(axis=0), X_scaled.max(axis=0), size=X_scaled.shape)
            km_ref = KMeans(n_clusters=k, random_state=42, n_init=5)
            km_ref.fit(X_ref)
            ref_W.append(np.log(km_ref.inertia_))

        gap = np.mean(ref_W) - np.log(W_k)
        sdk = np.std(ref_W) * np.sqrt(1 + 1/n_ref)
        gaps.append(gap)
        s_k.append(sdk)

    # First K where gap(k) >= gap(k+1) - s(k+1)
    optimal_k = max_k
    for k in range(len(gaps) - 1):
        if gaps[k] >= gaps[k + 1] - s_k[k + 1]:
            optimal_k = k + 1
            break

    return optimal_k, gaps, s_k


def run_clustering(evidence_data, k=None):
    """Run clustering on evidence-only features."""
    conv_ids = sorted(evidence_data.keys())
    X = np.array([
        [float(evidence_data[cid].get(col, 0)) for col in EVIDENCE_COLS]
        for cid in conv_ids
    ])
    X = np.nan_to_num(X, nan=0.0, posinf=10.0, neginf=-10.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"  Feature matrix: {X_scaled.shape[0]} conversations x {X_scaled.shape[1]} features")
    print(f"  Excluded {len(LENGTH_CONFOUNDED)} length-confounded features: {sorted(LENGTH_CONFOUNDED)}")

    # Gap statistic to test for structure
    print("\n  Computing gap statistic...")
    gap_k, gaps, gap_s = gap_statistic(X_scaled)
    print(f"  Gap statistic optimal K: {gap_k}")
    for i, (g, s) in enumerate(zip(gaps, gap_s)):
        print(f"    K={i+1}: gap={g:.4f}, s_k={s:.4f}")

    # Find optimal K via silhouette if not specified
    if k is None:
        print("\n  Finding optimal K via silhouette...")
        scores = find_optimal_k(X_scaled)
        k = max(scores, key=scores.get) if scores else 4
        print(f"  Silhouette scores: {scores}")
        print(f"  Silhouette-optimal K: {k}")

        if gap_k == 1:
            print(f"\n  WARNING: Gap statistic suggests K=1 (no meaningful cluster structure).")
            print(f"  Using silhouette-optimal K={k} for exploratory analysis,")
            print(f"  but findings should be interpreted as descriptive, not as")
            print(f"  evidence of discrete conversation types.")

    results = {
        'gap_statistic': {
            'optimal_k': gap_k,
            'gaps': [float(g) for g in gaps],
            's_k': [float(s) for s in gap_s],
        }
    }

    for method in ['kmeans', 'hierarchical']:
        print(f"\n  Clustering with {method} (K={k})...")

        if method == 'kmeans':
            clusterer = KMeans(n_clusters=k, random_state=42, n_init=10)
        else:
            clusterer = AgglomerativeClustering(n_clusters=k)

        labels = clusterer.fit_predict(X_scaled)

        sil = silhouette_score(X_scaled, labels)
        db = davies_bouldin_score(X_scaled, labels)
        ch = calinski_harabasz_score(X_scaled, labels)

        print(f"    Silhouette:        {sil:.4f}")
        print(f"    Davies-Bouldin:    {db:.4f} (lower=better)")
        print(f"    Calinski-Harabasz: {ch:.1f} (higher=better)")

        # Cluster sizes
        cluster_sizes = Counter(labels)
        for c_id in sorted(cluster_sizes.keys()):
            pct = cluster_sizes[c_id] / len(labels) * 100
            print(f"    Cluster {c_id}: {cluster_sizes[c_id]} ({pct:.1f}%)")

        # Feature importance via RF
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        fold_importances = []
        fold_accuracies = []

        for train_idx, test_idx in skf.split(X_scaled, labels):
            rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            rf.fit(X_scaled[train_idx], labels[train_idx])
            fold_importances.append(rf.feature_importances_)
            fold_accuracies.append(rf.score(X_scaled[test_idx], labels[test_idx]))

        importances = np.array(fold_importances)
        mean_imp = importances.mean(axis=0)
        std_imp = importances.std(axis=0)

        print(f"\n    RF accuracy: {np.mean(fold_accuracies):.1%} +/- {np.std(fold_accuracies):.1%}")
        print(f"    Top 10 features:")
        sorted_idx = np.argsort(mean_imp)[::-1]
        for idx in sorted_idx[:10]:
            print(f"      {EVIDENCE_COLS[idx]:30s} {mean_imp[idx]:.4f} +/- {std_imp[idx]:.4f}")

        # Permutation baseline
        rng = np.random.RandomState(42)
        perm_scores = []
        for _ in range(100):
            shuffled = rng.permutation(labels)
            perm_scores.append(silhouette_score(X_scaled, shuffled))
        perm_mean = np.mean(perm_scores)
        z_score = (sil - perm_mean) / np.std(perm_scores) if np.std(perm_scores) > 0 else float('inf')
        p_value = np.mean([s >= sil for s in perm_scores])

        print(f"\n    Permutation test (100 permutations):")
        print(f"      Real silhouette: {sil:.4f}")
        print(f"      Permuted mean:   {perm_mean:.4f} +/- {np.std(perm_scores):.4f}")
        print(f"      Z-score:         {z_score:.2f}")
        print(f"      p-value:         {p_value:.4f}")

        results[method] = {
            'labels': labels,
            'conv_ids': conv_ids,
            'silhouette': sil,
            'davies_bouldin': db,
            'calinski_harabasz': ch,
            'k': k,
            'feature_importance': {EVIDENCE_COLS[i]: float(mean_imp[i]) for i in sorted_idx},
            'permutation_z': z_score,
            'permutation_p': p_value,
        }

    return results


def main():
    parser = argparse.ArgumentParser(description="Evidence-only path clustering")
    parser.add_argument('--k', type=int, help="Number of clusters (auto if not specified)")
    args = parser.parse_args()

    print("=" * 60)
    print("EVIDENCE-ONLY PATH CLUSTERING (v2)")
    print("=" * 60)

    evidence_data = load_evidence_features()
    print(f"  Loaded evidence for {len(evidence_data)} conversations")

    results = run_clustering(evidence_data, k=args.k)

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save gap statistic results
    gap_file = OUTPUT_DIR / 'gap_statistic.json'
    with open(gap_file, 'w') as f:
        json.dump(results['gap_statistic'], f, indent=2)
    print(f"\n  Saved: {gap_file}")

    for method in ['kmeans', 'hierarchical']:
        result = results[method]
        # Save cluster assignments
        cluster_assignments = {
            cid: int(label)
            for cid, label in zip(result['conv_ids'], result['labels'])
        }
        output_file = OUTPUT_DIR / f'cluster_analysis_{method}.json'
        with open(output_file, 'w') as f:
            json.dump({
                'method': method,
                'k': result['k'],
                'silhouette': result['silhouette'],
                'davies_bouldin': result['davies_bouldin'],
                'calinski_harabasz': result['calinski_harabasz'],
                'permutation_z': result['permutation_z'],
                'permutation_p': result['permutation_p'],
                'feature_importance': result['feature_importance'],
                'gap_statistic_k': results['gap_statistic']['optimal_k'],
                'length_confounded_removed': sorted(LENGTH_CONFOUNDED),
                'cluster_assignments': cluster_assignments,
            }, f, indent=2)
        print(f"\n  Saved: {output_file}")


if __name__ == '__main__':
    main()
