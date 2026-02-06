#!/usr/bin/env python3
"""
analyze_existing.py - Analyze existing conversation data

Generates statistics for the paper's N=562 analysis section.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/Users/zac/Downloads/Cartography/public/output")

# Constraint patterns
CONSTRAINT_PATTERNS = {
    'goal': r'\b(goal|objective|want to|trying to|aim|looking for|need to find)\b',
    'hard_constraint': r'\b(must|require|have to|only|cannot|no more than|at least|maximum|minimum|deadline|budget)\b',
    'soft_constraint': r'\b(prefer|rather|ideally|if possible|would like|hope|should)\b',
    'negation': r'\b(no |don\'t|do not|won\'t|never|avoid|exclude)\b',
}


def analyze_conversation(data: dict) -> dict:
    """Analyze a single conversation."""
    messages = data.get('messages', [])
    user_messages = [m for m in messages if m.get('role') == 'user']
    assistant_messages = [m for m in messages if m.get('role') == 'assistant']

    # Combine user text for constraint detection
    user_text = ' '.join(m.get('content', '') for m in user_messages).lower()

    # Detect constraint types
    constraints_found = {}
    for ctype, pattern in CONSTRAINT_PATTERNS.items():
        matches = re.findall(pattern, user_text)
        if matches:
            constraints_found[ctype] = len(matches)

    # Check for restatements (same phrase appears multiple times)
    restatements = 0
    phrases = set()
    for m in user_messages:
        content = m.get('content', '').lower()
        # Look for repeated constraint phrases
        for pattern in [r'(no .{5,30})', r'(must .{5,30})', r'(only .{5,30})']:
            found = re.findall(pattern, content)
            for phrase in found:
                if phrase in phrases:
                    restatements += 1
                phrases.add(phrase)

    # Extract existing classification if present
    classification = data.get('classification', {})
    human_role = classification.get('humanRole', {}).get('distribution', {})

    return {
        'id': data.get('id', 'unknown'),
        'source': infer_source(data.get('id', '')),
        'total_messages': len(messages),
        'user_turns': len(user_messages),
        'assistant_turns': len(assistant_messages),
        'constraints_found': constraints_found,
        'total_constraints': sum(constraints_found.values()),
        'has_goal': 'goal' in constraints_found,
        'has_hard_constraint': 'hard_constraint' in constraints_found,
        'restatement_count': restatements,
        'human_role_distribution': human_role,
        'is_task_oriented': sum(constraints_found.values()) >= 3,
        'qualifies_for_study': len(messages) >= 10 and sum(constraints_found.values()) >= 2,
    }


def infer_source(conv_id: str) -> str:
    """Infer data source from ID."""
    if 'wildchat' in conv_id.lower():
        return 'WildChat'
    elif 'chatbot_arena' in conv_id.lower() or 'lmsys' in conv_id.lower():
        return 'ChatbotArena'
    elif 'oasst' in conv_id.lower():
        return 'OASST'
    else:
        return 'Other'


def main():
    print("=" * 70)
    print("Analyzing existing conversation data")
    print("=" * 70)

    files = list(DATA_DIR.glob("*.json"))
    print(f"Found {len(files)} JSON files\n")

    results = []
    source_counts = defaultdict(int)
    qualifying = []

    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
            analysis = analyze_conversation(data)
            results.append(analysis)
            source_counts[analysis['source']] += 1

            if analysis['qualifies_for_study']:
                qualifying.append(analysis)
        except Exception as e:
            pass  # Skip malformed files

    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    print(f"\n### Source Distribution")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")

    print(f"\n### Turn Distribution")
    turn_buckets = defaultdict(int)
    for r in results:
        bucket = (r['total_messages'] // 4) * 4
        turn_buckets[f"{bucket}-{bucket+3}"] += 1
    for bucket in sorted(turn_buckets.keys(), key=lambda x: int(x.split('-')[0])):
        print(f"  {bucket} messages: {turn_buckets[bucket]}")

    print(f"\n### Constraint Detection")
    with_goals = sum(1 for r in results if r['has_goal'])
    with_hard = sum(1 for r in results if r['has_hard_constraint'])
    task_oriented = sum(1 for r in results if r['is_task_oriented'])
    print(f"  With goals: {with_goals} ({100*with_goals/len(results):.1f}%)")
    print(f"  With hard constraints: {with_hard} ({100*with_hard/len(results):.1f}%)")
    print(f"  Task-oriented (3+ constraints): {task_oriented} ({100*task_oriented/len(results):.1f}%)")

    print(f"\n### Study Qualification (10+ messages, 2+ constraints)")
    print(f"  Qualifying: {len(qualifying)}")
    print(f"  Target: 562")
    print(f"  Gap: {562 - len(qualifying)}")

    # Source breakdown for qualifying
    print(f"\n### Qualifying by Source")
    qual_sources = defaultdict(int)
    for q in qualifying:
        qual_sources[q['source']] += 1
    for source, count in sorted(qual_sources.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")

    # Output for paper
    print("\n" + "=" * 70)
    print("FOR PAPER (Section 4.1)")
    print("=" * 70)
    print(f"""
| Source | Filtered N | Description |
|--------|------------|-------------|
| WildChat | {qual_sources.get('WildChat', 0)} | Real-world GPT interactions |
| Chatbot Arena | {qual_sources.get('ChatbotArena', 0)} | Comparative evaluation sessions |
| OASST | {qual_sources.get('OASST', 0)} | Open Assistant power users |
| **Total** | **{len(qualifying)}** | |
""")

    # Save qualifying IDs
    output_file = DATA_DIR.parent / "qualifying_ids.json"
    with open(output_file, 'w') as f:
        json.dump([q['id'] for q in qualifying], f, indent=2)
    print(f"\nSaved qualifying IDs to: {output_file}")


if __name__ == "__main__":
    main()
