#!/usr/bin/env python3
"""
STEP 5: Post-hoc Archetype Naming

Names archetypes AFTER clustering based on cluster signatures.
Calculates collapse rate per cluster.
Generates paper-ready tables and descriptions.

This is the final analysis step before writing.
"""

import json
import argparse
import pandas as pd
from pathlib import Path
from collections import Counter


# Archetype naming rules based on cluster signatures
# These are applied POST-HOC, not predefined
ARCHETYPE_RULES = {
    'repair_failure': {
        'condition': lambda row: row.get('mean_repair_count', 0) >= 5,
        'label': 'Repair Failure',
        'description': 'High frequency of user correction attempts, indicating persistent misalignment between user intent and AI behavior.'
    },
    'passive_acceptance': {
        'condition': lambda row: row.get('mean_passive_rate', 0) >= 0.3,
        'label': 'Passive Acceptance', 
        'description': 'Users frequently accept AI outputs without modification, potentially indicating reduced agency or satisficing.'
    },
    'stance_escalation': {
        'condition': lambda row: row.get('mean_stance_delta', 0) >= 0.5,
        'label': 'Stance Escalation',
        'description': 'Users shift from directive to passive/frustrated stance over the conversation.'
    },
    'healthy_interaction': {
        'condition': lambda row: row.get('mean_specificity_delta', 0) >= 0 and row.get('mean_repair_count', 0) < 3,
        'label': 'Healthy Interaction',
        'description': 'Maintained or increased specificity with minimal repair attempts, indicating successful collaboration.'
    },
}


def load_clustered_data(clustered_path: Path, collapse_path: Path) -> pd.DataFrame:
    """Load clustered data and merge with collapse labels."""
    with open(clustered_path, 'r') as f:
        clustered = json.load(f)
    
    with open(collapse_path, 'r') as f:
        collapse = json.load(f)
    
    # Create lookup for collapse data
    collapse_lookup = {c['conversation_id']: c for c in collapse}
    
    # Merge
    for item in clustered:
        conv_id = item.get('conversation_id')
        if conv_id in collapse_lookup:
            item['collapse'] = collapse_lookup[conv_id].get('collapse', False)
            item['collapse_conditions'] = collapse_lookup[conv_id].get('collapse_conditions', [])
            item['collapse_confidence'] = collapse_lookup[conv_id].get('collapse_confidence', 0)
    
    return pd.DataFrame(clustered)


def load_cluster_stats(stats_path: Path) -> pd.DataFrame:
    """Load cluster statistics CSV."""
    return pd.read_csv(stats_path)


def assign_archetype(row: pd.Series) -> tuple[str, str]:
    """Assign archetype label based on cluster signature."""
    for rule_name, rule in ARCHETYPE_RULES.items():
        if rule['condition'](row):
            return rule['label'], rule['description']
    return 'Mixed/Other', 'No dominant pattern identified; may represent heterogeneous interaction styles.'


def calculate_collapse_per_cluster(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate collapse rate per cluster."""
    results = []
    
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == cluster_id]
        n_collapse = cluster_df['collapse'].sum() if 'collapse' in cluster_df.columns else 0
        n_total = len(cluster_df)
        
        # Count condition types
        condition_counts = Counter()
        if 'collapse_conditions' in cluster_df.columns:
            for conditions in cluster_df['collapse_conditions']:
                if isinstance(conditions, list):
                    for c in conditions:
                        condition_counts[c] += 1
        
        results.append({
            'cluster': cluster_id,
            'n': n_total,
            'n_collapse': n_collapse,
            'collapse_rate': n_collapse / n_total * 100 if n_total > 0 else 0,
            'repair_failure_n': condition_counts.get('repair_failure', 0),
            'tone_degradation_n': condition_counts.get('tone_degradation', 0),
            'specificity_collapse_n': condition_counts.get('specificity_collapse', 0),
        })
    
    return pd.DataFrame(results)


def generate_paper_tables(
    cluster_stats: pd.DataFrame,
    collapse_stats: pd.DataFrame,
    archetypes: dict
) -> str:
    """Generate markdown tables for paper."""
    
    md = "# Classification Results\n\n"
    md += "## Table 1: Cluster Characteristics\n\n"
    md += "| Cluster | Archetype | N | % | Repair | Spec Δ | Stance Δ | Passive |\n"
    md += "|---------|-----------|---|---|--------|--------|----------|--------|\n"
    
    for _, row in cluster_stats.iterrows():
        cluster_id = int(row['cluster'])
        archetype = archetypes.get(cluster_id, ('Unknown', ''))[0]
        md += f"| {cluster_id} | {archetype} | {int(row['n'])} | {row['pct']:.1f}% | "
        md += f"{row.get('mean_repair_count', 0):.1f} | "
        md += f"{row.get('mean_specificity_delta', 0):.2f} | "
        md += f"{row.get('mean_stance_delta', 0):.2f} | "
        md += f"{row.get('mean_passive_rate', 0):.2f} |\n"
    
    md += "\n## Table 2: Agency Collapse by Cluster\n\n"
    md += "| Cluster | Archetype | N | Collapse | Rate | Repair Fail | Tone Deg | Spec Collapse |\n"
    md += "|---------|-----------|---|----------|------|-------------|----------|---------------|\n"
    
    for _, row in collapse_stats.iterrows():
        cluster_id = int(row['cluster'])
        archetype = archetypes.get(cluster_id, ('Unknown', ''))[0]
        md += f"| {cluster_id} | {archetype} | {int(row['n'])} | "
        md += f"{int(row['n_collapse'])} | {row['collapse_rate']:.1f}% | "
        md += f"{int(row['repair_failure_n'])} | {int(row['tone_degradation_n'])} | "
        md += f"{int(row['specificity_collapse_n'])} |\n"
    
    md += "\n## Archetype Descriptions\n\n"
    for cluster_id, (label, description) in sorted(archetypes.items()):
        md += f"### Cluster {cluster_id}: {label}\n\n"
        md += f"{description}\n\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description="Name archetypes and analyze collapse per cluster")
    parser.add_argument("--clustered", "-c", required=True, help="Clustered data JSON")
    parser.add_argument("--collapse", "-l", required=True, help="Collapse-labeled data JSON")
    parser.add_argument("--stats", "-s", required=True, help="Cluster stats CSV")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    args = parser.parse_args()
    
    print("Loading data...")
    df = load_clustered_data(Path(args.clustered), Path(args.collapse))
    cluster_stats = load_cluster_stats(Path(args.stats))
    
    print(f"Loaded {len(df)} conversations across {df['cluster'].nunique()} clusters")
    
    # Assign archetypes
    print("\nAssigning archetypes based on cluster signatures...")
    archetypes = {}
    for _, row in cluster_stats.iterrows():
        cluster_id = int(row['cluster'])
        label, description = assign_archetype(row)
        archetypes[cluster_id] = (label, description)
        print(f"  Cluster {cluster_id}: {label}")
    
    # Calculate collapse per cluster
    print("\nCalculating collapse rates per cluster...")
    collapse_stats = calculate_collapse_per_cluster(df)
    
    print("\nCollapse by Cluster:")
    print(collapse_stats.to_string(index=False))
    
    # Generate paper tables
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    paper_md = generate_paper_tables(cluster_stats, collapse_stats, archetypes)
    
    with open(output_dir / "paper_tables.md", 'w') as f:
        f.write(paper_md)
    
    # Save archetype assignments
    archetype_data = [
        {'cluster': k, 'archetype': v[0], 'description': v[1]}
        for k, v in archetypes.items()
    ]
    with open(output_dir / "archetypes.json", 'w') as f:
        json.dump(archetype_data, f, indent=2)
    
    # Save collapse stats
    collapse_stats.to_csv(output_dir / "collapse_per_cluster.csv", index=False)
    
    print(f"\n💾 Saved to {output_dir}")
    print(f"  - paper_tables.md")
    print(f"  - archetypes.json")
    print(f"  - collapse_per_cluster.csv")
    
    print("\n✅ Archetype analysis complete")


if __name__ == "__main__":
    main()
