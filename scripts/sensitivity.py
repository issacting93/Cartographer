#!/usr/bin/env python3
"""
Sensitivity Analysis: Threshold Stability

Varies collapse thresholds ±20% to check result stability.
Outputs collapse rates across threshold variations.
"""

import json
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from collapse import has_agency_collapse, THRESHOLDS


def run_sensitivity_analysis(data: list, base_thresholds: dict, variations: list) -> dict:
    """Run collapse detection across threshold variations."""
    results = {}
    
    for variation in variations:
        # Create modified thresholds
        modified = {}
        for key, base_val in base_thresholds.items():
            if isinstance(base_val, (int, float)):
                modified[key] = base_val * variation
            else:
                modified[key] = base_val
        
        # Run collapse detection
        collapse_count = 0
        condition_counts = {'repair_failure': 0, 'tone_degradation': 0, 'specificity_collapse': 0}
        
        for features in data:
            result = has_agency_collapse(features, modified)
            if result['collapse']:
                collapse_count += 1
                for cond in result['conditions']:
                    condition_counts[cond] += 1
        
        collapse_rate = collapse_count / len(data) * 100
        
        results[variation] = {
            'variation_pct': (variation - 1.0) * 100,
            'collapse_count': collapse_count,
            'collapse_rate': round(collapse_rate, 1),
            'repair_failure': condition_counts['repair_failure'],
            'tone_degradation': condition_counts['tone_degradation'],
            'specificity_collapse': condition_counts['specificity_collapse'],
            'thresholds': {k: round(v, 3) if isinstance(v, float) else v for k, v in modified.items()}
        }
    
    return results


def print_sensitivity_table(results: dict, n_total: int):
    """Print formatted sensitivity results."""
    print("\n" + "=" * 80)
    print("SENSITIVITY ANALYSIS: Threshold Stability")
    print("=" * 80)
    print(f"\nN = {n_total} conversations")
    print("\nVariation | Collapse Rate | Repair Fail | Tone Deg | Spec Collapse")
    print("-" * 70)
    
    for variation, data in sorted(results.items()):
        var_str = f"{data['variation_pct']:+.0f}%".rjust(6)
        print(f"  {var_str}   |    {data['collapse_rate']:5.1f}%     |    {data['repair_failure']:3d}     |   {data['tone_degradation']:3d}    |      {data['specificity_collapse']:3d}")
    
    print("-" * 70)
    
    # Stability check
    rates = [d['collapse_rate'] for d in results.values()]
    min_rate, max_rate = min(rates), max(rates)
    range_pct = max_rate - min_rate
    base_rate = results[1.0]['collapse_rate']
    
    print(f"\nBaseline collapse rate: {base_rate:.1f}%")
    print(f"Range across ±20% variation: {min_rate:.1f}% - {max_rate:.1f}% (Δ = {range_pct:.1f}pp)")
    
    if range_pct < 10:
        print("✅ STABLE: Collapse rate varies < 10 percentage points")
    elif range_pct < 20:
        print("⚠️  MODERATE: Collapse rate varies 10-20 percentage points")
    else:
        print("❌ UNSTABLE: Collapse rate varies > 20 percentage points")


def main():
    parser = argparse.ArgumentParser(description="Sensitivity analysis for collapse thresholds")
    parser.add_argument("--input", "-i", required=True, help="Input features JSON")
    parser.add_argument("--output", "-o", help="Output JSON for results (optional)")
    args = parser.parse_args()
    
    # Load data
    with open(args.input, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} conversations")
    
    # Define variations: -20%, -10%, baseline, +10%, +20%
    variations = [0.8, 0.9, 1.0, 1.1, 1.2]
    
    print(f"\nBase thresholds:")
    for key, val in THRESHOLDS.items():
        print(f"  {key}: {val}")
    
    # Run analysis
    results = run_sensitivity_analysis(data, THRESHOLDS, variations)
    
    # Print results
    print_sensitivity_table(results, len(data))
    
    # Per-threshold analysis
    print("\n" + "=" * 80)
    print("INDIVIDUAL THRESHOLD SENSITIVITY")
    print("=" * 80)
    
    for threshold_key in THRESHOLDS.keys():
        print(f"\n--- Varying only: {threshold_key} ---")
        
        single_results = {}
        for variation in variations:
            modified = THRESHOLDS.copy()
            base_val = modified[threshold_key]
            if isinstance(base_val, (int, float)):
                modified[threshold_key] = base_val * variation
            
            collapse_count = sum(1 for f in data if has_agency_collapse(f, modified)['collapse'])
            single_results[variation] = collapse_count / len(data) * 100
        
        print(f"  -20%: {single_results[0.8]:.1f}%  |  -10%: {single_results[0.9]:.1f}%  |  base: {single_results[1.0]:.1f}%  |  +10%: {single_results[1.1]:.1f}%  |  +20%: {single_results[1.2]:.1f}%")
        delta = single_results[0.8] - single_results[1.2]
        print(f"  Sensitivity: {abs(delta):.1f}pp swing")
    
    # Save if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Saved detailed results to {output_path}")
    
    print("\n✅ Sensitivity analysis complete")


if __name__ == "__main__":
    main()
