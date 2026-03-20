#!/usr/bin/env python3
"""
PAD Scoring (v2)
=================
Generate PAD (Pleasure-Arousal-Dominance) values for each message using GPT-4o-mini.
Reads from data/v2_unified/conversations/ and enriches in-place.
Skips conversations that already have PAD data.

Usage:
    python3 scripts/generate_pad.py [--limit N] [--force] [--dry-run]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Load .env
def load_env_file():
    for env_path in [Path(".env"), Path(__file__).parent.parent / ".env"]:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        if line.startswith("export "):
                            line = line[7:]
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            os.environ[parts[0].strip()] = parts[1].strip().strip('"').strip("'")
            break

load_env_file()

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed. Run: pip install openai")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONVERSATIONS_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# PAD Generation
# ---------------------------------------------------------------------------

def generate_pad_batch(client: OpenAI, conversation: Dict) -> Optional[List[Dict]]:
    """Generate PAD scores for all messages in a conversation."""
    messages = conversation.get('messages', [])
    if not messages:
        return None

    classification = conversation.get('classification', {})
    tone = classification.get('emotionalTone', {}).get('category', 'neutral') if classification else 'neutral'
    style = classification.get('engagementStyle', {}).get('category', 'reactive') if classification else 'reactive'

    formatted_history = ""
    for idx, msg in enumerate(messages):
        role = msg.get('role', 'user').upper()
        content = msg.get('content', '')
        formatted_history += f"[{idx}] {role}: {content}\n"

    system_prompt = f"""You are an expert behavioral psychologist specializing in the PAD (Pleasure-Arousal-Dominance) emotional model.
Analyze the following conversation and provide PAD scores (0.0 to 1.0) for EVERY message.

CONTEXT:
Overall Tone: {tone}
Engagement Style: {style}

DIMENSIONS:
- Pleasure (P): Valence. 0=Unhappy/Frustrated/Negative, 1=Happy/Satisfied/Positive.
- Arousal (A): Activation. 0=Sleepy/Calm/Passive, 1=Excited/Agitated/Activated.
- Dominance (D): Influence. 0=Submissive/Led/Passive, 1=Dominant/Leading/Assertive.

CRITICAL DETECTION RULES:

1. SARCASM/FRUSTRATION:
   - Markers: "yeah cool", "seriously?", "ugh", "come on"
   - Pattern: Lower pleasure (0.2-0.4), Higher arousal (0.6-0.8), Maintain dominance (0.5-0.7)

2. APOLOGIES:
   - Markers: "sorry", "apologize", "my mistake"
   - Pattern: Lower pleasure (0.3-0.5), Moderate arousal (0.4-0.6), Lower dominance (0.2-0.4)

3. TASK COMPLETION/SUCCESS:
   - Markers: "perfect", "thanks", "that works", "exactly"
   - Pattern: Higher pleasure (0.7-0.9), Moderate arousal (0.4-0.6), Maintain dominance (0.5-0.7)

4. EMOTIONAL VARIATION REQUIREMENT:
   - For conversations with 5+ messages, ensure emotional intensity range >= 0.2
   - At least 30% of messages should have unique PAD combinations
   - Do NOT make all messages have similar PAD values

CONTEXT AWARENESS:
- Consider the conversation flow and previous messages
- Track emotional arcs: frustration -> apology -> resolution
- Detect topic shifts and reflect in arousal

IMPORTANT:
- You MUST provide exactly ONE PAD score for EACH message.
- The array length must match the message count exactly ({len(messages)} messages).

OUTPUT FORMAT:
Return a JSON object with a "pad_scores" array containing exactly {len(messages)} objects.
Each object has "p", "a", and "d" fields.
"""

    user_prompt = f"Analyze these {len(messages)} messages and return the PAD array:\n\n{formatted_history}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        raw_output = json.loads(response.choices[0].message.content)

        if isinstance(raw_output, dict) and 'pad_scores' in raw_output:
            pad_array = raw_output['pad_scores']
        elif isinstance(raw_output, list):
            pad_array = raw_output
        else:
            pad_array = None
            for key, value in raw_output.items():
                if isinstance(value, list):
                    pad_array = value
                    break
            if pad_array is None:
                return None

        # Fix length mismatch
        if len(pad_array) < len(messages):
            last_pad = pad_array[-1] if pad_array else {"p": 0.5, "a": 0.5, "d": 0.5}
            pad_array.extend([last_pad.copy() for _ in range(len(messages) - len(pad_array))])
        elif len(pad_array) > len(messages):
            pad_array = pad_array[:len(messages)]

        return pad_array

    except Exception as e:
        print(f"  Error: {e}")
        return None


def apply_pad(conversation: Dict, pad_scores: List[Dict]) -> Dict:
    """Apply PAD values and calculate emotionalIntensity."""
    for i, msg in enumerate(conversation['messages']):
        if i < len(pad_scores):
            pad_entry = pad_scores[i]
            p = max(0.0, min(1.0, float(pad_entry.get('p', pad_entry.get('pleasure', 0.5)))))
            a = max(0.0, min(1.0, float(pad_entry.get('a', pad_entry.get('arousal', 0.5)))))
            d = max(0.0, min(1.0, float(pad_entry.get('d', pad_entry.get('dominance', 0.5)))))

            intensity = round(((1 - p) * 0.6) + (a * 0.4), 3)

            msg['pad'] = {
                "pleasure": round(p, 3),
                "arousal": round(a, 3),
                "dominance": round(d, 3),
                "emotionalIntensity": intensity
            }
    return conversation


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate PAD scores")
    parser.add_argument('--limit', type=int, help="Process only first N without PAD")
    parser.add_argument('--force', action='store_true', help="Recalculate even if PAD exists")
    parser.add_argument('--dry-run', action='store_true', help="Preview without API calls")
    parser.add_argument('--model', default=MODEL, help=f"Model to use (default: {MODEL})")
    parser.add_argument('--source-dir', type=Path, default=CONVERSATIONS_DIR, help="Directory containing conversation JSONs")
    args = parser.parse_args()

    conv_files = sorted(args.source_dir.glob('*.json'))
    to_process = []

    for fpath in conv_files:
        with open(fpath) as f:
            data = json.load(f)
        if not args.force and data.get('messages', [{}])[0].get('pad'):
            continue
        to_process.append(fpath)

    print(f"Source directory: {args.source_dir}")
    print(f"Total conversations: {len(conv_files)}")
    print(f"Need PAD: {len(to_process)}")

    if args.limit:
        to_process = to_process[:args.limit]

    if args.dry_run:
        print(f"\nDRY RUN - would process {len(to_process)} conversations")
        return

    if not to_process:
        print("Nothing to process!")
        return

    # Initialize client
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if args.model.startswith("claude") and anthropic_key:
        sys.path.append(str(PROJECT_ROOT / "scripts"))
        from atlas.anthropic_adapter import AnthropicOpenAIAdapter
        client = AnthropicOpenAIAdapter(api_key=anthropic_key)
        print(f"Using Anthropic model: {args.model}")
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        print(f"Using OpenAI model: {args.model}")
    else:
        print("Error: No valid API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        sys.exit(1)

    print(f"\nGenerating PAD for {len(to_process)} conversations with {MODEL}...")
    print(f"Estimated cost: ~${len(to_process) * 0.001:.2f}\n")

    success = 0
    errors = 0

    for i, fpath in enumerate(to_process):
        try:
            with open(fpath) as f:
                data = json.load(f)

            pad_scores = generate_pad_batch(client, data)
            if pad_scores is None:
                errors += 1
                continue

            data = apply_pad(data, pad_scores)

            with open(fpath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            success += 1
            pct = (i + 1) / len(to_process) * 100
            print(f"\r  [{i+1}/{len(to_process)}] ({pct:.0f}%) {fpath.name}", end="", flush=True)

        except Exception as e:
            errors += 1
            print(f"\n  ERROR: {fpath.name}: {e}")

    print(f"\n\nDone! Success: {success}, Errors: {errors}")


if __name__ == '__main__':
    main()
