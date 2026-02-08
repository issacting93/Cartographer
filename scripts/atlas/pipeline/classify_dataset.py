#!/usr/bin/env python3
"""
Dataset Classifier for CUI 2026 Paper
Implements the 4-layer classification scheme from Dataset_Classification_Plan.md

Usage:
    python classify_dataset.py --input ./data/conversations --output ./data/classified
"""

import os
import json
import re
import argparse
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Literal
from datetime import datetime
from pathlib import Path


# ============= Layer 1: Interaction Metadata =============

@dataclass
class InteractionMetadata:
    id: str
    source: Literal["WildChat", "ChatbotArena", "OASST"]
    total_turns: int
    domain: Literal["career", "travel", "code", "education", "creative", "general", "other"]
    task_complexity: Literal["single-goal", "multi-goal", "exploratory"]
    file_path: str


# ============= Layer 2: Turn-Level Coding =============

@dataclass
class TurnCoding:
    turn_number: int
    speaker: Literal["user", "assistant"]
    
    # Constraint Events
    constraint_stated: bool = False
    constraint_type: Optional[Literal["goal", "hard", "soft", "preference"]] = None
    constraint_text: Optional[str] = None
    
    # Violation Events
    constraint_violated: bool = False
    violated_constraint_id: Optional[str] = None
    violation_type: Optional[Literal["direct", "drift", "implicit"]] = None
    
    # Repair Events
    repair_attempted: bool = False
    repair_type: Optional[Literal["restatement", "reference", "redirect", "abandon"]] = None
    repair_success: Optional[bool] = None
    
    # Agency Markers
    user_specificity: int = 3  # 1-5 scale
    user_stance: Literal["directive", "collaborative", "passive", "reactive"] = "collaborative"
    passive_acceptance: bool = False


# ============= Layer 3: Trajectory Metrics =============

@dataclass
class TrajectoryMetrics:
    # Agency Collapse Metrics
    initial_specificity: float = 0.0
    final_specificity: float = 0.0
    specificity_delta: float = 0.0
    collapse_detected: bool = False
    
    # Constraint Maintenance
    constraints_stated: int = 0
    constraints_violated: int = 0
    constraint_half_life: float = 0.0
    restatement_count: int = 0
    restatement_loops: int = 0
    
    # Outcome
    task_completed: Optional[bool] = None
    aci_score: float = 0.0  # Agency Collapse Index


# ============= Layer 4: Archetype =============

@dataclass
class ClassifiedInteraction:
    metadata: InteractionMetadata
    turns: List[TurnCoding]
    trajectory: TrajectoryMetrics
    archetype: Literal["Provider Trap", "Hallucination Loop", "Identity Shift", 
                       "Canvas Hack", "Passive Default", "Mixed/Other"]
    archetype_confidence: float = 0.0
    annotator_notes: str = ""


# ============= Classification Functions =============

def detect_domain(text: str) -> str:
    """Classify interaction domain based on content."""
    text_lower = text.lower()
    
    domain_keywords = {
        "career": ["job", "resume", "interview", "salary", "hire", "work-life", "remote", "career", "position", "employer"],
        "travel": ["flight", "hotel", "trip", "vacation", "travel", "booking", "itinerary", "destination"],
        "code": ["code", "function", "debug", "error", "python", "javascript", "api", "database", "implement"],
        "education": ["learn", "explain", "teach", "understand", "study", "homework", "course", "lecture"],
        "creative": ["write", "story", "poem", "essay", "creative", "fiction", "character", "plot"],
    }
    
    scores = {domain: 0 for domain in domain_keywords}
    for domain, keywords in domain_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                scores[domain] += 1
    
    max_domain = max(scores, key=scores.get)
    return max_domain if scores[max_domain] >= 2 else "general"


def calculate_specificity(text: str) -> int:
    """Calculate user specificity on 1-5 scale."""
    if not text or len(text.strip()) < 5:
        return 1
    
    text_lower = text.lower().strip()
    
    # Level 1: Vague/empty
    if text_lower in ["ok", "sure", "yes", "thanks", "got it", "alright"]:
        return 1
    
    # Count specificity indicators
    specificity_score = 2  # Baseline
    
    # Quantifiers add specificity
    if any(q in text for q in ["$", "max", "min", "at least", "no more than", "exactly", "hours", "days"]):
        specificity_score += 1
    
    # Requirements/constraints add specificity
    if any(r in text_lower for r in ["must", "need to", "require", "only", "never", "always"]):
        specificity_score += 1
    
    # Detailed text adds specificity
    if len(text) > 200:
        specificity_score += 1
    
    return min(specificity_score, 5)


def detect_constraint(text: str) -> tuple[bool, Optional[str], Optional[str]]:
    """Detect if text contains a constraint statement."""
    constraint_patterns = [
        (r"(must|need to|require|only|never|always|no more than|at least|max|min)\s+(.{10,50})", "hard"),
        (r"(prefer|ideally|if possible|would like)\s+(.{10,50})", "soft"),
        (r"(my goal|i want to|looking to|trying to)\s+(.{10,50})", "goal"),
        (r"(budget|salary|hours|deadline|remote|in-person)\s*(is|of|around)?\s*(.{5,30})", "hard"),
    ]
    
    for pattern, ctype in constraint_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return True, ctype, match.group(0)[:100]
    
    return False, None, None


def detect_passive_acceptance(text: str) -> bool:
    """Detect passive acceptance phrases."""
    passive_phrases = [
        "ok", "okay", "sure", "alright", "got it", "i see", "thanks",
        "great", "perfect", "sounds good", "that works", "fine",
    ]
    text_lower = text.lower().strip()
    # Short responses that are just acceptance
    return len(text_lower) < 30 and any(text_lower.startswith(p) for p in passive_phrases)


def calculate_aci(trajectory: TrajectoryMetrics) -> float:
    """
    Calculate Agency Collapse Index.
    ACI = (Specificity_Δ × -1) + (Restatement_Count × 0.5) + (Violation_Acceptance × 2)
    """
    violation_acceptance = 0.0
    if trajectory.constraints_violated > 0:
        repaired = trajectory.restatement_count
        violation_acceptance = max(0, trajectory.constraints_violated - repaired) / trajectory.constraints_violated
    
    aci = (trajectory.specificity_delta * -1) + (trajectory.restatement_count * 0.5) + (violation_acceptance * 2)
    return round(aci, 2)


def assign_archetype(trajectory: TrajectoryMetrics, turns: List[TurnCoding]) -> tuple[str, float]:
    """Assign archetype based on trajectory patterns."""
    
    # Check for Canvas Hack: same constraint text appears 3+ times
    constraint_texts = [t.constraint_text for t in turns if t.constraint_text]
    from collections import Counter
    text_counts = Counter(constraint_texts)
    if any(count >= 3 for count in text_counts.values()):
        return "Canvas Hack", 0.9
    
    # Check for Hallucination Loop: 3+ sequential repair attempts
    repair_sequence = 0
    max_repair_sequence = 0
    for t in turns:
        if t.repair_attempted:
            repair_sequence += 1
            max_repair_sequence = max(max_repair_sequence, repair_sequence)
        else:
            repair_sequence = 0
    if max_repair_sequence >= 3:
        return "Hallucination Loop", 0.85
    
    # Check for Provider Trap: high initial specificity → collapse
    if trajectory.initial_specificity >= 4 and trajectory.collapse_detected:
        return "Provider Trap", 0.8
    
    # Check for Passive Default: low specificity throughout
    user_turns = [t for t in turns if t.speaker == "user"]
    avg_specificity = sum(t.user_specificity for t in user_turns) / len(user_turns) if user_turns else 3
    if avg_specificity < 2:
        return "Passive Default", 0.75
    
    # Check for Identity Shift: tone degradation (simplified)
    # Would need more sophisticated sentiment analysis
    
    return "Mixed/Other", 0.5


def classify_conversation(filepath: Path) -> Optional[ClassifiedInteraction]:
    """Classify a single conversation file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    # Extract messages (handle different formats)
    messages = data.get("messages", data.get("conversation", []))
    if not messages or len(messages) < 10:
        return None
    
    # Determine source from path or metadata
    source = "WildChat"  # Default
    if "arena" in str(filepath).lower():
        source = "ChatbotArena"
    elif "oasst" in str(filepath).lower():
        source = "OASST"
    
    # Combine all user text for domain detection
    all_user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
    domain = detect_domain(all_user_text)
    
    # Code each turn
    turns = []
    constraints_found = []
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role not in ["user", "assistant"]:
            continue
        
        turn = TurnCoding(
            turn_number=i + 1,
            speaker=role,
        )
        
        if role == "user":
            # Specificity
            turn.user_specificity = calculate_specificity(content)
            turn.passive_acceptance = detect_passive_acceptance(content)
            
            # Constraint detection
            has_constraint, ctype, ctext = detect_constraint(content)
            if has_constraint:
                turn.constraint_stated = True
                turn.constraint_type = ctype
                turn.constraint_text = ctext
                constraints_found.append((i, ctext))
            
            # Stance detection (simplified)
            if turn.user_specificity >= 4:
                turn.user_stance = "directive"
            elif turn.passive_acceptance:
                turn.user_stance = "passive"
            else:
                turn.user_stance = "collaborative"
        
        turns.append(turn)
    
    if not turns:
        return None
    
    # Calculate trajectory metrics
    user_turns = [t for t in turns if t.speaker == "user"]
    
    # Specificity trajectory
    initial_turns = user_turns[:3] if len(user_turns) >= 3 else user_turns
    final_turns = user_turns[-3:] if len(user_turns) >= 3 else user_turns
    
    initial_spec = sum(t.user_specificity for t in initial_turns) / len(initial_turns) if initial_turns else 3
    final_spec = sum(t.user_specificity for t in final_turns) / len(final_turns) if final_turns else 3
    
    trajectory = TrajectoryMetrics(
        initial_specificity=round(initial_spec, 2),
        final_specificity=round(final_spec, 2),
        specificity_delta=round(final_spec - initial_spec, 2),
        collapse_detected=(final_spec - initial_spec) < -1.0,
        constraints_stated=len(constraints_found),
        restatement_count=sum(1 for t in turns if t.repair_type == "restatement"),
    )
    
    trajectory.aci_score = calculate_aci(trajectory)
    
    # Assign archetype
    archetype, confidence = assign_archetype(trajectory, turns)
    
    # Task complexity
    if len(constraints_found) <= 1:
        complexity = "single-goal"
    elif len(constraints_found) <= 3:
        complexity = "multi-goal"
    else:
        complexity = "exploratory"
    
    metadata = InteractionMetadata(
        id=filepath.stem,
        source=source,
        total_turns=len(turns),
        domain=domain,
        task_complexity=complexity,
        file_path=str(filepath),
    )
    
    return ClassifiedInteraction(
        metadata=metadata,
        turns=turns,
        trajectory=trajectory,
        archetype=archetype,
        archetype_confidence=confidence,
    )


def main():
    parser = argparse.ArgumentParser(description="Classify CUI dataset for Agency Collapse analysis")
    parser.add_argument("--input", "-i", required=True, help="Input directory with conversation JSONs")
    parser.add_argument("--output", "-o", required=True, help="Output directory for classified data")
    parser.add_argument("--sample", "-s", type=int, default=None, help="Sample N conversations (random)")
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files
    json_files = list(input_dir.glob("**/*.json"))
    print(f"Found {len(json_files)} JSON files")
    
    # Sample if requested
    if args.sample:
        import random
        json_files = random.sample(json_files, min(args.sample, len(json_files)))
        print(f"Sampled {len(json_files)} files")
    
    # Classify each
    results = []
    archetype_counts = {}
    domain_counts = {}
    
    for i, fp in enumerate(json_files):
        if i % 100 == 0:
            print(f"Processing {i}/{len(json_files)}...")
        
        classified = classify_conversation(fp)
        if classified:
            results.append(classified)
            
            # Track distributions
            archetype_counts[classified.archetype] = archetype_counts.get(classified.archetype, 0) + 1
            domain_counts[classified.metadata.domain] = domain_counts.get(classified.metadata.domain, 0) + 1
    
    print(f"\n✅ Classified {len(results)} conversations")
    
    # Summary statistics
    print("\n📊 Archetype Distribution:")
    for arch, count in sorted(archetype_counts.items(), key=lambda x: -x[1]):
        pct = count / len(results) * 100
        print(f"  {arch}: {count} ({pct:.1f}%)")
    
    print("\n📊 Domain Distribution:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        pct = count / len(results) * 100
        print(f"  {domain}: {count} ({pct:.1f}%)")
    
    # ACI statistics
    aci_scores = [r.trajectory.aci_score for r in results]
    avg_aci = sum(aci_scores) / len(aci_scores)
    collapse_rate = sum(1 for r in results if r.trajectory.collapse_detected) / len(results) * 100
    
    print(f"\n📊 Agency Collapse Metrics:")
    print(f"  Mean ACI: {avg_aci:.2f}")
    print(f"  Collapse Rate: {collapse_rate:.1f}%")
    
    # Save results
    output_file = output_dir / "classified_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        # Convert dataclasses to dicts
        serializable = []
        for r in results:
            d = {
                "metadata": asdict(r.metadata),
                "trajectory": asdict(r.trajectory),
                "archetype": r.archetype,
                "archetype_confidence": r.archetype_confidence,
                "turn_count": len(r.turns),
            }
            serializable.append(d)
        json.dump(serializable, f, indent=2)
    
    print(f"\n💾 Saved to {output_file}")
    
    # Generate summary for paper
    summary_file = output_dir / "paper_statistics.md"
    with open(summary_file, 'w') as f:
        f.write("# Dataset Classification Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**N:** {len(results)}\n\n")
        f.write("## Archetype Distribution\n\n")
        f.write("| Archetype | N | % |\n|-----------|---|---|\n")
        for arch, count in sorted(archetype_counts.items(), key=lambda x: -x[1]):
            pct = count / len(results) * 100
            f.write(f"| {arch} | {count} | {pct:.1f}% |\n")
        f.write(f"\n## Agency Collapse Index\n\n")
        f.write(f"- **Mean ACI:** {avg_aci:.2f}\n")
        f.write(f"- **Collapse Rate:** {collapse_rate:.1f}%\n")
    
    print(f"📄 Paper statistics saved to {summary_file}")


if __name__ == "__main__":
    main()
