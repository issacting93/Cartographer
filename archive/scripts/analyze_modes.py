#!/usr/bin/env python3
"""
Plain-language analysis of: does the AI do what the user asked it to do?

Not about specific instructions like "use Python" — about the *kind* of help.
Did the user want advice? Did they get a lecture instead?
Did they want to explore? Did the AI just start executing?

METHODOLOGY CAVEAT:
The mode detector classifies AI responses primarily by text length:
  >800 chars → EXECUTOR (0.85 confidence)
  >300 chars → EXECUTOR (0.60 confidence)
  default    → EXECUTOR (0.50 confidence)
This means ~95% of AI responses are classified as EXECUTOR regardless
of actual content. The mismatch rate is therefore an artifact of response
length, NOT a measure of intent alignment. These results should be
interpreted with extreme caution.
"""
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"

# Human-readable translations
MODE_LABELS = {
    'LISTENER': 'exploring / thinking out loud',
    'ADVISOR': 'asking for advice',
    'EXECUTOR': 'asking for a specific output',
}

VIOLATION_LABELS = {
    'PREMATURE_EXECUTION': 'User wanted advice → AI just did the task',
    'UNSOLICITED_ADVICE': 'User wanted to explore → AI gave unsolicited advice',
    'EXECUTION_AVOIDANCE': 'User wanted output → AI gave advice instead',
}


def iter_valid_graphs():
    for f in sorted(GRAPHS_DIR.glob('*.json')):
        if '-error' in f.stem:
            continue
        yield f


def analyze():
    total_exchanges = 0
    mismatches = 0
    mismatch_types = Counter()
    matched_types = Counter()

    # Track per-conversation patterns
    convs_with_modes = 0
    convs_with_mismatch = 0
    mismatch_per_conv = []

    # Real examples
    examples = {
        'PREMATURE_EXECUTION': [],
        'UNSOLICITED_ADVICE': [],
        'EXECUTION_AVOIDANCE': [],
    }

    for f in iter_valid_graphs():
        with open(f) as fh:
            g = json.load(fh)

        nodes = g.get('nodes', [])
        conv_node = next((n for n in nodes if n.get('node_type') == 'Conversation'), None)
        conv_id = conv_node.get('conv_id', f.stem) if conv_node else f.stem

        modes = [n for n in nodes if n.get('node_type') == 'InteractionMode']
        if not modes:
            continue

        convs_with_modes += 1
        conv_mismatches = 0

        for mode in modes:
            user_wanted = mode.get('user_requested', '')
            ai_did = mode.get('ai_enacted', '')
            is_mismatch = mode.get('is_violation') in (True, 'True', 'true')
            vtype = mode.get('violation_type', '')

            if not user_wanted or not ai_did:
                continue

            total_exchanges += 1

            if is_mismatch and vtype:
                mismatches += 1
                conv_mismatches += 1
                mismatch_types[vtype] += 1

                # Collect examples
                turn_idx = mode.get('turn_index', '?')
                turns = [n for n in nodes if n.get('node_type') == 'Turn' and n.get('turn_index') == turn_idx]
                preview = ''
                if turns:
                    preview = turns[0].get('content_preview', '')[:100]

                if len(examples.get(vtype, [])) < 3:
                    examples[vtype].append({
                        'conv_id': conv_id,
                        'turn': turn_idx,
                        'user_wanted': MODE_LABELS.get(user_wanted, user_wanted),
                        'ai_did': MODE_LABELS.get(ai_did, ai_did),
                        'preview': preview,
                    })
            else:
                pair = f"{user_wanted}→{ai_did}"
                matched_types[pair] += 1

        if conv_mismatches > 0:
            convs_with_mismatch += 1
        mismatch_per_conv.append(conv_mismatches)

    # ===== PRINT =====
    print("=" * 70)
    print("DOES THE AI DO WHAT THE USER ASKED?")
    print("=" * 70)
    print()
    print("*** CAVEAT: Mode detection classifies AI as EXECUTOR ~95% of the")
    print("*** time based on response length. These mismatch rates are likely")
    print("*** artifacts of the classification method, not real intent gaps.")
    print()
    print(f"We analyzed {total_exchanges:,} exchanges across {convs_with_modes:,} conversations.")
    print(f"Each exchange: the user signals what kind of help they want,")
    print(f"and we check whether the AI responds in kind.")
    print()

    pct_mismatch = mismatches / total_exchanges * 100 if total_exchanges > 0 else 0
    pct_match = 100 - pct_mismatch
    print(f"  AI responded appropriately: {total_exchanges - mismatches:,}/{total_exchanges:,} ({pct_match:.0f}%)")
    print(f"  AI responded inappropriately: {mismatches:,}/{total_exchanges:,} ({pct_mismatch:.0f}%)")
    print()

    print("-" * 70)
    print("WHAT GOES WRONG?")
    print("-" * 70)
    print()
    for vtype, count in mismatch_types.most_common():
        pct = count / mismatches * 100 if mismatches > 0 else 0
        label = VIOLATION_LABELS.get(vtype, vtype)
        print(f"  {label}")
        print(f"    {count:,} times ({pct:.0f}% of mismatches)")
        print()
        for ex in examples.get(vtype, []):
            print(f"    Example [{ex['conv_id']}, turn {ex['turn']}]:")
            print(f"      User wanted: {ex['user_wanted']}")
            print(f"      AI did: {ex['ai_did']}")
            if ex['preview']:
                print(f"      Context: \"{ex['preview']}...\"")
            print()

    print("-" * 70)
    print("HOW COMMON IS THIS?")
    print("-" * 70)
    print()
    print(f"  Conversations with at least one mismatch: "
          f"{convs_with_mismatch}/{convs_with_modes} ({convs_with_mismatch/convs_with_modes*100:.0f}%)")
    print()

    # What users most commonly want
    print("-" * 70)
    print("WHAT DO USERS WANT vs WHAT DO THEY GET?")
    print("-" * 70)
    print()
    print("  Most common appropriate pairings:")
    for pair, count in matched_types.most_common(5):
        wanted, got = pair.split('→')
        print(f"    User wanted {MODE_LABELS.get(wanted, wanted)}, "
              f"AI did {MODE_LABELS.get(got, got)}: {count:,} times")
    print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"  In {pct_mismatch:.0f}% of exchanges, the AI responds with the wrong kind of help.")
    top_mismatch = mismatch_types.most_common(1)
    if top_mismatch:
        label = VIOLATION_LABELS.get(top_mismatch[0][0], top_mismatch[0][0])
        pct = top_mismatch[0][1] / mismatches * 100
        print(f"  The most common problem ({pct:.0f}%): {label}")
    print()

    # Save
    output = {
        'total_exchanges': total_exchanges,
        'mismatches': mismatches,
        'pct_mismatch': round(pct_mismatch, 1),
        'mismatch_types': {
            k: {'count': v, 'pct': round(v / mismatches * 100, 1), 'description': VIOLATION_LABELS.get(k, k)}
            for k, v in mismatch_types.most_common()
        },
        'conversations_analyzed': convs_with_modes,
        'conversations_with_mismatch': convs_with_mismatch,
    }

    out_path = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "mode_analysis.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == '__main__':
    analyze()
