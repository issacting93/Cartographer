#!/usr/bin/env python3
"""
Evidence Feature Pipeline (v2)
===============================
Extracts claim-safe features from raw message text and turn structure.
These features are independent of classification labels and can be used
for clustering, ablation studies, and feature importance analysis.

Three evidence channels:
  A) Linguistic divergence (paired-turn human<->AI comparison)
  B) Functional<->Social expressiveness (per-message text analysis)
  C) Interaction dynamics markers (corrections, hedging, goal drift)

Plus: affect proxy (heuristic or transformer-based).

Usage:
  python3 scripts/evidence_features.py [--affect transformer|heuristic|none]

Outputs:
  data/v2_unified/evidence_features.csv  - one row per conversation
  data/v2_unified/affect_proxy/          - per-message affect scores (JSON)
"""

import json
import os
import re
import sys
import csv
import math
import statistics
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
EVIDENCE_OUTPUT = PROJECT_ROOT / "data" / "v2_unified" / "evidence_features.csv"
AFFECT_DIR = PROJECT_ROOT / "data" / "v2_unified" / "affect_proxy"

# ---------------------------------------------------------------------------
# Channel A: Linguistic Divergence (paired-turn)
# ---------------------------------------------------------------------------

FORMAL_MARKERS = re.compile(
    r'\b(thus|therefore|furthermore|moreover|however|nevertheless|consequently|'
    r'accordingly|additionally|subsequently|notwithstanding|whereas|hereby)\b', re.I)

INFORMAL_MARKERS = re.compile(
    r'\b(gonna|wanna|gotta|kinda|sorta|yeah|nah|lol|lmao|haha|hehe|'
    r'omg|btw|tbh|imo|idk|ngl|bruh|dude|bro|yo)\b', re.I)

HEDGE_MARKERS = re.compile(
    r'\b(maybe|perhaps|might|possibly|probably|could be|I think|not sure|'
    r'I guess|it seems|sort of|kind of|somewhat|arguably)\b', re.I)

CERTAINTY_MARKERS = re.compile(
    r'\b(definitely|certainly|clearly|obviously|absolutely|undoubtedly|'
    r'without doubt|for sure|no question|always|never|must be)\b', re.I)

POLITENESS_MARKERS = re.compile(
    r'\b(please|thank you|thanks|appreciate|kindly|excuse me|sorry|'
    r'pardon|if you don\'t mind|would you mind|I\'d appreciate)\b', re.I)

DIRECTIVE_MARKERS = re.compile(
    r'^(please |can you |could you |would you |do |make |write |create |'
    r'implement |add |fix |change |update |remove |delete |show |list |'
    r'explain |describe |tell me |give me |help me )', re.I | re.M)

SELF_REF_I = re.compile(r'\b(I|I\'m|I\'ve|I\'d|I\'ll|my|mine|myself)\b')
SELF_REF_YOU = re.compile(r'\b(you|you\'re|you\'ve|you\'d|you\'ll|your|yours|yourself)\b', re.I)
SELF_REF_WE = re.compile(r'\b(we|we\'re|we\'ve|we\'d|we\'ll|our|ours|ourselves|let\'s)\b', re.I)


def extract_linguistic_features(text: str) -> dict:
    """Extract linguistic features from a single message."""
    if not text or len(text.strip()) < 5:
        return {
            'formality': 0.5, 'hedging': 0.5, 'certainty': 0.5,
            'politeness': 0.0, 'question_density': 0.0, 'directive_density': 0.0,
            'pronoun_i': 0.0, 'pronoun_you': 0.0, 'pronoun_we': 0.0,
        }

    words = text.split()
    word_count = max(len(words), 1)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = max(len(sentences), 1)

    formal = len(FORMAL_MARKERS.findall(text))
    informal = len(INFORMAL_MARKERS.findall(text))
    formality = 0.5 + (formal - informal) / max(word_count, 1) * 10
    formality = max(0.0, min(1.0, formality))

    hedging = min(1.0, len(HEDGE_MARKERS.findall(text)) / sentence_count * 0.3)
    certainty = min(1.0, len(CERTAINTY_MARKERS.findall(text)) / sentence_count * 0.3)
    politeness = min(1.0, len(POLITENESS_MARKERS.findall(text)) / sentence_count * 0.25)

    questions = text.count('?')
    question_density = min(1.0, questions / sentence_count)

    directives = len(DIRECTIVE_MARKERS.findall(text))
    directive_density = min(1.0, directives / sentence_count)

    pronoun_i = min(1.0, len(SELF_REF_I.findall(text)) / word_count * 5)
    pronoun_you = min(1.0, len(SELF_REF_YOU.findall(text)) / word_count * 5)
    pronoun_we = min(1.0, len(SELF_REF_WE.findall(text)) / word_count * 5)

    return {
        'formality': formality, 'hedging': hedging, 'certainty': certainty,
        'politeness': politeness, 'question_density': question_density,
        'directive_density': directive_density,
        'pronoun_i': pronoun_i, 'pronoun_you': pronoun_you, 'pronoun_we': pronoun_we,
    }


def compute_divergence_trajectory(messages: list) -> list:
    """Compute per-turn linguistic divergence between user<->assistant pairs."""
    pairs = []
    i = 0
    while i < len(messages) - 1:
        if messages[i].get('role') == 'user' and messages[i + 1].get('role') == 'assistant':
            pairs.append((messages[i], messages[i + 1]))
            i += 2
        else:
            i += 1

    if not pairs:
        return []

    divergences = []
    for user_msg, ai_msg in pairs:
        user_feat = extract_linguistic_features(user_msg.get('content', ''))
        ai_feat = extract_linguistic_features(ai_msg.get('content', ''))
        diffs = [abs(user_feat[k] - ai_feat[k]) for k in user_feat]
        avg_diff = sum(diffs) / len(diffs)
        divergences.append(avg_diff)

    return divergences


def channel_a_features(messages: list) -> dict:
    """Channel A: Linguistic divergence trajectory features."""
    trajectory = compute_divergence_trajectory(messages)

    if len(trajectory) < 1:
        return {
            'div_mean': 0.0, 'div_variance': 0.0, 'div_trend': 0.0,
            'div_max_spike': 0.0, 'div_range': 0.0, 'div_n_pairs': 0,
        }

    div_mean = statistics.mean(trajectory)
    div_variance = statistics.variance(trajectory) if len(trajectory) > 1 else 0.0

    if len(trajectory) >= 2:
        n = len(trajectory)
        x_mean = (n - 1) / 2
        numerator = sum((i - x_mean) * (v - div_mean) for i, v in enumerate(trajectory))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        div_trend = numerator / denominator if denominator > 0 else 0.0
    else:
        div_trend = 0.0

    return {
        'div_mean': div_mean, 'div_variance': div_variance, 'div_trend': div_trend,
        'div_max_spike': max(trajectory), 'div_range': max(trajectory) - min(trajectory),
        'div_n_pairs': len(trajectory),
    }


# ---------------------------------------------------------------------------
# Channel B: Functional <-> Social Expressiveness
# ---------------------------------------------------------------------------

SOCIAL_MARKERS = [
    re.compile(r'\b(thanks|thank you|please|sorry|appreciate|love|enjoy|fun|interesting|amazing|awesome)\b', re.I),
    re.compile(r'[!]{2,}'),
    re.compile(r'\b(haha|lol|wow|cool|nice|great|wonderful)\b', re.I),
    re.compile(r'\b(I feel|I\'m worried|I\'m excited|I\'m frustrated|I think|I believe|I wonder|I hope)\b', re.I),
    re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]'),
]

FUNCTIONAL_MARKERS = [
    re.compile(r'\b(implement|code|function|error|fix|bug|write|create|compile|debug|deploy)\b', re.I),
    re.compile(r'\b(how to|what is|explain|describe|list|compare|define|summarize|calculate)\b', re.I),
    re.compile(r'```'),
    re.compile(r'\b(step \d|first|second|third|finally|next|then)\b', re.I),
    re.compile(r'\b(algorithm|database|API|server|client|framework|library|module)\b', re.I),
]


def message_expressiveness(text: str) -> float:
    """Score a message on the functional (0) <-> social (1) spectrum."""
    if not text:
        return 0.5
    social_count = sum(1 for pattern in SOCIAL_MARKERS if pattern.search(text))
    functional_count = sum(1 for pattern in FUNCTIONAL_MARKERS if pattern.search(text))
    total = social_count + functional_count
    if total == 0:
        return 0.5
    return social_count / total


def channel_b_features(messages: list) -> dict:
    """Channel B: Expressiveness trajectory features."""
    scores = [message_expressiveness(msg.get('content', '')) for msg in messages]

    if not scores:
        return {
            'expr_mean': 0.5, 'expr_variance': 0.0, 'expr_trend': 0.0,
            'expr_range': 0.0, 'expr_early_mean': 0.5, 'expr_late_mean': 0.5,
            'expr_shift': 0.0,
        }

    expr_mean = statistics.mean(scores)
    expr_variance = statistics.variance(scores) if len(scores) > 1 else 0.0

    if len(scores) >= 2:
        n = len(scores)
        x_mean = (n - 1) / 2
        numerator = sum((i - x_mean) * (v - expr_mean) for i, v in enumerate(scores))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        expr_trend = numerator / denominator if denominator > 0 else 0.0
    else:
        expr_trend = 0.0

    mid = len(scores) // 2
    early = scores[:max(mid, 1)]
    late = scores[max(mid, 1):]
    expr_early_mean = statistics.mean(early)
    expr_late_mean = statistics.mean(late) if late else expr_early_mean

    return {
        'expr_mean': expr_mean, 'expr_variance': expr_variance, 'expr_trend': expr_trend,
        'expr_range': max(scores) - min(scores),
        'expr_early_mean': expr_early_mean, 'expr_late_mean': expr_late_mean,
        'expr_shift': expr_late_mean - expr_early_mean,
    }


# ---------------------------------------------------------------------------
# Channel C: Interaction Dynamics Markers
# ---------------------------------------------------------------------------

CORRECTION_MARKERS = re.compile(
    r'\b(no[,.]?\s+(that\'s|this is|it is)|not\s+(quite|right|correct|what)|'
    r'you misunderstood|that\'s wrong|incorrect|that\'s not|actually,?\s+I|'
    r'I (said|meant|asked)|let me (rephrase|clarify))\b', re.I)

CONSTRAINT_MARKERS = re.compile(
    r'\b(I said|remember that|must|don\'t|do not|should not|'
    r'as I mentioned|like I said|I already|I specifically|'
    r'I need you to|make sure|be sure to|important:)\b', re.I)

AI_HEDGE_MARKERS = re.compile(
    r'\b(might|maybe|I\'m not sure|it\'s possible|could be|'
    r'I think|perhaps|it seems|it appears|arguably|'
    r'I\'m not certain|to my knowledge|as far as I know)\b', re.I)

AI_ASSERT_MARKERS = re.compile(
    r'\b(definitely|certainly|absolutely|clearly|obviously|'
    r'without doubt|undoubtedly|for sure|always|never|'
    r'the answer is|the correct)\b', re.I)

REFUSAL_MARKERS = re.compile(
    r'\b(I can\'t|I cannot|I\'m unable|I\'m not able|'
    r'I don\'t have|I\'m not allowed|as an AI|'
    r'I apologize but|I\'m sorry but I|against my)\b', re.I)


def channel_c_features(messages: list) -> dict:
    """Channel C: Interaction dynamics features."""
    user_msgs = [m for m in messages if m.get('role') == 'user']
    ai_msgs = [m for m in messages if m.get('role') == 'assistant']
    n_turns = max(len(user_msgs), 1)

    corrections = sum(len(CORRECTION_MARKERS.findall(m.get('content', ''))) for m in user_msgs)
    constraints = sum(len(CONSTRAINT_MARKERS.findall(m.get('content', ''))) for m in user_msgs)
    ai_hedges = sum(len(AI_HEDGE_MARKERS.findall(m.get('content', ''))) for m in ai_msgs)
    ai_asserts = sum(len(AI_ASSERT_MARKERS.findall(m.get('content', ''))) for m in ai_msgs)
    ai_refusals = sum(len(REFUSAL_MARKERS.findall(m.get('content', ''))) for m in ai_msgs)

    goal_drifts = []
    for i in range(1, len(user_msgs)):
        words_prev = set(user_msgs[i - 1].get('content', '').lower().split())
        words_curr = set(user_msgs[i].get('content', '').lower().split())
        if words_prev or words_curr:
            union = words_prev | words_curr
            intersection = words_prev & words_curr
            jaccard = len(intersection) / len(union) if union else 1.0
            goal_drifts.append(1.0 - jaccard)

    user_lengths = [len(m.get('content', '').split()) for m in user_msgs]
    ai_lengths = [len(m.get('content', '').split()) for m in ai_msgs]
    avg_user_len = statistics.mean(user_lengths) if user_lengths else 1
    avg_ai_len = statistics.mean(ai_lengths) if ai_lengths else 1
    length_ratio = avg_ai_len / max(avg_user_len, 1)

    hedge_total = ai_hedges + ai_asserts
    hedge_assert_ratio = ai_hedges / hedge_total if hedge_total > 0 else 0.5

    return {
        'repair_rate': corrections / n_turns,
        'constraint_pressure': constraints / n_turns,
        'hedge_assert_ratio': hedge_assert_ratio,
        'ai_refusal_rate': ai_refusals / max(len(ai_msgs), 1),
        'goal_drift_mean': statistics.mean(goal_drifts) if goal_drifts else 0.0,
        'goal_drift_variance': statistics.variance(goal_drifts) if len(goal_drifts) > 1 else 0.0,
        'goal_stability': 1.0 - (statistics.mean(goal_drifts) if goal_drifts else 0.0),
        'length_ratio': min(length_ratio, 10.0),
    }


# ---------------------------------------------------------------------------
# Affect Proxy
# ---------------------------------------------------------------------------

def compute_affect_heuristic(text: str) -> dict:
    """Enriched heuristic affect proxy."""
    if not text or len(text.strip()) < 3:
        return {'valence': 0.5, 'activation': 0.3, 'dominance': 0.5, 'intensity': 0.38}

    clean = text.lower()
    words = text.split()
    word_count = max(len(words), 1)
    char_count = max(len(text), 1)

    # Valence
    valence = 0.5
    frustration_patterns = [
        r'\b(wrong|incorrect|error|mistake|failed|broken)\b',
        r'\bnot\s+(quite|right|correct|working)',
        r'\b(doesn\'t|does not|can\'t|cannot|won\'t)\s+(work|seem|make sense)',
        r'\b(issue|problem|bug|fault)\b',
    ]
    frust_count = sum(len(re.findall(p, clean)) for p in frustration_patterns)
    valence -= min(0.4, frust_count * 0.08)

    satisfaction_patterns = [
        r'\b(perfect|exactly|brilliant|excellent|amazing|awesome|fantastic|wonderful)\b',
        r'\b(thanks|thank you)\b',
        r'\b(works?\s+perfectly|that\'s it|exactly what)\b',
        r'\b(great|good|nice|love it)\b',
    ]
    satis_count = sum(len(re.findall(p, clean)) for p in satisfaction_patterns)
    valence += min(0.4, satis_count * 0.08)
    valence = max(0.0, min(1.0, valence))

    # Activation
    activation = 0.3
    activation += min(0.3, text.count('!') * 0.06)
    caps_ratio = sum(1 for c in text if c.isupper()) / char_count
    activation += min(0.2, caps_ratio * 2)
    activation += min(0.15, text.count('?') * 0.05)
    urgency_count = len(re.findall(r'\b(urgent|asap|quickly|immediately|help|hurry|rush)\b', clean))
    activation += min(0.2, urgency_count * 0.08)
    if word_count < 10:
        activation += 0.05
    activation = max(0.0, min(1.0, activation))

    # Dominance
    is_question = '?' in text
    is_command = bool(re.match(
        r'^(please |can you |could you |would you |do |make |write |create |'
        r'implement |add |fix |change |show |tell |give |help )', clean))
    has_apology = bool(re.search(r'\b(sorry|apologize|apologies)\b', clean))
    dominance = 0.5
    if is_question:
        dominance -= 0.15
    if is_command:
        dominance += 0.15
    if has_apology:
        dominance -= 0.25
    dominance = max(0.0, min(1.0, dominance))

    intensity = (1.0 - valence) * 0.6 + activation * 0.4
    intensity = max(0.0, min(1.0, intensity))

    return {
        'valence': round(valence, 4), 'activation': round(activation, 4),
        'dominance': round(dominance, 4), 'intensity': round(intensity, 4),
    }


def affect_trajectory_features(messages: list, affect_scores: list) -> dict:
    """Derive trajectory features from per-message affect scores."""
    intensities = [s['intensity'] for s in affect_scores]
    valences = [s['valence'] for s in affect_scores]

    if not intensities:
        return {
            'affect_mean': 0.5, 'affect_variance': 0.0, 'affect_trend': 0.0,
            'affect_range': 0.0, 'affect_max': 0.5, 'affect_min': 0.5,
            'affect_peak_count': 0, 'affect_valley_count': 0,
            'valence_mean': 0.5, 'valence_variance': 0.0, 'valence_trend': 0.0,
        }

    aff_mean = statistics.mean(intensities)
    aff_var = statistics.variance(intensities) if len(intensities) > 1 else 0.0

    if len(intensities) >= 2:
        n = len(intensities)
        x_mean = (n - 1) / 2
        num = sum((i - x_mean) * (v - aff_mean) for i, v in enumerate(intensities))
        den = sum((i - x_mean) ** 2 for i in range(n))
        aff_trend = num / den if den > 0 else 0.0
    else:
        aff_trend = 0.0

    peaks = valleys = 0
    for i in range(1, len(intensities) - 1):
        if intensities[i] > intensities[i - 1] and intensities[i] > intensities[i + 1]:
            peaks += 1
        if intensities[i] < intensities[i - 1] and intensities[i] < intensities[i + 1]:
            valleys += 1

    val_mean = statistics.mean(valences)
    val_var = statistics.variance(valences) if len(valences) > 1 else 0.0
    if len(valences) >= 2:
        n = len(valences)
        x_mean = (n - 1) / 2
        num = sum((i - x_mean) * (v - val_mean) for i, v in enumerate(valences))
        den = sum((i - x_mean) ** 2 for i in range(n))
        val_trend = num / den if den > 0 else 0.0
    else:
        val_trend = 0.0

    return {
        'affect_mean': aff_mean, 'affect_variance': aff_var, 'affect_trend': aff_trend,
        'affect_range': max(intensities) - min(intensities),
        'affect_max': max(intensities), 'affect_min': min(intensities),
        'affect_peak_count': peaks, 'affect_valley_count': valleys,
        'valence_mean': val_mean, 'valence_variance': val_var, 'valence_trend': val_trend,
    }


# ---------------------------------------------------------------------------
# Structural features
# ---------------------------------------------------------------------------

def structural_features(messages: list) -> dict:
    """Basic structural features independent of classification."""
    n = len(messages)
    user_msgs = [m for m in messages if m.get('role') == 'user']
    ai_msgs = [m for m in messages if m.get('role') == 'assistant']

    user_lengths = [len(m.get('content', '').split()) for m in user_msgs]
    ai_lengths = [len(m.get('content', '').split()) for m in ai_msgs]

    return {
        'n_messages': n,
        'n_messages_log': math.log(n + 1),
        'n_user_messages': len(user_msgs),
        'n_ai_messages': len(ai_msgs),
        'user_avg_length': statistics.mean(user_lengths) if user_lengths else 0,
        'ai_avg_length': statistics.mean(ai_lengths) if ai_lengths else 0,
        'user_length_var': statistics.variance(user_lengths) if len(user_lengths) > 1 else 0,
        'ai_length_var': statistics.variance(ai_lengths) if len(ai_lengths) > 1 else 0,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def extract_all_features(conv_id: str, data: dict, affect_mode: str = 'heuristic',
                         sentiment_pipeline=None) -> Tuple[dict, list]:
    """Extract all evidence features for a single conversation."""
    messages = data.get('messages', [])

    affect_scores = []
    for msg in messages:
        text = msg.get('content', '')
        score = compute_affect_heuristic(text)
        score['role'] = msg.get('role', 'unknown')
        affect_scores.append(score)

    features = {'conv_id': conv_id}
    features.update(channel_a_features(messages))
    features.update(channel_b_features(messages))
    features.update(channel_c_features(messages))
    features.update(affect_trajectory_features(messages, affect_scores))
    features.update(structural_features(messages))

    return features, affect_scores


def main():
    affect_mode = 'heuristic'
    if '--affect' in sys.argv:
        idx = sys.argv.index('--affect')
        if idx + 1 < len(sys.argv):
            affect_mode = sys.argv[idx + 1]

    print("=" * 60)
    print("EVIDENCE FEATURE PIPELINE (v2)")
    print(f"  Affect mode: {affect_mode}")
    print(f"  Source: {CANONICAL_DIR}")
    print("=" * 60)

    canonical_files = sorted(CANONICAL_DIR.glob('*.json'))
    print(f"\n  Canonical corpus: {len(canonical_files)} conversations")

    if not canonical_files:
        print("  ERROR: No files found. Run build_corpus.py first.")
        sys.exit(1)

    all_features = []
    all_affect = {}
    feature_names = None

    for i, fpath in enumerate(canonical_files):
        conv_id = fpath.stem
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  WARNING: Could not read {conv_id}: {e}")
            continue

        features, affect_scores = extract_all_features(conv_id, data, affect_mode)

        all_features.append(features)
        all_affect[conv_id] = affect_scores

        if feature_names is None:
            feature_names = [k for k in features.keys()]

        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(canonical_files)}...")

    print(f"\n  Extracted features for {len(all_features)} conversations")
    print(f"  Feature count: {len(feature_names) - 1} (excluding conv_id)")

    # Write evidence features CSV
    EVIDENCE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_OUTPUT, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=feature_names)
        writer.writeheader()
        writer.writerows(all_features)
    print(f"\n  Written: {EVIDENCE_OUTPUT}")

    # Write per-message affect scores
    AFFECT_DIR.mkdir(parents=True, exist_ok=True)
    for conv_id, scores in all_affect.items():
        with open(AFFECT_DIR / f"{conv_id}.json", 'w') as f:
            json.dump(scores, f, indent=2)
    print(f"  Written: {len(all_affect)} affect files to {AFFECT_DIR}")

    # Print feature summary statistics
    print(f"\n{'=' * 60}")
    print("FEATURE SUMMARY")
    print(f"{'=' * 60}")

    numeric_keys = [k for k in feature_names if k != 'conv_id']
    for key in numeric_keys:
        values = [float(f[key]) for f in all_features if f.get(key) is not None]
        if not values:
            continue
        unique = len(set(round(v, 6) for v in values))
        print(f"  {key:30s}  mean={statistics.mean(values):.4f}  "
              f"std={statistics.stdev(values) if len(values) > 1 else 0:.4f}  "
              f"unique={unique:4d}  "
              f"range=[{min(values):.4f}, {max(values):.4f}]")


if __name__ == '__main__':
    main()
