#!/usr/bin/env python3
"""
Plain-language analysis of what happens to user instructions in LLM conversations.

No jargon. Just: what did the user ask for, did the AI follow it, and what happened next?
"""
import json
import statistics
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"


def iter_valid_graphs():
    for f in sorted(GRAPHS_DIR.glob('*.json')):
        if '-error' in f.stem:
            continue
        yield f


def analyze():
    # Per-conversation tracking
    conversations_with_instructions = []  # list of dicts
    conversations_without = 0

    for f in iter_valid_graphs():
        with open(f) as fh:
            g = json.load(fh)

        nodes = g.get('nodes', [])
        links = g.get('links', [])

        # Get conversation metadata
        conv_node = next((n for n in nodes if n.get('node_type') == 'Conversation'), None)
        conv_id = conv_node.get('conv_id', f.stem) if conv_node else f.stem

        # Get instructions (Constraint nodes)
        instructions = [n for n in nodes if n.get('node_type') == 'Constraint']
        if not instructions:
            conversations_without += 1
            continue

        # Get turns
        turns = sorted(
            [n for n in nodes if n.get('node_type') == 'Turn'],
            key=lambda x: x.get('turn_index', 0)
        )
        total_turns = len(turns)

        # Get violation events for task constraints (not mode violations)
        task_violations = [
            n for n in nodes
            if n.get('node_type') == 'ViolationEvent'
            and n.get('violation_type') == 'constraint_violation'
        ]

        # Get moves via links
        turn_to_moves = {t.get('id'): [] for t in turns}
        move_dict = {n.get('id'): n for n in nodes if n.get('node_type') == 'Move'}
        for link in links:
            if link.get('edge_type') == 'HAS_MOVE':
                src = link.get('source')
                if src in turn_to_moves:
                    turn_to_moves[src].append(link.get('target'))

        # Count repair attempts (REPAIR_INITIATE moves)
        repair_attempts = 0
        for turn in turns:
            m_ids = turn_to_moves.get(turn.get('id'), [])
            for m_id in m_ids:
                m = move_dict.get(m_id, {})
                if m.get('move_type') in ('REPAIR_INITIATE', 'ESCALATE'):
                    repair_attempts += 1

        # Per-instruction analysis
        instruction_outcomes = []
        for inst in instructions:
            text = inst.get('text', '')
            state = inst.get('current_state', '')
            introduced = inst.get('introduced_at', 0)
            times_violated = inst.get('times_violated', 0)
            times_repaired = inst.get('times_repaired', 0)

            # Find when it was first ignored
            inst_violations = [
                v for v in task_violations
                if v.get('constraint_id') == inst.get('constraint_id')
            ]
            if inst_violations:
                first_violation_turn = min(v.get('turn_index', 999) for v in inst_violations)
                turns_until_ignored = first_violation_turn - introduced
            else:
                first_violation_turn = None
                turns_until_ignored = None

            was_ignored = state in ('VIOLATED', 'ABANDONED') or times_violated > 0
            was_corrected = times_repaired > 0

            # Determine confidence level for "followed" instructions
            # Check state_history: was this constraint ever ACTIVE?
            history = inst.get('state_history', [])
            states_in_history = [
                entry[1] if isinstance(entry, (list, tuple)) and len(entry) >= 2 else None
                for entry in history
            ]
            was_acknowledged = 'ACTIVE' in states_in_history

            if was_ignored:
                outcome = 'violated'
            elif was_acknowledged:
                outcome = 'followed'
            else:
                outcome = 'ambiguous'  # never violated, never acknowledged

            instruction_outcomes.append({
                'text': text[:120],
                'was_ignored': was_ignored,
                'was_corrected': was_corrected,
                'was_acknowledged': was_acknowledged,
                'outcome': outcome,
                'turns_until_ignored': turns_until_ignored,
                'state': state,
            })

        conversations_with_instructions.append({
            'conv_id': conv_id,
            'n_instructions': len(instructions),
            'total_turns': total_turns,
            'n_violations': len(task_violations),
            'repair_attempts': repair_attempts,
            'instruction_outcomes': instruction_outcomes,
        })

    # ===== AGGREGATE ANALYSIS =====

    total_instructions = sum(c['n_instructions'] for c in conversations_with_instructions)
    ignored_instructions = sum(
        sum(1 for i in c['instruction_outcomes'] if i['outcome'] == 'violated')
        for c in conversations_with_instructions
    )
    followed_instructions = sum(
        sum(1 for i in c['instruction_outcomes'] if i['outcome'] == 'followed')
        for c in conversations_with_instructions
    )
    ambiguous_instructions = sum(
        sum(1 for i in c['instruction_outcomes'] if i['outcome'] == 'ambiguous')
        for c in conversations_with_instructions
    )
    corrected_instructions = sum(
        sum(1 for i in c['instruction_outcomes'] if i['was_corrected'])
        for c in conversations_with_instructions
    )

    # Turns until ignored
    turns_until = [
        i['turns_until_ignored']
        for c in conversations_with_instructions
        for i in c['instruction_outcomes']
        if i['turns_until_ignored'] is not None
    ]

    # Immediate ignores (turn 0 = AI's first response)
    immediate_ignores = sum(1 for t in turns_until if t == 0)

    # Conversations where user tried to correct
    convs_with_correction = sum(
        1 for c in conversations_with_instructions if c['repair_attempts'] > 0
    )
    convs_total = len(conversations_with_instructions)

    # Total violation events vs successful corrections
    total_violation_events = sum(c['n_violations'] for c in conversations_with_instructions)

    # Turn distribution
    turn_dist = Counter(turns_until)

    # Get real examples
    examples_ignored_immediately = []
    examples_ignored_later = []
    examples_followed = []

    for c in conversations_with_instructions:
        for i in c['instruction_outcomes']:
            entry = {'conv_id': c['conv_id'], 'instruction': i['text'], 'state': i['state']}
            if i['was_ignored'] and i['turns_until_ignored'] == 0:
                if len(examples_ignored_immediately) < 5:
                    examples_ignored_immediately.append(entry)
            elif i['was_ignored'] and i['turns_until_ignored'] is not None and i['turns_until_ignored'] > 0:
                entry['turns'] = i['turns_until_ignored']
                if len(examples_ignored_later) < 5:
                    examples_ignored_later.append(entry)
            elif not i['was_ignored']:
                if len(examples_followed) < 5:
                    examples_followed.append(entry)

    # ===== PRINT PLAIN-LANGUAGE REPORT =====

    print("=" * 70)
    print("WHAT HAPPENS WHEN USERS GIVE INSTRUCTIONS TO LLMs?")
    print("=" * 70)
    print()
    print(f"We looked at {convs_total + conversations_without:,} conversations.")
    print(f"{convs_total} of them contained explicit instructions from the user.")
    print(f"Those {convs_total} conversations contained {total_instructions} instructions total.")
    print()

    print("-" * 70)
    print("1. DID THE AI FOLLOW THE INSTRUCTIONS?")
    print("-" * 70)
    print()
    pct_ignored = ignored_instructions / total_instructions * 100
    pct_followed = followed_instructions / total_instructions * 100
    pct_ambiguous = ambiguous_instructions / total_instructions * 100
    print(f"  Violated:   {ignored_instructions}/{total_instructions} ({pct_ignored:.0f}%)")
    print(f"  Followed:   {followed_instructions}/{total_instructions} ({pct_followed:.0f}%)")
    print(f"  Ambiguous:  {ambiguous_instructions}/{total_instructions} ({pct_ambiguous:.0f}%)")
    print()
    print(f"  'Followed' = the AI acknowledged the instruction AND never violated it")
    print(f"  'Ambiguous' = never violated, but never acknowledged either")
    print(f"  (The AI may have coincidentally complied without tracking the instruction)")
    print()

    print("-" * 70)
    print("2. HOW QUICKLY WERE INSTRUCTIONS IGNORED?")
    print("-" * 70)
    print()
    if turns_until:
        print(f"  Of the {len(turns_until)} ignored instructions:")
        print(f"  - {immediate_ignores} ({immediate_ignores/len(turns_until)*100:.0f}%) were ignored in the AI's FIRST response")
        print(f"  - Median: the AI ignored the instruction after {statistics.median(turns_until):.0f} turn(s)")
        print(f"  - Mean: {statistics.mean(turns_until):.1f} turns")
        print()
        print("  Distribution (turns until ignored):")
        for turn_n in sorted(turn_dist.keys()):
            count = turn_dist[turn_n]
            bar = "#" * min(count, 60)
            pct = count / len(turns_until) * 100
            print(f"    Turn {turn_n:2d}: {bar} {count} ({pct:.0f}%)")
            if turn_n > 15:
                remaining = sum(turn_dist[k] for k in turn_dist if k > turn_n)
                if remaining > 0:
                    print(f"    Turn {turn_n+1}+: ... {remaining} more")
                break
    print()

    print("-" * 70)
    print("3. DID USERS TRY TO CORRECT THE AI?")
    print("-" * 70)
    print()
    print(f"  Conversations where the user tried to correct the AI: "
          f"{convs_with_correction}/{convs_total} ({convs_with_correction/convs_total*100:.1f}%)")
    print(f"  Conversations where the user did NOT try: "
          f"{convs_total - convs_with_correction}/{convs_total} ({(convs_total - convs_with_correction)/convs_total*100:.1f}%)")
    print()

    print("-" * 70)
    print("4. WHEN USERS DID TRY TO CORRECT, DID IT WORK?")
    print("-" * 70)
    print()
    print(f"  Total times the AI ignored an instruction: {total_violation_events}")
    print(f"  Times a correction was successful: {corrected_instructions}")
    if total_violation_events > 0:
        print(f"  Success rate: {corrected_instructions}/{total_violation_events} "
              f"({corrected_instructions/total_violation_events*100:.1f}%)")
    print()

    print("-" * 70)
    print("5. REAL EXAMPLES")
    print("-" * 70)
    print()
    if examples_ignored_immediately:
        print("  Instructions ignored on the FIRST response:")
        for ex in examples_ignored_immediately:
            print(f"    [{ex['conv_id']}] \"{ex['instruction']}\"")
        print()
    if examples_ignored_later:
        print("  Instructions followed briefly, then ignored:")
        for ex in examples_ignored_later:
            print(f"    [{ex['conv_id']}] \"{ex['instruction']}\" (followed for {ex['turns']} turn(s))")
        print()
    if examples_followed:
        print("  Instructions that WERE followed throughout:")
        for ex in examples_followed:
            print(f"    [{ex['conv_id']}] \"{ex['instruction']}\"")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"  When users give LLMs explicit instructions:")
    print(f"  - {pct_ignored:.0f}% are violated")
    print(f"  - {pct_followed:.0f}% are acknowledged and followed")
    print(f"  - {pct_ambiguous:.0f}% have ambiguous outcomes (never violated, never acknowledged)")
    if turns_until:
        print(f"  - {immediate_ignores/len(turns_until)*100:.0f}% of violations happen on the first response")
    print(f"  - Only {convs_with_correction/convs_total*100:.0f}% of users even try to correct the AI")
    if total_violation_events > 0:
        print(f"  - When they do try, it works {corrected_instructions/total_violation_events*100:.1f}% of the time")
    print()

    # Save machine-readable version
    output = {
        'total_conversations': convs_total + conversations_without,
        'conversations_with_instructions': convs_total,
        'total_instructions': total_instructions,
        'instructions_violated': ignored_instructions,
        'instructions_followed': followed_instructions,
        'instructions_ambiguous': ambiguous_instructions,
        'pct_violated': round(pct_ignored, 1),
        'pct_followed': round(pct_followed, 1),
        'pct_ambiguous': round(pct_ambiguous, 1),
        'immediate_ignores': immediate_ignores,
        'pct_immediate': round(immediate_ignores / len(turns_until) * 100, 1) if turns_until else 0,
        'median_turns_until_ignored': statistics.median(turns_until) if turns_until else None,
        'mean_turns_until_ignored': round(statistics.mean(turns_until), 2) if turns_until else None,
        'users_who_tried_to_correct': convs_with_correction,
        'pct_tried_to_correct': round(convs_with_correction / convs_total * 100, 1),
        'total_times_ignored': total_violation_events,
        'successful_corrections': corrected_instructions,
        'correction_success_rate': round(corrected_instructions / total_violation_events * 100, 2) if total_violation_events > 0 else 0,
        'turns_until_ignored_distribution': {str(k): v for k, v in sorted(turn_dist.items())},
    }

    out_path = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "instruction_analysis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == '__main__':
    analyze()
