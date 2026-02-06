#!/usr/bin/env python3
"""
Task-First Classifier for CUI 2026 Paper
Classifies conversations based on Task Object stability, using robust production-grade logic.

Features:
- Smart truncation (Head + Tail + Keyword search)
- Retry logic with exponential backoff
- JSON repair pass for malformed outputs
- Strict schema validation
- Caching (hash-based)
- Evidence span extraction

Usage:
    python3 classify_task_first.py --input ./data/source --output ./data/task_classified
"""

import os
import json
import re
import argparse
import asyncio
import hashlib
import random
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Any, Set
from datetime import datetime
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# ============= Configuration =============

TASK_STATES = {
    "Task Maintained",
    "Constraint Drift",
    "Agency Collapse",
    "Task Shift",
    "No Constraints"
}

DECISION_RULES = """
DECISION RULES:
- Task Shift ONLY if user explicitly changes the goal (not just relaxing a constraint due to AI pressure).
- Agency Collapse ONLY if AI violates a constraint AND user later accepts/abandons it or stops enforcing it.
- Constraint Drift if AI violates AND user repairs AND constraint is enforced afterward.
- Task Maintained if no meaningful violations OR immediate minor correction with no drift.
- No Constraints if no stable goal + no explicit constraints are present.
"""

CLASSIFICATION_PROMPT = """Analyze this human-AI conversation through a "Task Object" lens.

TASK STATES:
1. Task Maintained: Core goal and constraints are preserved throughout.
2. Constraint Drift: Constraints are violated/forgotten but successfully repaired by user.
3. Agency Collapse: Constraints are violated and the user abandons them (accepts violation).
4. Task Shift: User explicitly changes the task (valid adaptation, not collapse).
5. No Constraints: Interaction had no explicit constraints to maintain.

{decision_rules}

CONVERSATION:
{conversation}

TASK:
1. Identify the Task Object (User's Goal).
2. Identify Primary Constraints (invariable requirements).
   CONSTRAINT QUALITY FILTER — Only emit constraints that meet ALL criteria:
   - Verifiable: A third party could check pass/fail against the AI response.
   - Specific: Names a concrete behavior, format, boundary, or exclusion.
   - NOT aspirational: Reject quality standards ("provide accurate information",
     "be helpful", "give correct answers").
   - NOT meta-goals: Reject general competence descriptions.
   If no verifiable constraints exist, return an empty primary_constraints list.
3. Detect Violations (AI ignoring constraints).
4. Analyze User Response (Repair vs Abandon).
5. Classify stability.

Respond in this exact JSON format:
{{
  "task_goal": "<short summary>",
  "primary_constraints": ["<constraint 1>", "<constraint 2>", ...],
  "stability_class": "<one of the 5 Task States>",
  "confidence": <0.0-1.0>,
  "violation_count": <int>,
  "user_response": "<Repaired/Abandoned/N/A>",
  "reasoning": "<explanation>",
  "evidence": {{
      "constraint_turns": [<int>, ...], 
      "violation_turns": [<int>, ...],
      "repair_turns": [<int>, ...]
  }}
}}"""

# ============= Data Classes & Validation =============

@dataclass
class TaskEvidence:
    constraint_turns: List[int]
    violation_turns: List[int]
    repair_turns: List[int]

@dataclass
class TaskClassification:
    task_goal: str
    primary_constraints: List[str]
    stability_class: str
    confidence: float
    violation_count: int
    user_response: str
    reasoning: str
    evidence: TaskEvidence

@dataclass
class ClassifiedConversation:
    id: str
    source: str
    domain: str
    total_turns: int
    classification: TaskClassification
    file_path: str

def normalize_class(s: Any) -> str:
    if not isinstance(s, str): return "No Constraints"
    s = s.strip()
    mapping = {
        "TaskMaintained": "Task Maintained",
        "ConstraintDrift": "Constraint Drift",
        "AgencyCollapse": "Agency Collapse",
        "TaskShift": "Task Shift",
        "NoConstraint": "No Constraints",
    }
    s = mapping.get(s, s)
    return s if s in TASK_STATES else "No Constraints"

def coerce_float(x: Any, default=0.5) -> float:
    try:
        v = float(x)
        return max(0.0, min(1.0, v))
    except (ValueError, TypeError):
        return default

def coerce_int(x: Any, default=0) -> int:
    try:
        return max(0, int(float(x)))
    except (ValueError, TypeError):
        return default

def ensure_str_list(x: Any) -> List[str]:
    if not isinstance(x, list): return []
    return [str(i).strip() for i in x if str(i).strip()]

def ensure_int_list(x: Any) -> List[int]:
    if not isinstance(x, list): return []
    return [coerce_int(i) for i in x]

def validate_taskclassification(data: dict) -> TaskClassification:
    ev = data.get("evidence", {})
    return TaskClassification(
        task_goal=str(data.get("task_goal", "Unknown")).strip()[:300],
        primary_constraints=ensure_str_list(data.get("primary_constraints", []))[:20],
        stability_class=normalize_class(data.get("stability_class")),
        confidence=coerce_float(data.get("confidence", 0.5)),
        violation_count=coerce_int(data.get("violation_count", 0)),
        user_response=str(data.get("user_response", "N/A")).strip()[:100],
        reasoning=str(data.get("reasoning", "")).strip()[:1500],
        evidence=TaskEvidence(
            constraint_turns=ensure_int_list(ev.get("constraint_turns", [])),
            violation_turns=ensure_int_list(ev.get("violation_turns", [])),
            repair_turns=ensure_int_list(ev.get("repair_turns", []))
        )
    )

# ============= Helpers =============

REPAIR_HINTS = ["i said", "no", "not", "instead", "remote only", "under", "stop", "again", "as i said", "actually", "wrong"]

def smart_truncate(messages: List[dict], max_chars: int = 12000, head: int = 10, tail: int = 10) -> str:
    if len(messages) <= head + tail:
        return truncate_to_chars(messages, max_chars)

    head_msgs = messages[:head]
    tail_msgs = messages[-tail:]
    
    # Scan middle for repair signals
    mid_msgs = messages[head:-tail]
    picked = []
    
    for i, m in enumerate(mid_msgs):
        txt = (m.get("content") or "").lower()
        if any(h in txt for h in REPAIR_HINTS):
            # Keep original index hint in content if possible, but here we just grab the msg
            # To track turn numbers accurately, we'd need to preserve original indices.
            # For purely text classification, extracting the content is enough.
            picked.append(m)
        if len(picked) >= 15: # Grab up to 15 interesting mid-turns
            break
            
    stitched = head_msgs + picked + tail_msgs
    # Sort by time? No, picked are in order.
    # Note: This loses the strictly linear flow but captures key moments.
    return truncate_to_chars(stitched, max_chars)

def truncate_to_chars(messages: List[dict], max_chars: int) -> str:
    lines = []
    char_count = 0
    for i, msg in enumerate(messages):
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")[:1500]
        line = f"[Turn {i}] {role}: {content}" # Add explicit turn numbers for evidence
        
        if char_count + len(line) > max_chars:
            lines.append("... [truncated] ...")
            break
        lines.append(line)
        char_count += len(line)
    return "\n\n".join(lines)

def detect_domain(text: str) -> str:
    text_lower = text.lower()
    keywords = {
        "career": ["job", "resume", "interview", "salary", "hire", "recruiter", "linkedin"],
        "code": ["code", "function", "debug", "error", "python", "java", "script", "api", "compile"],
        "travel": ["flight", "hotel", "trip", "vacation", "booking", "itinerary", "visa"],
        "education": ["learn", "explain", "teach", "tutor", "student", "assignment"],
        "creative": ["write", "story", "poem", "essay", "draft", "plot", "character"],
        "finance": ["invest", "stock", "portfolio", "bank", "tax", "crypto"],
        "limitations": ["sorry", "i cannot", "language model"]
    }
    
    # Count hits
    scores = {k: 0 for k in keywords}
    for k, words in keywords.items():
        for w in words:
            if w in text_lower:
                scores[k] += 1
                
    # Get max
    best_domain = max(scores, key=scores.get)
    if scores[best_domain] >= 2:
        return best_domain
    return "general"

def file_hash(path: Path) -> str:
    try:
        b = path.read_bytes()
        return hashlib.sha256(b).hexdigest()[:16]
    except:
        return "unknown"

async def with_retries(fn, max_tries=6, base_delay=1.0):
    for attempt in range(max_tries):
        try:
            return await fn()
        except Exception as e:
            msg = str(e).lower()
            # Retry on rate limits and server errors
            retriable = any(k in msg for k in ["429", "rate", "limit", "timeout", "503", "502", "500", "connection"])
            if not retriable or attempt == max_tries - 1:
                raise
            
            delay = base_delay * (2 ** attempt) + random.random() * 0.5
            print(f"  [Retry {attempt+1}/{max_tries}] Error: {str(e)[:50]}... Waiting {delay:.1f}s")
            await asyncio.sleep(delay)

# ============= LLM Logic =============

async def repair_to_json(client: AsyncOpenAI, model: str, bad_text: str) -> Optional[dict]:
    prompt = f"""Fix this into valid JSON matching the schema. Return JSON only.
TEXT:
{bad_text[:4000]}""" # Truncate if massive
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":"You output JSON only."},
                {"role":"user","content":prompt}
            ],
            temperature=0.0,
            max_tokens=600
        )
        fixed = response.choices[0].message.content.strip()
        fixed = re.sub(r"^```json?\n?", "", fixed)
        fixed = re.sub(r"\n?```$", "", fixed)
        return json.loads(fixed)
    except:
        return None

async def classify_with_llm(client: AsyncOpenAI, conversation: List[dict], model: str) -> Optional[TaskClassification]:
    conv_text = smart_truncate(conversation)
    
    prompt = CLASSIFICATION_PROMPT.format(
        decision_rules=DECISION_RULES,
        conversation=conv_text
    )
    
    try:
        # Call with retries
        response = await with_retries(lambda: client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert in Agency Analysis. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0, # Deterministic
            max_tokens=600
        ))
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown
        content = re.sub(r'^```json?\n?', '', content)
        content = re.sub(r'\n?```$', '', content)
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print("  ! JSON parse failed, attempting repair...")
            data = await repair_to_json(client, model, content)
            if not data:
                return None
                
        return validate_taskclassification(data)
        
    except Exception as e:
        print(f"  Fatal error in LLM call: {e}")
        return None

async def process_file(client, filepath: Path, output_dir: Path, model: str) -> Optional[ClassifiedConversation]:
    fhash = file_hash(filepath)
    cache_file = output_dir / f"{filepath.stem}_{fhash}.json"
    
    # 1. Check cache
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                # Re-validate to ensure type safety even from cache
                # Re-wrap
                cls_data = cached.get("classification", {})
                return ClassifiedConversation(
                    id=cached["id"],
                    source=cached["source"],
                    domain=cached["domain"],
                    total_turns=cached["total_turns"],
                    classification=TaskClassification(
                        task_goal=cls_data.get("task_goal"),
                        primary_constraints=cls_data.get("primary_constraints"),
                        stability_class=cls_data.get("stability_class"),
                        confidence=cls_data.get("confidence"),
                        violation_count=cls_data.get("violation_count"),
                        user_response=cls_data.get("user_response"),
                        reasoning=cls_data.get("reasoning"),
                        evidence=TaskEvidence(**cls_data.get("evidence", {}))
                    ),
                    file_path=cached["file_path"]
                )
        except Exception:
            pass # Invalid cache, ignore

    # 2. Load Data
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except: return None
    
    messages = data.get("messages", data.get("conversation", []))
    if len(messages) < 6: return None
    
    # 3. Classify
    cl = await classify_with_llm(client, messages, model)
    if not cl: return None
    
    # 4. Domain Detect
    full_text = " ".join([m.get("content","") for m in messages])
    domain = detect_domain(full_text)
    
    source_name = filepath.stem.lower()
    source = "ChatbotArena" if "arena" in source_name else \
             "OASST" if "oasst" in source_name else "WildChat"
    
    result = ClassifiedConversation(
        id=filepath.stem,
        source=source,
        domain=domain,
        total_turns=len(messages),
        classification=cl,
        file_path=str(filepath)
    )
    
    # 5. Write to Cache
    try:
        with open(cache_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
    except Exception as e:
        print(f"Failed to write cache: {e}")
        
    return result

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample", type=int, default=None)
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--concurrent", type=int, default=10)
    args = parser.parse_args()
    
    # Load .env explicitly if allowed
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Missing OPENAI_API_KEY. Checked environment and .env")
        return

    client = AsyncOpenAI(api_key=api_key)
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(input_dir.glob("*.json"))
    if args.sample:
        files = random.sample(files, min(args.sample, len(files)))
    
    print(f"🚀 Processing {len(files)} files with model {args.model}")
    print(f"   Concurrency: {args.concurrent}")
    print(f"   Output: {output_dir}")
    
    semaphore = asyncio.Semaphore(args.concurrent)
    async def run(fp):
        async with semaphore:
            res = await process_file(client, fp, output_dir, args.model)
            print(".", end="", flush=True)
            return res
            
    tasks = [run(fp) for fp in files]
    results = []
    
    start = time.time()
    for coro in asyncio.as_completed(tasks):
        res = await coro
        if res: results.append(res)
    duration = time.time() - start
    
    print(f"\n\n✅ Done in {duration:.1f}s")
    print(f"   Successfully classified: {len(results)}/{len(files)}")
        
    # Stats
    counts = {}
    for r in results:
        s = r.classification.stability_class
        counts[s] = counts.get(s, 0) + 1
        
    print("\nTask Stability Distribution:")
    for s in TASK_STATES:
        c = counts.get(s, 0)
        pct = (c / len(results) * 100) if len(results) > 0 else 0
        print(f"  {s:<20}: {c} ({pct:.1f}%)")
        
    # Save Aggregate
    agg_file = output_dir / "all_task_classified.json"
    with open(agg_file, 'w') as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\nSaved aggregate to {agg_file}")

if __name__ == "__main__":
    asyncio.run(main())
