#!/usr/bin/env python3
"""
STEP 4: Agency Collapse Detection (Outcome Variable)

Defines collapse INDEPENDENTLY of clusters.
Collapse is an outcome, not a category.

Thresholds are adjustable and empirically motivated.
"""

import json
import argparse
from pathlib import Path


# ============= COLLAPSE THRESHOLDS =============
# These are adjustable. Document your choices.

THRESHOLDS = {
    # Condition A: Repeated failed repairs
    'repair_count_min': 3,
    'repair_success_max': 0.3,
    
    # Condition B: Tone degradation
    'politeness_delta_min': -0.5,  # Must be this negative or more
    
    # Condition C: Specificity collapse with passivity
    'specificity_delta_min': -1.0,
    'passive_rate_min': 0.4,
}


def has_agency_collapse(features: dict, thresholds: dict = THRESHOLDS) -> dict:
    """
    Determine if a conversation shows Agency Collapse.
    
    Works with both regex features and LLM-enhanced features.
    
    Returns dict with:
    - collapse: bool
    - conditions: list of which conditions triggered
    - confidence: float (0-1, based on how strongly conditions are met)
    """
    conditions_met = []
    confidence_scores = []
    
    # Condition A: Repeated failed repairs
    # For LLM features: repair_count >= 3 (no success rate available)
    # For regex features: repair_count >= 3 AND success < 30%
    repair_count = features.get('repair_count', 0)
    if repair_count >= thresholds['repair_count_min']:
        repair_success = features.get('repair_success_rate', None)
        if repair_success is not None:
            # Regex features: check success rate
            if repair_success < thresholds['repair_success_max']:
                conditions_met.append('repair_failure')
                confidence_scores.append(1.0 - repair_success)
        else:
            # LLM features: high repair count alone indicates failure
            # (LLM already classified these as repair attempts)
            if repair_count >= 5:  # Higher threshold since no success rate filter
                conditions_met.append('repair_failure')
                confidence_scores.append(min(1.0, repair_count / 10))
    
    # Condition B: Tone degradation
    # For LLM features: use stance_delta (positive = becoming passive/frustrated)
    # For regex features: use politeness_delta + frustration_trend
    politeness_delta = features.get('politeness_delta', 0)
    stance_delta = features.get('stance_delta', None)
    frustration_trend = features.get('frustration_trend', 'stable')
    
    if stance_delta is not None:
        # LLM features: stance increasing (becoming more passive/frustrated)
        if stance_delta > 0.5 and politeness_delta < -0.2:
            conditions_met.append('tone_degradation')
            confidence_scores.append(min(1.0, stance_delta))
    else:
        # Regex features: politeness delta + frustration
        if politeness_delta < thresholds['politeness_delta_min']:
            if frustration_trend == 'increasing':
                conditions_met.append('tone_degradation')
                confidence_scores.append(min(1.0, abs(politeness_delta)))
    
    # Condition C: Specificity collapse with passivity
    # "User became less specific AND increasingly passive"
    specificity_delta = features.get('specificity_delta', 0)
    passive_rate = features.get('passive_rate', 0)
    
    if specificity_delta < thresholds['specificity_delta_min']:
        if passive_rate > thresholds['passive_rate_min']:
            conditions_met.append('specificity_collapse')
            # Confidence based on severity
            severity = (abs(specificity_delta) / 2) * (passive_rate / 0.5)
            confidence_scores.append(min(1.0, severity))
    
    # Final determination
    collapse = len(conditions_met) > 0
    confidence = max(confidence_scores) if confidence_scores else 0.0
    
    return {
        'collapse': collapse,
        'conditions': conditions_met,
        'confidence': round(confidence, 3),
        'n_conditions': len(conditions_met),
    }


def main():
    parser = argparse.ArgumentParser(description="Detect Agency Collapse in conversations")
    parser.add_argument("--input", "-i", required=True, help="Input features JSON")
    parser.add_argument("--output", "-o", required=True, help="Output JSON with collapse labels")
    parser.add_argument("--thresholds", "-t", help="Custom thresholds JSON (optional)")
    args = parser.parse_args()
    
    # Load features
    with open(args.input, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} conversations")
    
    # Load custom thresholds if provided
    thresholds = THRESHOLDS.copy()
    if args.thresholds:
        with open(args.thresholds, 'r') as f:
            custom = json.load(f)
            thresholds.update(custom)
        print(f"Using custom thresholds: {thresholds}")
    
    # Detect collapse
    results = []
    collapse_count = 0
    condition_counts = {'repair_failure': 0, 'tone_degradation': 0, 'specificity_collapse': 0}
    
    for features in data:
        collapse_result = has_agency_collapse(features, thresholds)
        
        # Add to features
        enriched = features.copy()
        enriched['collapse'] = collapse_result['collapse']
        enriched['collapse_conditions'] = collapse_result['conditions']
        enriched['collapse_confidence'] = collapse_result['confidence']
        enriched['collapse_n_conditions'] = collapse_result['n_conditions']
        
        results.append(enriched)
        
        if collapse_result['collapse']:
            collapse_count += 1
            for cond in collapse_result['conditions']:
                condition_counts[cond] += 1
    
    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Saved to {output_path}")
    
    # Statistics
    collapse_rate = collapse_count / len(results) * 100
    print(f"\n📊 Agency Collapse Results:")
    print(f"  Total conversations: {len(results)}")
    print(f"  Collapse detected: {collapse_count} ({collapse_rate:.1f}%)")
    print(f"\n  Condition breakdown:")
    for cond, count in condition_counts.items():
        pct = count / len(results) * 100
        print(f"    {cond}: {count} ({pct:.1f}%)")
    
    print(f"\n  Thresholds used:")
    for key, val in thresholds.items():
        print(f"    {key}: {val}")
    
    print("\n✅ Collapse detection complete")
    print("Next: Run cluster.py (if not done) then name_archetypes.py")


if __name__ == "__main__":
    main()
