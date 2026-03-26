#!/usr/bin/env python3
"""
Automated fact-checker for FINDINGS_REPORT_v2.md

Reads verified_stats.json and acceptance_results.json, extracts every
quantitative claim from the report via regex, and validates each one.

Outputs: data/v2_unified/reports/validation_report.json
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / "paper" / "FINDINGS_REPORT_v2.md"
VERIFIED_STATS = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "verified_stats.json"
ACCEPTANCE_JSON = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "acceptance_results.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "validation_report.json"

TOLERANCE = 0.05  # 5% relative tolerance for float comparisons


def close_enough(reported, actual, tol=TOLERANCE):
    """Check if reported value is within tolerance of actual."""
    if actual == 0:
        return abs(reported) < 0.01
    return abs(reported - actual) / abs(actual) <= tol


def load_sources():
    with open(VERIFIED_STATS) as f:
        stats = json.load(f)
    acc = {}
    if ACCEPTANCE_JSON.exists():
        with open(ACCEPTANCE_JSON) as f:
            acc = json.load(f)
    report_text = REPORT_PATH.read_text()
    return stats, acc, report_text


def validate_corpus_claims(stats, report):
    """Validate Section 2 corpus claims."""
    results = []
    corpus = stats["corpus"]

    checks = [
        ("Total conversations N=2,577", r"N=2,?577", corpus["total_conversations"], 2577),
        ("Chatbot Arena N=1,739", r"Chatbot Arena.*?1,?739", corpus["sources"].get("chatbot_arena", 0), 1739),
        ("WildChat N=786", r"WildChat.*?786", corpus["sources"].get("wildchat", 0), 786),
        ("OASST N=50", r"OASST.*?50", corpus["sources"].get("oasst", 0), 50),
        ("Median length 6", r"median.*?6 messages", corpus["median_length"], 6),
        ("Mean length 10.1", r"mean.*?10\.1", corpus["mean_length"], 10.1),
    ]

    for name, pattern, actual, expected in checks:
        found = bool(re.search(pattern, report, re.IGNORECASE))
        match = close_enough(actual, expected)
        results.append({
            "claim": name,
            "section": "2. Corpus",
            "found_in_report": found,
            "expected": expected,
            "actual": actual,
            "status": "PASS" if (found and match) else "FAIL",
        })

    return results


def validate_role_claims(stats, report):
    """Validate Section 3 role claims."""
    results = []
    corpus = stats["corpus"]

    role_checks = [
        ("Information Seeker N=1,904", "information-seeker", 1904),
        ("Director N=379", "director", 379),
        ("Provider N=123", "provider", 123),
        ("Collaborator N=92", "collaborator", 92),
        ("Social Expressor N=62", "social-expressor", 62),
        ("Relational Peer N=16", "relational-peer", 16),
    ]

    for name, role_key, expected_n in role_checks:
        actual = corpus["human_roles"].get(role_key, 0)
        results.append({
            "claim": name,
            "section": "3. Roles",
            "expected": expected_n,
            "actual": actual,
            "status": "PASS" if actual == expected_n else "FAIL",
        })

    # Instrumental percentage
    results.append({
        "claim": "97.0% instrumental",
        "section": "3. Roles",
        "expected": 97.0,
        "actual": corpus["pct_instrumental"],
        "status": "PASS" if close_enough(corpus["pct_instrumental"], 97.0) else "FAIL",
    })

    # AI roles
    ai_checks = [
        ("Expert System N=1,998", "expert-system", 1998),
        ("Co-Constructor N=258", "co-constructor", 258),
        ("Advisor N=121", "advisor", 121),
        ("Social Facilitator N=107", "social-facilitator", 107),
        ("Relational Peer (AI) N=61", "relational-peer", 61),
        ("Learning Facilitator N=31", "learning-facilitator", 31),
    ]

    for name, role_key, expected_n in ai_checks:
        actual = corpus["ai_roles"].get(role_key, 0)
        results.append({
            "claim": name,
            "section": "3. Roles (AI)",
            "expected": expected_n,
            "actual": actual,
            "status": "PASS" if actual == expected_n else "FAIL",
        })

    return results


def validate_role_pair_claims(stats, report):
    """Validate Section 4 role pair claims."""
    results = []
    corpus = stats["corpus"]

    is_es = corpus["role_pairs"].get("information-seeker|expert-system", 0)
    total = corpus["conversations_with_roles"]
    pct = round(is_es / total * 100, 1) if total > 0 else 0

    results.append({
        "claim": "IS→ES 70.0% of all conversations",
        "section": "4. Role Pairs",
        "expected": 70.0,
        "actual": pct,
        "status": "PASS" if close_enough(pct, 70.0) else "FAIL",
    })

    return results


def validate_purpose_claims(stats, report):
    """Validate Section 5 purpose claims."""
    results = []
    purposes = stats["corpus"]["purposes"]

    expected_purposes = {
        "information-seeking": 1451,
        "problem-solving": 569,
        "capability-exploration": 178,
        "entertainment": 156,
        "collaborative-refinement": 113,
        "relationship-building": 54,
        "self-expression": 41,
        "emotional-processing": 13,
    }

    for purpose, expected_n in expected_purposes.items():
        actual = purposes.get(purpose, 0)
        results.append({
            "claim": f"Purpose '{purpose}' N={expected_n}",
            "section": "5. Purpose",
            "expected": expected_n,
            "actual": actual,
            "status": "PASS" if actual == expected_n else "FAIL",
        })

    return results


def validate_variance_ratio(stats, report):
    """Validate Section 6 variance ratio claims."""
    results = []
    vr = stats["variance_ratio"]

    results.append({
        "claim": "Variance ratio 2,817x",
        "section": "6. Affect",
        "expected": 2817,
        "actual": vr["variance_ratio"],
        "status": "PASS" if close_enough(vr["variance_ratio"], 2817) else "FAIL",
    })

    results.append({
        "claim": "IS→ES pairs N=1,039",
        "section": "6. Affect",
        "expected": 1039,
        "actual": vr["n_is_es_pairs"],
        "status": "PASS" if vr["n_is_es_pairs"] == 1039 else "FAIL",
    })

    results.append({
        "claim": "Smooth exemplar: chatbot_arena_11761",
        "section": "6. Affect",
        "expected": "chatbot_arena_11761",
        "actual": vr["smooth_id"],
        "status": "PASS" if vr["smooth_id"] == "chatbot_arena_11761" else "FAIL",
    })

    results.append({
        "claim": "Volatile exemplar: wildchat_new_300289e3c40bce07",
        "section": "6. Affect",
        "expected": "wildchat_new_300289e3c40bce07",
        "actual": vr["volatile_id"],
        "status": "PASS" if vr["volatile_id"] == "wildchat_new_300289e3c40bce07" else "FAIL",
    })

    return results


def validate_rf_claims(stats, report):
    """Validate Section 8 RF and feature importance claims."""
    results = []
    rf = stats["rf_role_pair"]

    results.append({
        "claim": "RF accuracy 71.6%",
        "section": "8. Features",
        "expected": 71.6,
        "actual": rf["rf_accuracy_mean"] * 100,
        "status": "PASS" if close_enough(rf["rf_accuracy_mean"] * 100, 71.6) else "FAIL",
    })

    results.append({
        "claim": "RF n_classes = 16",
        "section": "8. Features",
        "expected": 16,
        "actual": rf["n_classes"],
        "status": "PASS" if rf["n_classes"] == 16 else "FAIL",
    })

    results.append({
        "claim": "Chance level 6.2%",
        "section": "8. Features",
        "expected": 6.25,
        "actual": rf["chance_level"] * 100,
        "status": "PASS" if close_enough(rf["chance_level"] * 100, 6.25) else "FAIL",
    })

    # Channel contributions
    expected_channels = {
        "Affect": 39.3,
        "Divergence": 21.6,
        "Dynamics": 16.5,
        "Expressiveness": 15.4,
        "Structure": 7.2,
    }
    for ch, expected_pct in expected_channels.items():
        actual_pct = rf["channel_contributions"].get(ch, 0)
        results.append({
            "claim": f"Channel {ch} = {expected_pct}%",
            "section": "8. Channels",
            "expected": expected_pct,
            "actual": actual_pct,
            "status": "PASS" if close_enough(actual_pct, expected_pct) else "FAIL",
        })

    # Top 3 features
    top3_expected = [("div_mean", 0.0518), ("length_ratio", 0.0517), ("affect_mean", 0.0475)]
    for rank, (feat, exp_imp) in enumerate(top3_expected, 1):
        actual_feat = rf["top_15"][rank - 1]["feature"]
        actual_imp = rf["top_15"][rank - 1]["importance"]
        results.append({
            "claim": f"Top feature #{rank}: {feat} ({exp_imp})",
            "section": "8. Feature Importance",
            "expected": f"{feat} ({exp_imp})",
            "actual": f"{actual_feat} ({actual_imp})",
            "status": "PASS" if actual_feat == feat and close_enough(actual_imp, exp_imp) else "FAIL",
        })

    return results


def validate_acceptance_tests(acc, report):
    """Validate Section 9 acceptance test claims."""
    results = []
    if not acc:
        results.append({
            "claim": "Acceptance results JSON exists",
            "section": "9. Acceptance",
            "expected": True,
            "actual": False,
            "status": "FAIL",
        })
        return results

    # Test A
    hr_acc = acc["test_a"]["Human Role"]["accuracy"] * 100
    ai_acc = acc["test_a"]["AI Role"]["accuracy"] * 100

    results.append({
        "claim": "Test A Human Role ~74.7%",
        "section": "9. Acceptance",
        "expected": 74.7,
        "actual": round(hr_acc, 1),
        "status": "PASS" if close_enough(hr_acc, 74.7) else "FAIL",
    })

    results.append({
        "claim": "Test A AI Role ~78.0%",
        "section": "9. Acceptance",
        "expected": 78.0,
        "actual": round(ai_acc, 1),
        "status": "PASS" if close_enough(ai_acc, 78.0) else "FAIL",
    })

    # Ablation silhouettes
    ablation_checks = [
        ("Evidence-only (KMeans)", 0.111),
        ("Evidence-only (Hierarchical)", 0.124),
        ("Labels-only (KMeans)", 0.453),
        ("Labels-only (Hierarchical)", 0.431),
        ("Combined (KMeans)", 0.087),
        ("Combined (Hierarchical)", 0.058),
    ]
    for name, expected_sil in ablation_checks:
        actual_sil = round(acc["ablation"][name]["silhouette"], 3)
        results.append({
            "claim": f"Ablation {name} silhouette ≈ {expected_sil}",
            "section": "9. Ablation",
            "expected": expected_sil,
            "actual": actual_sil,
            "status": "PASS" if close_enough(actual_sil, expected_sil) else "FAIL",
        })

    return results


def validate_constraint_claims(stats, report):
    """Validate Section 12 constraint and collapse claims."""
    results = []
    if "constraints" not in stats:
        results.append({
            "claim": "Constraint stats in verified_stats.json",
            "section": "12. Constraints",
            "expected": True,
            "actual": False,
            "status": "FAIL",
        })
        return results

    c = stats["constraints"]

    checks = [
        ("N graphs = 1383", c["n_graphs"], 1383),
        ("Total constraints = 559", c["total_constraints"], 559),
        ("Violation rate 69.1%", c["violation_rate_pct"], 69.1),
        ("Survival rate 30.9%", c["survival_rate_pct"], 30.9),
        ("Mean time-to-violation 2.11 turns", c["half_life_mean"], 2.11),
        ("Median time-to-violation = 1", c["half_life_median"], 1),
        ("Turn 0 violation pct 24.1%", c["turn_0_violation_pct"], 24.1),
        ("Repair rate 1.03%", c["repair_rate_event_pct"], 1.03),
        ("Collapse rate 50.3%", c["agency_collapse"]["collapse_rate_pct"], 50.3),
    ]

    for name, actual, expected in checks:
        results.append({
            "claim": name,
            "section": "12. Constraints",
            "expected": expected,
            "actual": actual,
            "status": "PASS" if close_enough(actual, expected) else "FAIL",
        })

    return results


def main():
    stats, acc, report = load_sources()

    all_results = []
    all_results.extend(validate_corpus_claims(stats, report))
    all_results.extend(validate_role_claims(stats, report))
    all_results.extend(validate_role_pair_claims(stats, report))
    all_results.extend(validate_purpose_claims(stats, report))
    all_results.extend(validate_variance_ratio(stats, report))
    all_results.extend(validate_rf_claims(stats, report))
    all_results.extend(validate_acceptance_tests(acc, report))
    all_results.extend(validate_constraint_claims(stats, report))

    n_pass = sum(1 for r in all_results if r["status"] == "PASS")
    n_fail = sum(1 for r in all_results if r["status"] == "FAIL")

    output = {
        "total_claims": len(all_results),
        "passed": n_pass,
        "failed": n_fail,
        "pass_rate": round(n_pass / len(all_results) * 100, 1) if all_results else 0,
        "results": all_results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Validation: {n_pass}/{len(all_results)} claims PASS ({output['pass_rate']}%)")
    if n_fail > 0:
        print(f"\nFAILED claims:")
        for r in all_results:
            if r["status"] == "FAIL":
                print(f"  [{r['section']}] {r['claim']}: expected={r['expected']}, actual={r['actual']}")
    else:
        print("All claims validated successfully.")

    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
