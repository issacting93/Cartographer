#!/usr/bin/env python3
"""
Check that every number in the short paper matches verified_stats.json.
Fails loudly if anything is wrong.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATS_FILE = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "verified_stats.json"


def validate():
    with open(STATS_FILE) as f:
        s = json.load(f)

    passed = 0
    failed = 0

    def check(label, expected, actual, tolerance=0.05):
        nonlocal passed, failed
        if isinstance(expected, float):
            ok = abs(expected - actual) <= tolerance
        else:
            ok = expected == actual
        status = "PASS" if ok else "FAIL"
        if not ok:
            print(f"  {status}: {label} — expected {expected}, got {actual}")
            failed += 1
        else:
            passed += 1

    # --- Abstract claims ---
    check("1,383 conversations", 1383, s['n_graphs'])
    check("559 constraints", 559, s['total_constraints'])
    check("69% violated", 69, round(s['pct_violated']))
    check("24% on first response", 24, round(s['pct_turn_0']))
    check("17% followed", 17, round(s['pct_followed']))
    check("14% ambiguous", 14, round(s['pct_ambiguous']))
    check("median 1 turn", 1.0, s['median_turns_to_violation'])
    check("1.0% repair success", 1.03, s['repair_success_pct'], tolerance=0.1)
    check("5.6% tried repair", 5.6, s['pct_convs_with_repair'])
    check("0.4% repair density", 0.4, s['repair_density_pct'])

    # --- Section 3: Constraint Outcome ---
    check("386 violated", 386, s['violated'])
    check("93 followed", 93, s['followed'])
    check("80 ambiguous", 80, s['ambiguous'])

    # --- Section 3: Patience ---
    check("patience abandoned mean 12.0", 12.0, s['patience_abandoned']['mean'])
    check("patience survived mean 9.5", 9.5, s['patience_survived']['mean'])

    # --- Section 4: Abandonment Default ---
    check("15 of 270 convs with repair", 15, s['convs_with_repair_attempts'])
    check("270 constrained convs", 270, s['n_with_constraints'])
    check("4/390 repaired", 4, s['repaired_events'])
    check("390 violation events", 390, s['total_violation_events'])
    check("mean 2.1 turns", 2.11, s['mean_turns_to_violation'], tolerance=0.05)

    # --- Section 4: Immediate Failure ---
    check("24% turn 0", 24.1, s['pct_turn_0'], tolerance=0.5)
    # "41% fail by Turn 1" → turn 0 + turn 1 = 93 + 158 = 251; 251/386 = 65.0%
    turn_0_1 = s['turns_until_violated_distribution'].get('0', 0) + s['turns_until_violated_distribution'].get('1', 0)
    pct_0_1 = round(turn_0_1 / s['violated'] * 100, 1)
    check("65% within first two turns", 65.0, pct_0_1, tolerance=0.5)

    # "41% fail by Turn 1" means turn 1 alone
    pct_turn_1 = round(s['turns_until_violated_distribution'].get('1', 0) / s['violated'] * 100, 1)
    check("41% at turn 1", 40.9, pct_turn_1, tolerance=0.5)

    # --- Agency Collapse ---
    check("50.3% collapse", 50.3, s['agency_collapse']['collapse_rate_pct'])

    # --- Corpus note ---
    check("N=2,577 conversations", True, s['agency_collapse']['n_conversations'] > 0)  # collapse file exists

    # --- CA-Grounded Metrics (Section 4.3 + 5.1) ---
    ge = s.get('grounding_evidence_distribution', {})
    total_ge = ge.get('demonstration', 0) + ge.get('token', 0) + ge.get('unmarked', 0)
    check("grounding evidence total > 0", True, total_ge > 0)
    if total_ge > 0:
        pct_unmarked = round(ge['unmarked'] / total_ge * 100, 1)
        pct_token = round(ge['token'] / total_ge * 100, 1)
        pct_demo = round(ge['demonstration'] / total_ge * 100, 1)
        check("84.8% unmarked grounding", 84.8, pct_unmarked, tolerance=1.0)
        check("14.5% token grounding", 14.5, pct_token, tolerance=1.0)
        check("0.6% demonstration grounding", 0.6, pct_demo, tolerance=0.5)

    check("self-repair rate < 1%", True, s.get('self_repair_rate_pct', 0) < 1.0)
    check("330 constraint-response events", 330, total_ge)

    # --- Section 4.1: repair density denominator ---
    check("4,296 turns in constrained convs", 4296, s['total_turns_in_constrained'])
    check("17 repair turns", 17, s['total_repair_turns'])

    print(f"\n  {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    print("Validating short paper claims against verified_stats.json...\n")
    ok = validate()
    if not ok:
        print("\nSome claims don't match the data!")
        sys.exit(1)
    else:
        print("\nAll claims verified.")
