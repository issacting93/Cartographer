#!/usr/bin/env python3
"""
STEP 2-3: Clustering + Characterization

Clusters conversations using features only.
No archetypes assumed — labels come from Step 5.

Methods:
- HDBSCAN (primary): finds structure + noise
- k-means (secondary): robustness check
"""

import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

try:
    from hdbscan import HDBSCAN
    HAS_HDBSCAN = True
except ImportError:
    HAS_HDBSCAN = False
    print("Warning: hdbscan not installed, using only k-means")


# Features to use for clustering (numeric only)
# These are checked dynamically based on what's in the data
CLUSTER_FEATURES_REGEX = [
    'repair_count',
    'repair_success_rate',
    'constraint_count',
    'politeness_delta',
    'frustration_score',
    'passive_rate',
    'specificity_delta',
    'verbatim_repeats',
    'mean_user_length',
]

CLUSTER_FEATURES_LLM = [
    'repair_count',
    'specificity_delta',
    'stance_delta',
    'politeness_delta',
    'passive_rate',
    'constraint_count',
    'verbatim_repeats',
    'mean_user_length',
]

def get_cluster_features(df: pd.DataFrame) -> list:
    """Determine which feature set to use based on available columns."""
    if 'stance_delta' in df.columns:
        # LLM-enhanced features
        return [f for f in CLUSTER_FEATURES_LLM if f in df.columns]
    else:
        # Regex features
        return [f for f in CLUSTER_FEATURES_REGEX if f in df.columns]


def load_features(filepath: Path) -> pd.DataFrame:
    """Load features from JSON."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def prepare_feature_matrix(df: pd.DataFrame) -> tuple[np.ndarray, StandardScaler, list]:
    """Prepare and scale feature matrix."""
    features = get_cluster_features(df)
    print(f"Using features: {features}")
    X = df[features].values
    
    # Handle any NaN
    X = np.nan_to_num(X, nan=0.0)
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, scaler, features


def cluster_hdbscan(X: np.ndarray, min_cluster_size: int = 10, min_samples: int = 5) -> np.ndarray:
    """Cluster using HDBSCAN."""
    if not HAS_HDBSCAN:
        raise ImportError("hdbscan not installed")
    
    clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    labels = clusterer.fit_predict(X)
    return labels


def cluster_kmeans(X: np.ndarray, k: int = 5) -> np.ndarray:
    """Cluster using k-means."""
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    return labels


def find_optimal_k(X: np.ndarray, k_range: range = range(3, 10)) -> int:
    """Find optimal k using silhouette score."""
    best_k = 3
    best_score = -1
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        score = silhouette_score(X, labels)
        print(f"  k={k}: silhouette={score:.3f}")
        
        if score > best_score:
            best_score = score
            best_k = k
    
    return best_k


def characterize_clusters(df: pd.DataFrame, labels: np.ndarray, features: list) -> pd.DataFrame:
    """Compute cluster statistics."""
    df = df.copy()
    df['cluster'] = labels
    
    # Aggregate statistics per cluster
    stats = []
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == cluster_id]
        
        row = {
            'cluster': cluster_id,
            'n': len(cluster_df),
            'pct': len(cluster_df) / len(df) * 100,
        }
        
        # Mean for each feature
        for feat in features:
            if feat in cluster_df.columns:
                row[f'mean_{feat}'] = cluster_df[feat].mean()
        
        stats.append(row)
    
    stats_df = pd.DataFrame(stats)
    
    # Add z-scores relative to population
    for feat in features:
        if feat in df.columns:
            pop_mean = df[feat].mean()
            pop_std = df[feat].std()
            if pop_std > 0:
                stats_df[f'z_{feat}'] = (stats_df[f'mean_{feat}'] - pop_mean) / pop_std
            else:
                stats_df[f'z_{feat}'] = 0
    
    return stats_df


def main():
    parser = argparse.ArgumentParser(description="Cluster conversations by features")
    parser.add_argument("--input", "-i", required=True, help="Input features JSON")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--method", "-m", default="hdbscan", choices=["hdbscan", "kmeans", "both"])
    parser.add_argument("--k", type=int, default=None, help="Number of clusters for k-means")
    parser.add_argument("--min-cluster-size", type=int, default=10, help="HDBSCAN min cluster size")
    args = parser.parse_args()
    
    # Load features
    print(f"Loading features from {args.input}")
    df = load_features(Path(args.input))
    print(f"Loaded {len(df)} conversations")
    
    # Prepare matrix
    X_scaled, scaler, features_used = prepare_feature_matrix(df)
    print(f"Feature matrix: {X_scaled.shape}")
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ===== HDBSCAN =====
    if args.method in ["hdbscan", "both"] and HAS_HDBSCAN:
        print("\n--- HDBSCAN Clustering ---")
        hdb_labels = cluster_hdbscan(X_scaled, min_cluster_size=args.min_cluster_size)
        
        n_clusters = len(set(hdb_labels)) - (1 if -1 in hdb_labels else 0)
        n_noise = (hdb_labels == -1).sum()
        print(f"Found {n_clusters} clusters + {n_noise} noise points")
        
        # Silhouette (excluding noise)
        mask = hdb_labels != -1
        if mask.sum() > 1 and len(set(hdb_labels[mask])) > 1:
            sil = silhouette_score(X_scaled[mask], hdb_labels[mask])
            print(f"Silhouette score (excl. noise): {sil:.3f}")
        
        # Characterize
        hdb_stats = characterize_clusters(df, hdb_labels, features_used)
        print("\nCluster Summary (HDBSCAN):")
        display_cols = ['cluster', 'n', 'pct'] + [f'mean_{f}' for f in features_used if f'mean_{f}' in hdb_stats.columns]
        print(hdb_stats[display_cols[:8]].to_string())
        
        # Save
        df_hdb = df.copy()
        df_hdb['cluster'] = hdb_labels
        df_hdb.to_json(output_dir / "clustered_hdbscan.json", orient='records', indent=2)
        hdb_stats.to_csv(output_dir / "cluster_stats_hdbscan.csv", index=False)
        print(f"\n💾 Saved HDBSCAN results to {output_dir}")
    
    # ===== K-MEANS =====
    if args.method in ["kmeans", "both"]:
        print("\n--- K-Means Clustering ---")
        
        if args.k is None:
            print("Finding optimal k...")
            args.k = find_optimal_k(X_scaled)
            print(f"Optimal k = {args.k}")
        
        km_labels = cluster_kmeans(X_scaled, k=args.k)
        
        sil = silhouette_score(X_scaled, km_labels)
        print(f"Silhouette score: {sil:.3f}")
        
        # Characterize
        km_stats = characterize_clusters(df, km_labels, features_used)
        print("\nCluster Summary (K-Means):")
        display_cols = ['cluster', 'n', 'pct'] + [f'mean_{f}' for f in features_used if f'mean_{f}' in km_stats.columns]
        print(km_stats[display_cols[:8]].to_string())
        
        # Save
        df_km = df.copy()
        df_km['cluster'] = km_labels
        df_km.to_json(output_dir / "clustered_kmeans.json", orient='records', indent=2)
        km_stats.to_csv(output_dir / "cluster_stats_kmeans.csv", index=False)
        print(f"\n💾 Saved K-Means results to {output_dir}")
    
    print("\n✅ Clustering complete")
    print("Next: Run collapse.py to define Agency Collapse outcome variable")


if __name__ == "__main__":
    main()
