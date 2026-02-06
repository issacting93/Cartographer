#!/usr/bin/env python3
"""
Taxonomy Analyzer for CUI 2026
Analyze logical task types and constraint types to find correlations with Drift.
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict

# ================== Classification Logic ==================

def classify_task_type(goal: str, domain: str) -> str:
    text = goal.lower()
    
    # Priority Heuristics
    if any(w in text for w in ["plan", "schedule", "itinerary", "timeline", "organize", "roadmap"]):
        return "Planning"
    
    if any(w in text for w in ["write", "story", "poem", "essay", "draft", "plot", "character", "blog", "email", "letter"]):
        return "Creative Generation"
        
    if any(w in text for w in ["code", "function", "debug", "script", "api", "compile", "html", "css", "sql", "react"]):
        return "Coding"
        
    if any(w in text for w in ["analyze", "compare", "evaluate", "summary", "summarize", "review", "audit"]):
        return "Analysis"
        
    if any(w in text for w in ["learn", "explain", "teach", "how to", "what is", "search", "find"]):
        return "Information Seeking"
        
    return "Other"

def classify_constraint_type(constraints: list) -> str:
    # Heuristic: Hard vs Soft
    # Hard: Binary clear (format, length, language, forbidden words)
    # Soft: Vague (tone, style, quality)
    
    hard_signals = ["no ", "only ", "must ", "limit", "format", "json", "python", "english", "french", "pages", "words", "code block"]
    soft_signals = ["professional", "funny", "polite", "creative", "style", "brief", "concise", "tone", "friendly"]
    
    text = " ".join(constraints).lower()
    
    hard_score = sum(text.count(s) for s in hard_signals)
    soft_score = sum(text.count(s) for s in soft_signals)
    
    if hard_score > soft_score:
        return "Hard Constraints"
    elif soft_score > hard_score:
        return "Soft Constraints"
    else:
        return "Mixed/Neutral"

# ================== Analysis ==================

def analyze_drift(data):
    taxonomy = {
        "Task Type": defaultdict(lambda: {"total": 0, "drift": 0}),
        "Constraint Type": defaultdict(lambda: {"total": 0, "drift": 0}),
        "Domain": defaultdict(lambda: {"total": 0, "drift": 0})
    }
    
    for item in data:
        cls_data = item.get("classification", {})
        stability = cls_data.get("stability_class", "No Constraints")
        goal = cls_data.get("task_goal", "")
        constraints = cls_data.get("primary_constraints", [])
        domain = item.get("domain", "general")
        
        is_drift = (stability == "Constraint Drift")
        
        # Classify
        t_type = classify_task_type(goal, domain)
        c_type = classify_constraint_type(constraints)
        
        # Aggregate
        for cat, key in [("Task Type", t_type), ("Constraint Type", c_type), ("Domain", domain)]:
            taxonomy[cat][key]["total"] += 1
            if is_drift:
                taxonomy[cat][key]["drift"] += 1

    # Print Report
    print("\n" + "="*60)
    print("TAXONOMY DRIFT ANALYSIS (N={})".format(len(data)))
    print("="*60 + "\n")
    
    for category, metrics in taxonomy.items():
        print(f"--- {category} ---")
        print(f"{'Category':<25} {'Count':<10} {'Drift %':<10} {'Relative Risk'}")
        print("-" * 60)
        
        base_rate = sum(m["drift"] for m in metrics.values()) / len(data)
        
        sorted_keys = sorted(metrics.keys(), key=lambda k: metrics[k]["total"], reverse=True)
        
        for k in sorted_keys:
            m = metrics[k]
            if m["total"] < 10: continue # Skip noise
            rate = m["drift"] / m["total"]
            risk = rate / base_rate if base_rate > 0 else 0
            print(f"{k:<25} {m['total']:<10} {rate:.1%}{'':<5} {risk:.2f}x")
        print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        data = json.load(f)
        
    analyze_drift(data)

if __name__ == "__main__":
    main()
