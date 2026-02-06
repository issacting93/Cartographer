#!/usr/bin/env python3
"""
LLM-Assisted Dataset Classifier for CUI 2026 Paper
Uses OpenAI to classify archetypes and detect Agency Collapse patterns.

Usage:
    python classify_llm.py --input ./data/output --output ./data/classified
    
Environment:
    OPENAI_API_KEY=sk-...
"""

import os
import json
import re
import argparse
import asyncio
from dataclasses import dataclass, asdict
from typing import List, Optional, Literal
from datetime import datetime
from pathlib import Path
from openai import AsyncOpenAI

# ============= Configuration =============

ARCHETYPES = [
    "Provider Trap",
    "Hallucination Loop", 
    "Identity Shift",
    "Canvas Hack",
    "Passive Default",
    "Mixed/Other"
]

ARCHETYPE_DESCRIPTIONS = """
ARCHETYPES:
1. Provider Trap: User starts with specific requirements but becomes increasingly passive as AI takes control. The AI expands scope beyond original intent.
2. Hallucination Loop: User makes repeated failed attempts to correct the AI. Multiple "no, I meant..." or "that's not what I asked" patterns.
3. Identity Shift: User's tone degrades from polite/collaborative to curt/frustrated. "Please could you" becomes "Just give me" becomes "No."
4. Canvas Hack: User copy-pastes the same constraint text 2+ times because AI keeps forgetting it.
5. Passive Default: User never states specific requirements, just accepts whatever AI suggests with "ok", "sure", "thanks".
6. Mixed/Other: Doesn't clearly fit any pattern, or shows healthy back-and-forth without collapse.
"""

CLASSIFICATION_PROMPT = """Analyze this human-AI conversation for Agency Collapse patterns.

{archetype_descriptions}

CONVERSATION:
{conversation}

TASK: Classify this conversation into exactly ONE archetype. Consider:
- Does the user start specific and become passive? (Provider Trap)
- Are there repeated failed corrections? (Hallucination Loop)  
- Does tone degrade from polite to frustrated? (Identity Shift)
- Does user repeat the same text multiple times? (Canvas Hack)
- Is user passive throughout with no specific requests? (Passive Default)
- Is it a healthy interaction without clear collapse? (Mixed/Other)

Also estimate:
- Agency Collapse present: true/false
- User specificity trend: increasing/stable/decreasing
- Constraint violations observed: count (0-10)

Respond in this exact JSON format:
{{
  "archetype": "<one of the 6 archetypes>",
  "confidence": <0.0-1.0>,
  "collapse_detected": <true/false>,
  "specificity_trend": "<increasing/stable/decreasing>",
  "constraint_violations": <0-10>,
  "reasoning": "<1-2 sentence explanation>"
}}"""


# ============= Data Classes =============

@dataclass
class LLMClassification:
    archetype: str
    confidence: float
    collapse_detected: bool
    specificity_trend: str
    constraint_violations: int
    reasoning: str


@dataclass
class ClassifiedConversation:
    id: str
    source: str
    domain: str
    total_turns: int
    classification: LLMClassification
    file_path: str


# ============= Helper Functions =============

def detect_domain(text: str) -> str:
    """Simple domain detection."""
    text_lower = text.lower()
    
    keywords = {
        "career": ["job", "resume", "interview", "salary", "hire", "career", "remote", "position"],
        "travel": ["flight", "hotel", "trip", "vacation", "travel", "booking"],
        "code": ["code", "function", "debug", "error", "python", "javascript", "api"],
        "education": ["learn", "explain", "teach", "understand", "study"],
        "creative": ["write", "story", "poem", "essay", "creative"],
    }
    
    for domain, kws in keywords.items():
        if sum(1 for kw in kws if kw in text_lower) >= 2:
            return domain
    return "general"


def truncate_conversation(messages: List[dict], max_chars: int = 8000) -> str:
    """Format conversation for LLM, truncating if needed."""
    lines = []
    char_count = 0
    
    for msg in messages:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")[:500]  # Truncate individual messages
        line = f"{role}: {content}"
        
        if char_count + len(line) > max_chars:
            lines.append("... [truncated] ...")
            break
        
        lines.append(line)
        char_count += len(line)
    
    return "\n\n".join(lines)


def detect_source(filepath: Path) -> str:
    """Detect source from filename."""
    name = filepath.stem.lower()
    if "arena" in name or "chatbot" in name:
        return "ChatbotArena"
    elif "oasst" in name:
        return "OASST"
    return "WildChat"


# ============= LLM Classification =============

async def classify_with_llm(
    client: AsyncOpenAI,
    conversation: List[dict],
    model: str = "gpt-4o-mini"
) -> Optional[LLMClassification]:
    """Use LLM to classify a conversation."""
    
    conv_text = truncate_conversation(conversation)
    
    prompt = CLASSIFICATION_PROMPT.format(
        archetype_descriptions=ARCHETYPE_DESCRIPTIONS,
        conversation=conv_text
    )
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert in Human-Computer Interaction analyzing conversation patterns. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON (handle markdown code blocks)
        if content.startswith("```"):
            content = re.sub(r'^```json?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        
        data = json.loads(content)
        
        return LLMClassification(
            archetype=data.get("archetype", "Mixed/Other"),
            confidence=data.get("confidence", 0.5),
            collapse_detected=data.get("collapse_detected", False),
            specificity_trend=data.get("specificity_trend", "stable"),
            constraint_violations=data.get("constraint_violations", 0),
            reasoning=data.get("reasoning", "")
        )
        
    except Exception as e:
        print(f"  LLM classification error: {e}")
        return None


async def process_file(
    client: AsyncOpenAI,
    filepath: Path,
    model: str
) -> Optional[ClassifiedConversation]:
    """Process a single conversation file."""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    
    messages = data.get("messages", data.get("conversation", []))
    if len(messages) < 10:
        return None
    
    # Get domain from all user text
    user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
    domain = detect_domain(user_text)
    source = detect_source(filepath)
    
    # LLM classification
    classification = await classify_with_llm(client, messages, model)
    
    if not classification:
        return None
    
    return ClassifiedConversation(
        id=filepath.stem,
        source=source,
        domain=domain,
        total_turns=len(messages),
        classification=classification,
        file_path=str(filepath)
    )


async def main():
    parser = argparse.ArgumentParser(description="LLM-assisted conversation classification")
    parser.add_argument("--input", "-i", required=True, help="Input directory")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--sample", "-s", type=int, default=None, help="Sample N files")
    parser.add_argument("--model", "-m", default="gpt-4o-mini", help="OpenAI model")
    parser.add_argument("--concurrent", "-c", type=int, default=5, help="Concurrent requests")
    args = parser.parse_args()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get files
    json_files = list(input_dir.glob("*.json"))
    print(f"Found {len(json_files)} JSON files")
    
    if args.sample:
        import random
        json_files = random.sample(json_files, min(args.sample, len(json_files)))
        print(f"Sampled {len(json_files)} files")
    
    # Process with concurrency limit
    results = []
    semaphore = asyncio.Semaphore(args.concurrent)
    
    async def process_with_limit(fp):
        async with semaphore:
            return await process_file(client, fp, args.model)
    
    print(f"Processing with {args.concurrent} concurrent requests...")
    
    tasks = [process_with_limit(fp) for fp in json_files]
    
    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro
        if result:
            results.append(result)
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(json_files)} ({len(results)} classified)")
    
    print(f"\n✅ Classified {len(results)} conversations")
    
    # Statistics
    archetype_counts = {}
    collapse_count = 0
    
    for r in results:
        arch = r.classification.archetype
        archetype_counts[arch] = archetype_counts.get(arch, 0) + 1
        if r.classification.collapse_detected:
            collapse_count += 1
    
    print("\n📊 Archetype Distribution:")
    for arch in ARCHETYPES:
        count = archetype_counts.get(arch, 0)
        pct = count / len(results) * 100 if results else 0
        print(f"  {arch}: {count} ({pct:.1f}%)")
    
    collapse_rate = collapse_count / len(results) * 100 if results else 0
    print(f"\n📊 Agency Collapse Rate: {collapse_rate:.1f}%")
    
    # Save results
    output_file = output_dir / "llm_classified_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        serializable = []
        for r in results:
            d = {
                "id": r.id,
                "source": r.source,
                "domain": r.domain,
                "total_turns": r.total_turns,
                "classification": asdict(r.classification),
                "file_path": r.file_path
            }
            serializable.append(d)
        json.dump(serializable, f, indent=2)
    
    print(f"\n💾 Saved to {output_file}")
    
    # Paper statistics
    stats_file = output_dir / "llm_paper_statistics.md"
    with open(stats_file, 'w') as f:
        f.write("# LLM-Classified Dataset Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Model:** {args.model}\n")
        f.write(f"**N:** {len(results)}\n\n")
        f.write("## Archetype Distribution\n\n")
        f.write("| Archetype | N | % |\n|-----------|---|---|\n")
        for arch in ARCHETYPES:
            count = archetype_counts.get(arch, 0)
            pct = count / len(results) * 100 if results else 0
            f.write(f"| {arch} | {count} | {pct:.1f}% |\n")
        f.write(f"\n## Agency Collapse\n\n")
        f.write(f"- **Collapse Detected:** {collapse_count} ({collapse_rate:.1f}%)\n")
        
        # Domain breakdown
        domain_counts = {}
        for r in results:
            domain_counts[r.domain] = domain_counts.get(r.domain, 0) + 1
        f.write(f"\n## Domain Distribution\n\n")
        f.write("| Domain | N | % |\n|--------|---|---|\n")
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            pct = count / len(results) * 100
            f.write(f"| {domain} | {count} | {pct:.1f}% |\n")
    
    print(f"📄 Statistics saved to {stats_file}")


if __name__ == "__main__":
    asyncio.run(main())
