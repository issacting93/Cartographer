#!/usr/bin/env python3
"""
LLM-Enhanced Feature Extraction

Uses LLM to improve feature quality where regex is weak:
- Specificity scoring (semantic understanding)
- Repair detection (contextual)
- Stance classification (nuanced)

Maintains methodological rigor:
- Features are still per-conversation
- Clustering remains unsupervised
- Archetypes emerge post-hoc
"""

import os
import json
import re
import asyncio
import argparse
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path
from openai import AsyncOpenAI

# Import base features
from features import (
    ConversationFeatures,
    count_pattern_matches,
    REPAIR_MARKERS,
    CONSTRAINT_HARD,
    CONSTRAINT_SOFT,
    CONSTRAINT_GOAL,
    find_verbatim_repeats,
    detect_source,
)


# ============= LLM PROMPTS =============

SPECIFICITY_PROMPT = """Rate the specificity of this user message on a 1-5 scale:

1 = Vague: No clear requirements ("help me with something", "make it better")
2 = Low: General topic but no constraints ("write about dogs", "explain quantum physics")
3 = Moderate: Some requirements stated ("write 500 words about dogs", "explain for a beginner")
4 = High: Clear requirements with constraints ("write 500 words about golden retrievers, focus on health issues, formal tone")
5 = Precise: Detailed specs with quantified constraints ("write exactly 500 words about golden retriever hip dysplasia, cite 3 sources, formal academic tone, no personal pronouns")

User message:
"{text}"

Respond with ONLY a single digit (1-5):"""


REPAIR_PROMPT = """Is this user message attempting to correct or redirect the AI?

A repair attempt includes:
- Correcting a misunderstanding ("No, I meant...")
- Restating requirements ("I said I wanted...")
- Expressing the AI didn't follow instructions ("That's not what I asked")
- Redirecting to original goal ("Let's go back to...")

User message:
"{text}"

Previous AI response (context):
"{prev_ai}"

Is this a repair attempt? Respond with ONLY "yes" or "no":"""


STANCE_PROMPT = """Classify this user's stance toward the AI:

1 = Directive: User is in control, giving clear instructions
2 = Collaborative: Working together, back-and-forth
3 = Deferential: Asking for AI's opinion, uncertain
4 = Passive: Just accepting, minimal engagement
5 = Frustrated: Showing signs of giving up or irritation

User message:
"{text}"

Respond with ONLY a single digit (1-5):"""


POLITENESS_PROMPT = """Rate the politeness of this user message on a -1 to +1 scale:

-1 = Rude/Frustrated: Demands, complaints, dismissive
0 = Neutral: Neither particularly polite nor rude
+1 = Polite: Please, thank you, collaborative language

User message:
"{text}"

Respond with ONLY a number between -1 and 1 (can be decimal like 0.5):"""


# ============= LLM FEATURE EXTRACTION =============

@dataclass
class LLMEnhancedFeatures:
    """Features extracted with LLM assistance."""
    
    # Metadata
    conversation_id: str
    source: str
    total_turns: int
    user_turns: int
    
    # LLM-enhanced features
    specificity_scores: List[int]  # Per user turn
    specificity_initial: float
    specificity_final: float
    specificity_delta: float
    
    repair_detected: List[bool]  # Per user turn
    repair_count: int
    
    stance_scores: List[int]  # Per user turn
    stance_initial: float
    stance_final: float
    stance_delta: float
    
    politeness_scores: List[float]  # Per user turn
    politeness_initial: float
    politeness_final: float
    politeness_delta: float
    
    # Regex features (kept for comparison)
    constraint_count: int
    verbatim_repeats: int
    mean_user_length: float
    
    # Derived
    passive_rate: float  # Turns with stance >= 4


async def score_specificity(client: AsyncOpenAI, text: str, model: str) -> int:
    """Score specificity 1-5 using LLM."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": SPECIFICITY_PROMPT.format(text=text[:500])}],
            temperature=0,
            max_tokens=5
        )
        content = response.choices[0].message.content.strip()
        return int(content[0]) if content[0].isdigit() else 3
    except:
        return 3


async def detect_repair(client: AsyncOpenAI, text: str, prev_ai: str, model: str) -> bool:
    """Detect if message is a repair attempt."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": REPAIR_PROMPT.format(text=text[:300], prev_ai=prev_ai[:300])}],
            temperature=0,
            max_tokens=5
        )
        content = response.choices[0].message.content.strip().lower()
        return content.startswith('yes')
    except:
        return False


async def score_stance(client: AsyncOpenAI, text: str, model: str) -> int:
    """Score stance 1-5 using LLM."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": STANCE_PROMPT.format(text=text[:500])}],
            temperature=0,
            max_tokens=5
        )
        content = response.choices[0].message.content.strip()
        return int(content[0]) if content[0].isdigit() else 2
    except:
        return 2


async def score_politeness(client: AsyncOpenAI, text: str, model: str) -> float:
    """Score politeness -1 to +1 using LLM."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": POLITENESS_PROMPT.format(text=text[:500])}],
            temperature=0,
            max_tokens=10
        )
        content = response.choices[0].message.content.strip()
        # Parse number
        match = re.search(r'-?\d*\.?\d+', content)
        if match:
            val = float(match.group())
            return max(-1, min(1, val))
        return 0
    except:
        return 0


async def extract_llm_features(
    client: AsyncOpenAI,
    conversation_id: str,
    messages: List[dict],
    source: str,
    model: str
) -> Optional[LLMEnhancedFeatures]:
    """Extract features using LLM."""
    
    user_messages = []
    prev_ai_responses = []
    
    for i, msg in enumerate(messages):
        if msg.get('role') == 'user':
            user_messages.append(msg.get('content', ''))
            # Find previous AI response
            prev_ai = ""
            for j in range(i - 1, -1, -1):
                if messages[j].get('role') == 'assistant':
                    prev_ai = messages[j].get('content', '')[:300]
                    break
            prev_ai_responses.append(prev_ai)
    
    if not user_messages:
        return None
    
    # Score each user turn (batch for efficiency)
    specificity_scores = []
    repair_detected = []
    stance_scores = []
    politeness_scores = []
    
    for i, text in enumerate(user_messages):
        # Run LLM calls concurrently for this turn
        spec, repair, stance, polite = await asyncio.gather(
            score_specificity(client, text, model),
            detect_repair(client, text, prev_ai_responses[i], model),
            score_stance(client, text, model),
            score_politeness(client, text, model),
        )
        specificity_scores.append(spec)
        repair_detected.append(repair)
        stance_scores.append(stance)
        politeness_scores.append(polite)
    
    # Compute aggregates
    n = len(user_messages)
    n_initial = min(3, n)
    n_final = min(3, n)
    
    spec_initial = sum(specificity_scores[:n_initial]) / n_initial
    spec_final = sum(specificity_scores[-n_final:]) / n_final
    
    stance_initial = sum(stance_scores[:n_initial]) / n_initial
    stance_final = sum(stance_scores[-n_final:]) / n_final
    
    polite_initial = sum(politeness_scores[:n_initial]) / n_initial
    polite_final = sum(politeness_scores[-n_final:]) / n_final
    
    # Passive rate: stance >= 4 (passive or frustrated)
    passive_count = sum(1 for s in stance_scores if s >= 4)
    
    # Regex features
    user_texts = user_messages
    constraint_count = sum(
        count_pattern_matches(t, CONSTRAINT_HARD) +
        count_pattern_matches(t, CONSTRAINT_SOFT) +
        count_pattern_matches(t, CONSTRAINT_GOAL)
        for t in user_texts
    )
    
    return LLMEnhancedFeatures(
        conversation_id=conversation_id,
        source=source,
        total_turns=len(messages),
        user_turns=n,
        specificity_scores=specificity_scores,
        specificity_initial=round(spec_initial, 2),
        specificity_final=round(spec_final, 2),
        specificity_delta=round(spec_final - spec_initial, 2),
        repair_detected=repair_detected,
        repair_count=sum(repair_detected),
        stance_scores=stance_scores,
        stance_initial=round(stance_initial, 2),
        stance_final=round(stance_final, 2),
        stance_delta=round(stance_final - stance_initial, 2),
        politeness_scores=politeness_scores,
        politeness_initial=round(polite_initial, 2),
        politeness_final=round(polite_final, 2),
        politeness_delta=round(polite_final - polite_initial, 2),
        constraint_count=constraint_count,
        verbatim_repeats=find_verbatim_repeats(user_texts),
        mean_user_length=round(sum(len(t) for t in user_texts) / n, 1),
        passive_rate=round(passive_count / n, 2),
    )


async def process_file(
    client: AsyncOpenAI,
    filepath: Path,
    model: str,
    semaphore: asyncio.Semaphore
) -> Optional[LLMEnhancedFeatures]:
    """Process a single file with rate limiting."""
    async with semaphore:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            return None
        
        messages = data.get("messages", data.get("conversation", []))
        if len(messages) < 10:
            return None
        
        return await extract_llm_features(
            client,
            filepath.stem,
            messages,
            detect_source(filepath),
            model
        )


async def main():
    parser = argparse.ArgumentParser(description="LLM-enhanced feature extraction")
    parser.add_argument("--input", "-i", required=True, help="Input directory")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file")
    parser.add_argument("--sample", "-s", type=int, default=None, help="Sample N files")
    parser.add_argument("--model", "-m", default="gpt-4o-mini", help="OpenAI model")
    parser.add_argument("--concurrent", "-c", type=int, default=3, help="Concurrent requests")
    args = parser.parse_args()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    input_dir = Path(args.input)
    json_files = list(input_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON files")
    
    if args.sample:
        import random
        json_files = random.sample(json_files, min(args.sample, len(json_files)))
        print(f"Sampled {len(json_files)} files")
    
    semaphore = asyncio.Semaphore(args.concurrent)
    tasks = [process_file(client, fp, args.model, semaphore) for fp in json_files]
    
    results = []
    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro
        if result:
            results.append(asdict(result))
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(json_files)} ({len(results)} extracted)")
    
    print(f"\n✅ Extracted LLM-enhanced features from {len(results)} conversations")
    
    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Saved to {output_path}")
    
    # Stats
    print("\n📊 Feature Summary (LLM-enhanced):")
    print(f"  Mean specificity_delta: {sum(r['specificity_delta'] for r in results) / len(results):.2f}")
    print(f"  Mean repair_count: {sum(r['repair_count'] for r in results) / len(results):.2f}")
    print(f"  Mean stance_delta: {sum(r['stance_delta'] for r in results) / len(results):.2f}")
    print(f"  Mean politeness_delta: {sum(r['politeness_delta'] for r in results) / len(results):.2f}")
    print(f"  Mean passive_rate: {sum(r['passive_rate'] for r in results) / len(results):.2f}")


if __name__ == "__main__":
    asyncio.run(main())
