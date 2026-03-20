#!/usr/bin/env python3
"""
SRT Role Classification (v2)
=============================
Classifies conversations using Social Role Theory framework via GPT-4o.
12-role taxonomy (6 human + 6 AI) with 8-dimension classification.

Reads from data/v2_unified/conversations/ and enriches in-place.
Skips conversations that already have classification data.

Usage:
    python3 scripts/classify_roles_srt.py [--limit N] [--force] [--model MODEL]
    python3 scripts/classify_roles_srt.py --dry-run
"""

import json
import sys
import time
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Load .env file
def load_env_file():
    """Load environment variables from .env file."""
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
                            key = parts[0].strip()
                            value = parts[1].strip().strip('"').strip("'")
                            os.environ[key] = value
            break

load_env_file()

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONVERSATIONS_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
FEW_SHOT_FILE = PROJECT_ROOT / "scripts" / "few-shot-examples-social-role-theory.json"

# ---------------------------------------------------------------------------
# Prompt (from v1 classifier-openai-social-role-theory.py)
# ---------------------------------------------------------------------------

CLASSIFICATION_PROMPT_TEMPLATE = """You are an academic conversation coder analyzing human-AI dialogues for research on conversational dynamics using Social Role Theory.

## RULES
- Roles are interactional configurations observable in text, not identities or relationships.
- Do NOT infer private intent, diagnosis, or internal emotion beyond explicit wording.
- Use ONLY evidence from the provided conversation.
- Provide short evidence quotes (<= 20 words each).
- If confidence < 0.6, you MUST name one plausible alternative category.
- Evidence quotes must be EXACT excerpts from the conversation.

## TASK
Classify the conversation across 10 dimensions:
- Dimensions 1-8: choose ONE category
- Dimensions 9-10: output a PROBABILITY DISTRIBUTION over roles (values must sum to 1.0)

## CONFIDENCE CALIBRATION
- 0.9-1.0: Unambiguous, clear signals, no reasonable alternative
- 0.7-0.9: Strong fit, minor ambiguity or mixed signals
- 0.5-0.7: Moderate fit, could reasonably be another category
- 0.3-0.5: Weak fit, defaulting due to lack of better option / short conversation
- <0.3: Highly uncertain, conversation may be too short or ambiguous

## EDGE CASES
- If conversation is 1-2 turns: set confidence <= 0.5 for most dimensions
- If you cannot justify with quotes: set confidence <= 0.5
- Set "abstain": true if too short/ambiguous to meaningfully classify (still provide best-effort)

---

## SOCIAL ROLE THEORY FRAMEWORK

Roles are organized along two dimensions:

1. **Instrumental <-> Expressive**
   - **Instrumental**: Task-oriented, goal-directed, functional
   - **Expressive**: Relationship-oriented, emotional, communal

2. **Authority Level**
   - **High Authority**: Asserts knowledge/control
   - **Low Authority**: Seeks information or guides
   - **Equal Authority**: Collaborative partnership

### Key Distinctions:

**Learning-Facilitator (Instrumental) vs Social-Facilitator (Expressive):**
- **Learning-Facilitator**: Scaffolds understanding, guides discovery (task-oriented, educational)
- **Social-Facilitator**: Maintains conversation, builds rapport (relationship-oriented, casual)

**Provider (Human, Instrumental, Low Authority) vs Expert-System (AI, Instrumental, High Authority):**
- **Provider** (Human): Seeks information (asks questions, low authority)
- **Expert-System** (AI): Provides information (gives answers, high authority)

---

## FEW-SHOT EXAMPLES

{few_shot_examples}

---

## DIMENSION DEFINITIONS

### 1. INTERACTION PATTERN
| Category | Definition |
|----------|------------|
| question-answer | One party primarily asks questions, other provides answers |
| storytelling | Extended narrative, explanation, or sequential account |
| advisory | Guidance, recommendations, or counsel being given |
| debate | Argumentation, persuasion, or position defense |
| collaborative | Joint problem-solving, brainstorming, or co-creation |
| casual-chat | Social exchange without specific instrumental goal |
| philosophical-dialogue | Meaning-making, worldview exchange, existential exploration |
| artistic-expression | Creative sharing (poetry, lyrics, art description) |

### 2. POWER DYNAMICS
| Category | Definition |
|----------|------------|
| human-led | Human sets agenda, asks most questions, steers topics |
| ai-led | AI drives conversation through questions or topic shifts |
| balanced | Roughly equal contribution to direction |
| alternating | Control shifts noticeably between parties |

### 3. EMOTIONAL TONE
| Category | Definition |
|----------|------------|
| supportive | Warm, encouraging, affirming |
| playful | Light, humorous, fun |
| serious | Grave, weighty, consequential |
| empathetic | Understanding, compassionate, validating feelings |
| professional | Formal, business-like, task-focused |
| neutral | No strong emotional coloring |

### 4. ENGAGEMENT STYLE
| Category | Definition |
|----------|------------|
| questioning | Frequent questions driving exploration |
| challenging | Pushback, critique, or devil's advocate |
| exploring | Open-ended wondering, brainstorming |
| affirming | Agreement, validation, building on ideas |
| reactive | Responding without strong direction |
| directive-iterative | Commands with iterative refinement cycles |

### 5. KNOWLEDGE EXCHANGE
| Category | Definition |
|----------|------------|
| personal-sharing | Private experiences, feelings, life details |
| skill-sharing | How-to knowledge, techniques, methods |
| opinion-exchange | Views, beliefs, interpretations |
| factual-info | Data, facts, definitions, specifications |
| experience-sharing | Narratives about learning or doing something |
| meaning-making | Philosophical exploration, worldview construction |

### 6. CONVERSATION PURPOSE
| Category | Definition |
|----------|------------|
| information-seeking | Obtaining specific knowledge or answers |
| problem-solving | Resolving an issue or challenge |
| entertainment | Fun, amusement, passing time |
| relationship-building | Social bonding, rapport, connection |
| self-expression | Processing thoughts, venting, journaling |
| emotional-processing | Working through feelings despite lack of solutions |
| collaborative-refinement | Iterative improvement through feedback |
| capability-exploration | Testing AI abilities, probing limitations |

### 7. TOPIC DEPTH
| Category | Definition |
|----------|------------|
| surface | Brief, shallow, or introductory |
| moderate | Some exploration but not exhaustive |
| deep | Thorough, nuanced, detailed exploration |

### 8. TURN TAKING
| Category | Definition |
|----------|------------|
| user-dominant | Human messages substantially longer/more |
| assistant-dominant | AI messages substantially longer/more |
| balanced | Roughly equal message lengths |

---

### 9. HUMAN ROLE (DISTRIBUTION REQUIRED)
Output probability weights that sum to 1.0. Mixed roles are expected.

| Role | Instrumental/Expressive | Authority | Definition |
|------|----------------------|-----------|------------|
| **information-seeker** | Instrumental | Low | Requests information, asks questions to fill knowledge gaps |
| **provider** | Instrumental | Low | Seeks information from AI, asks questions expecting answers |
| **director** | Instrumental | High | Commands, specifies deliverables, controls task |
| **collaborator** | Instrumental | Equal | Co-builds, proposes alternatives, joint problem-solving |
| **social-expressor** | Expressive | Low | Personal narrative, emotional expression, sharing |
| **relational-peer** | Expressive | Equal | Equal partner, social bonding, casual conversation |

---

### 10. AI ROLE (DISTRIBUTION REQUIRED)
Output probability weights that sum to 1.0. Mixed roles are expected.

| Role | Instrumental/Expressive | Authority | Definition |
|------|----------------------|-----------|------------|
| **expert-system** | Instrumental | High | Provides direct answers, asserts epistemic authority |
| **learning-facilitator** | Instrumental | Low | Scaffolds learning, guides discovery |
| **advisor** | Instrumental | High | Prescribes actions, gives recommendations |
| **co-constructor** | Instrumental | Equal | Joint problem-solving, co-creates with user |
| **social-facilitator** | Expressive | Low | Maintains conversation flow, social bonding |
| **relational-peer** | Expressive | Equal | Equal social partner, casual conversation |

---

## OUTPUT FORMAT
Return ONLY valid JSON (no markdown fences). Role distributions must sum to 1.0.

{{
  "abstain": false,
  "interactionPattern": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "powerDynamics": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "emotionalTone": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "engagementStyle": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "knowledgeExchange": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "conversationPurpose": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "topicDepth": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "turnTaking": {{"category": "...", "confidence": 0.0, "evidence": ["..."], "rationale": "...", "alternative": null}},
  "humanRole": {{
    "distribution": {{
      "information-seeker": 0,
      "provider": 0,
      "director": 0,
      "collaborator": 0,
      "social-expressor": 0,
      "relational-peer": 0
    }},
    "confidence": 0.0,
    "evidence": [{{"role": "information-seeker", "quote": "..."}}],
    "rationale": "...",
    "alternative": null
  }},
  "aiRole": {{
    "distribution": {{
      "expert-system": 0,
      "learning-facilitator": 0,
      "advisor": 0,
      "co-constructor": 0,
      "social-facilitator": 0,
      "relational-peer": 0
    }},
    "confidence": 0.0,
    "evidence": [{{"role": "expert-system", "quote": "..."}}],
    "rationale": "...",
    "alternative": null
  }}
}}

---

## CONVERSATION TO ANALYZE

"""


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

HUMAN_ROLES = ["information-seeker", "provider", "director", "collaborator",
               "social-expressor", "relational-peer"]
AI_ROLES = ["expert-system", "learning-facilitator", "advisor", "co-constructor",
            "social-facilitator", "relational-peer"]


def normalize_dist(dist: dict) -> dict:
    """Normalize distribution to sum to 1.0."""
    total = sum(dist.values())
    if total <= 0:
        return dist
    return {k: round(v / total, 3) for k, v in dist.items()}


def format_conversation(messages: list) -> str:
    """Format messages for prompt."""
    lines = []
    for i, m in enumerate(messages, 1):
        role = "HUMAN" if m["role"] == "user" else "AI"
        lines.append(f"[{i}] {role}: {m['content']}")
    return "\n\n".join(lines)


def extract_json(text: str) -> str:
    """Extract JSON from response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def validate_classification(data: dict) -> dict:
    """Validate and fix classification output."""
    if "humanRole" in data and "distribution" in data["humanRole"]:
        dist = data["humanRole"]["distribution"]
        for role in HUMAN_ROLES:
            if role not in dist:
                dist[role] = 0.0
        dist = {k: v for k, v in dist.items() if k in HUMAN_ROLES}
        data["humanRole"]["distribution"] = normalize_dist(dist)

    if "aiRole" in data and "distribution" in data["aiRole"]:
        dist = data["aiRole"]["distribution"]
        for role in AI_ROLES:
            if role not in dist:
                dist[role] = 0.0
        dist = {k: v for k, v in dist.items() if k in AI_ROLES}
        data["aiRole"]["distribution"] = normalize_dist(dist)

    return data


def load_few_shot_examples(file_path: Path) -> str:
    """Load and format few-shot examples from JSON file."""
    if not file_path.exists():
        return "(No examples provided - using zero-shot)"

    with open(file_path) as f:
        data = json.load(f)

    if 'promptFormat' in data:
        return data['promptFormat']

    examples = data.get('examples', [])
    if not examples:
        return "(No examples provided)"

    formatted = []
    for i, ex in enumerate(examples, 1):
        transcript = ex.get('transcript', '')
        formatted.append(f"### Example {i}\n{transcript}")

    return "\n---\n\n".join(formatted)


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify_messages(client, messages: list, few_shot_examples: str,
                      model: str = "gpt-4o") -> dict:
    """Classify a single conversation."""
    formatted = format_conversation(messages)
    prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
        few_shot_examples=few_shot_examples) + formatted

    request_params = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert conversation analyst using Social Role Theory. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 3000,
    }

    response = client.chat.completions.create(**request_params)
    text = response.choices[0].message.content
    json_text = extract_json(text)
    data = json.loads(json_text)
    return validate_classification(data)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SRT Role Classification")
    parser.add_argument('--limit', type=int, help="Process only first N unclassified")
    parser.add_argument('--force', action='store_true', help="Reclassify even if already classified")
    parser.add_argument('--model', default='gpt-4o', help="OpenAI model (default: gpt-4o)")
    parser.add_argument('--delay', type=int, default=600, help="Delay between API calls in ms")
    parser.add_argument('--dry-run', action='store_true', help="Preview without making API calls")
    parser.add_argument('--source-dir', type=Path, default=CONVERSATIONS_DIR, help="Directory containing conversation JSONs")
    args = parser.parse_args()

    # Load few-shot examples
    few_shot_examples = load_few_shot_examples(FEW_SHOT_FILE)

    # Find conversations needing classification
    conv_files = sorted(args.source_dir.glob('*.json'))
    to_classify = []

    for fpath in conv_files:
        with open(fpath) as f:
            data = json.load(f)
        if not args.force and data.get('classification'):
            continue
        to_classify.append(fpath)

    print(f"Source directory: {args.source_dir}")
    print(f"Total conversations: {len(conv_files)}")
    print(f"Need classification: {len(to_classify)}")

    if args.limit:
        to_classify = to_classify[:args.limit]
        print(f"Processing first {args.limit}")

    if args.dry_run:
        print("\nDRY RUN - no API calls will be made")
        for fpath in to_classify[:10]:
            print(f"  Would classify: {fpath.name}")
        if len(to_classify) > 10:
            print(f"  ... and {len(to_classify) - 10} more")
        return

    if not to_classify:
        print("Nothing to classify!")
        return

    # Initialize client
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if args.model.startswith("claude") and anthropic_key:
        sys.path.append(str(PROJECT_ROOT / "scripts"))
        from atlas.anthropic_adapter import AnthropicOpenAIAdapter
        client = AnthropicOpenAIAdapter(api_key=anthropic_key)
        provider = "anthropic"
        print(f"Using Anthropic model: {args.model}")
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        provider = "openai"
        print(f"Using OpenAI model: {args.model}")
    else:
        print("Error: No valid API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        sys.exit(1)

    print(f"\nClassifying {len(to_classify)} conversations with {args.model}...")
    print(f"Estimated cost: ~${len(to_classify) * 0.02:.2f}")
    print(f"Estimated time: ~{len(to_classify) * args.delay / 1000 / 60:.0f} minutes\n")

    success = 0
    errors = 0

    for i, fpath in enumerate(to_classify):
        try:
            with open(fpath) as f:
                data = json.load(f)

            classification = classify_messages(
                client, data['messages'], few_shot_examples, args.model)

            data['classification'] = classification
            data['classificationMetadata'] = {
                'model': args.model,
                'provider': provider,
                'timestamp': datetime.now().isoformat(),
                'promptVersion': '2.0-social-role-theory',
            }

            with open(fpath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            success += 1
            pct = (i + 1) / len(to_classify) * 100
            print(f"\r  [{i+1}/{len(to_classify)}] ({pct:.0f}%) {fpath.name} - OK", end="", flush=True)

        except Exception as e:
            errors += 1
            print(f"\n  ERROR: {fpath.name}: {e}")

        if i < len(to_classify) - 1:
            time.sleep(args.delay / 1000)

    print(f"\n\nDone! Success: {success}, Errors: {errors}")


if __name__ == '__main__':
    main()
