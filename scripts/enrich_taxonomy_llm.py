#!/usr/bin/env python3
"""
Hybrid Taxonomy Enricher
Uses GPT-4o-mini to semantically tag tasks with Architecture and Constraint Hardness,
then computes drift statistics.
"""

import os
import json
import asyncio
import re
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
import pandas as pd # Optional, but good for stats if available, else standard python

# ================= Configuration =================

ENRICHMENT_PROMPT = """Analyze this Task Goal and its Constraints. Classify them into the following categories.

TAXONOMY DEFINITIONS:
1. Task Architecture:
   - "Generation": Creating new content (stories, code, emails, essays).
   - "Planning": Sequencing steps, scheduling, itineraries, roadmaps.
   - "Analysis": Evaluating, debugging, summarizing, or critiquing input.
   - "Transformation": Translating, formatting, or rewriting existing text.
   - "Information Seeking": Finding facts, learning concepts, "how to".

2. Constraint Hardness:
   - "Strict": Binary/Objective rules (e.g., "Python only", "JSON format", "valid syntax", "under 500 words").
   - "Flexible": Subjective/Vague rules (e.g., "be polite", "creative tone", "professional style").
   - "Mixed": Contains both strong rules and style guides.

INPUT:
Goal: {goal}
Constraints: {constraints}

Respond in JSON only:
{{
  "architecture": "Generation" | "Planning" | "Analysis" | "Transformation" | "Information Seeking" | "Other",
  "constraint_hardness": "Strict" | "Flexible" | "Mixed"
}}
"""

# ================= Async LLM Worker =================

async def enrich_item(client, item, semaphore, model):
    async with semaphore:
        cls = item.get("classification", {})
        goal = cls.get("task_goal", "")
        constraints = cls.get("primary_constraints", [])
        
        prompt = ENRICHMENT_PROMPT.format(
            goal=goal,
            constraints=json.dumps(constraints)
        )
        
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a data classifier. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_completion_tokens=100
            )
            
            content = response.choices[0].message.content.strip()
            # Clean markdown
            content = re.sub(r'^```json?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
            
            tags = json.loads(content)
            
            # Merge into item
            item["taxonomy"] = tags
            return item
            
        except Exception as e:
            print(f"Error classifying {item.get('id')}: {e}")
            item["taxonomy"] = {"architecture": "Other", "constraint_hardness": "Mixed"}
            return item

# ================= Analysis & Reporting =================

def print_report(data):
    # Aggregation
    arch_stats = {}
    hard_stats = {}
    
    total = len(data)
    
    for item in data:
        tax = item.get("taxonomy", {})
        arch = tax.get("architecture", "Other")
        hard = tax.get("constraint_hardness", "Mixed")
        
        drift = 1 if item["classification"].get("stability_class") == "Constraint Drift" else 0
        
        # Arch
        if arch not in arch_stats: arch_stats[arch] = {"total": 0, "drift": 0}
        arch_stats[arch]["total"] += 1
        arch_stats[arch]["drift"] += drift
        
        # Hardness
        if hard not in hard_stats: hard_stats[hard] = {"total": 0, "drift": 0}
        hard_stats[hard]["total"] += 1
        hard_stats[hard]["drift"] += drift

    overall_drift = sum(i["classification"].get("stability_class") == "Constraint Drift" for i in data) / total
    
    print("\n" + "="*70)
    print(f"HYBRID TAXONOMY ANALYSIS (N={total}) | Baseline Drift: {overall_drift:.1%}")
    print("="*70 + "\n")
    
    # 1. Architecture Table
    print(f"{'Architecture':<25} {'Count':<10} {'Drift %':<10} {'Risk Factor'}")
    print("-" * 65)
    for k in sorted(arch_stats.keys(), key=lambda x: arch_stats[x]["total"], reverse=True):
        s = arch_stats[k]
        if s["total"] < 5: continue
        rate = s["drift"] / s["total"]
        risk = rate / overall_drift if overall_drift > 0 else 0
        print(f"{k:<25} {s['total']:<10} {rate:.1%}{'':<5} {risk:.2f}x")
        
    print("\n")
    
    # 2. Hardness Table
    print(f"{'Constraint Hardness':<25} {'Count':<10} {'Drift %':<10} {'Risk Factor'}")
    print("-" * 65)
    for k in sorted(hard_stats.keys(), key=lambda x: hard_stats[x]["total"], reverse=True):
        s = hard_stats[k]
        if s["total"] < 5: continue
        rate = s["drift"] / s["total"]
        risk = rate / overall_drift if overall_drift > 0 else 0
        print(f"{k:<25} {s['total']:<10} {rate:.1%}{'':<5} {risk:.2f}x")

# ================= Main =================

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/task_classified/all_task_enriched.json")
    parser.add_argument("--model", default="gpt-4o")
    args = parser.parse_args()
    
    # Setup
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Missing API Key")
        return
        
    client = AsyncOpenAI(api_key=api_key)
    
    # Load
    with open(args.input, 'r') as f:
        data = json.load(f)
        
    print(f"Processing {len(data)} items with GPT-4o-mini...")
    
    # Run
    semaphore = asyncio.Semaphore(20) # High concurrency
    tasks = [enrich_item(client, item, semaphore, args.model) for item in data]
    
    enriched_data = []
    for f in asyncio.as_completed(tasks):
        res = await f
        enriched_data.append(res)
        print(".", end="", flush=True)
        
    print("\nDone.")
    
    # Save
    with open(args.output, 'w') as f:
        json.dump(enriched_data, f, indent=2)
        
    # Report
    print_report(enriched_data)

if __name__ == "__main__":
    asyncio.run(main())
