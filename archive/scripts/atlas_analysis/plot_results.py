#!/usr/bin/env python3
"""
Generate Paper Visualizations

Produces high-quality figures for the CUI 2026 paper:
1. Bar Chart: Agency Collapse Rate by Archetype (with CI)
2. Radar Chart: Feature Signatures of Archetypes

Usage: python scripts/plot_results.py
"""

import json
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
from pathlib import Path
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-paper')
sns.set_context("paper", font_scale=1.5)
sns.set_style("ticks")

COLORS = {
    'Repair Failure (Severe)': '#d62728',   # Red
    'Repair Failure (Moderate)': '#ff7f0e', # Orange
    'Passive Acceptance': '#9467bd',        # Purple
    'Mixed/Healthy': '#2ca02c',             # Green
    'Outlier': '#7f7f7f'                    # Gray
}

def load_data(analysis_dir: Path):
    """Load analysis data."""
    # Load archetypes
    with open(analysis_dir / "archetypes.json", 'r') as f:
        archetypes = json.load(f)
    archetype_map = {item['cluster']: item['archetype'] for item in archetypes}
    
    # Load collapse stats
    collapse_df = pd.read_csv(analysis_dir / "collapse_per_cluster.csv")
    collapse_df['Archetype'] = collapse_df['cluster'].map(archetype_map)
    
    # Load cluster stats (features)
    # We need the source file for Z-scores
    cluster_stats_df = pd.read_csv(analysis_dir.parent / "clustered_llm_all" / "cluster_stats_kmeans.csv")
    cluster_stats_df['Archetype'] = cluster_stats_df['cluster'].map(archetype_map)
    
    return collapse_df, cluster_stats_df


def plot_collapse_rates(df: pd.DataFrame, output_path: Path):
    """Generate Bar Chart of Collapse Rates."""
    # Filter out outliers if N is very small
    df = df[df['n'] > 10].sort_values('collapse_rate', ascending=False)
    
    plt.figure(figsize=(10, 6))
    
    # Calculate Standard Error for Error Bars (Wald interval approximation)
    # SE = sqrt( p(1-p) / n )
    p = df['collapse_rate'] / 100
    n = df['n']
    df['se'] = np.sqrt(p * (1 - p) / n) * 100
    
    # Create distinct colors
    colors = [COLORS.get(label, '#333333') for label in df['Archetype']]
    
    bars = plt.bar(
        df['Archetype'], 
        df['collapse_rate'], 
        yerr=df['se']*1.96, # 95% CI
        capsize=5, 
        color=colors,
        alpha=0.9,
        edgecolor='black',
        width=0.6
    )
    
    plt.ylabel('Agency Collapse Rate (%)')
    plt.title('Agency Collapse Rate by Archetype', pad=15, fontsize=16, fontweight='bold')
    plt.ylim(0, 105)
    
    # Add labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2., 
            height + 3,
            f'{height:.1f}%',
            ha='center', va='bottom', fontweight='bold'
        )
    
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    sns.despine()
    
    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved {output_path}")
    plt.close()


def plot_radar_signatures(df: pd.DataFrame, output_path: Path):
    """Generate Radar Chart of Feature Signatures (Z-scores)."""
    # Features to plot (Z-scores)
    features = [
        'z_repair_count', 
        'z_specificity_delta', 
        'z_stance_delta', 
        'z_passive_rate'
    ]
    
    # Pretty labels
    labels = [
        'Repair\nAttempt', 
        'Specificity\nGain', 
        'Stance\nEscalation', 
        'Passivity'
    ]
    
    # Filter and setup
    df = df[df['n'] > 10]  # Filter small clusters
    
    # Number of variables
    N = len(features)
    
    # What will be the angle of each axis
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Initialize plot
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)
    
    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], labels, size=12)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([-1, 0, 1, 2, 3, 4, 5, 6, 7], ["-1", "0", "1", "2", "3", "4", "5", "6", "7"], color="grey", size=10)
    plt.ylim(-1.5, 7.5)  # Adapted for high repair Z-scores
    
    # Plot each archetype
    for _, row in df.iterrows():
        label = row['Archetype']
        color = COLORS.get(label, '#333333')
        
        values = row[features].values.flatten().tolist()
        values += values[:1]
        
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=label, color=color)
        ax.fill(angles, values, color=color, alpha=0.1)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title('Archetype Feature Signatures (Z-scores)', size=16, fontweight='bold', y=1.1)
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate paper figures")
    parser.add_argument("--analysis_dir", "-d", default="data/analysis_all", help="Analysis output directory")
    args = parser.parse_args()
    
    base_path = Path.cwd() / args.analysis_dir
    print(f"Loading data from {base_path}")
    
    if not base_path.exists():
        print(f"Error: Directory {base_path} not found")
        return

    collapse_df, cluster_stats_df = load_data(base_path)
    
    output_dir = base_path / "figures"
    output_dir.mkdir(exist_ok=True)
    
    print("Generating Bar Chart...")
    plot_collapse_rates(collapse_df, output_dir / "fig_collapse_rates.png")
    
    print("Generating Radar Chart...")
    plot_radar_signatures(cluster_stats_df, output_dir / "fig_radar_signatures.png")
    
    print("✅ Figures generated successfully")


if __name__ == "__main__":
    main()
