#!/ intent/python3
"""
Atlas Technical Evaluation: Sampler and Exporter
Samples N=100 conversations from the canonical corpus for manual annotation.
"""

import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPHS_DIR = PROJECT_ROOT / "data" / "atlas_canonical" / "graphs"
OUTPUT_FILE = PROJECT_ROOT / "data" / "v2_unified" / "eval" / "annotation_sample_100.json"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

def sample_conversations(n=100):
    all_files = list(GRAPHS_DIR.glob("*.json"))
    # Skip error files
    valid_files = [f for f in all_files if "-error" not in f.name]
    
    print(f"Total valid graphs: {len(valid_files)}")
    sample = random.sample(valid_files, min(n, len(valid_files)))
    
    export_data = []
    for f in sample:
        with open(f) as fh:
            graph = json.load(fh)
            
        conv_id = f.stem
        # Map graph ID to source conversation file
        source_file = PROJECT_ROOT / "data" / "v2_unified" / "conversations" / f"{conv_id}.json"
        
        full_transcript = []
        if source_file.exists():
            print(f"Loading source: {source_file}")
            with open(source_file) as sfh:
                source_data = json.load(sfh)
                # Handle different source formats
                if isinstance(source_data, list):
                    items = source_data
                else:
                    items = source_data.get("messages", source_data.get("conversation", source_data.get("items", [])))
                
                for item in items:
                    role = item.get("role")
                    content = item.get("content") or item.get("text") or item.get("value")
                    if role and content:
                        full_transcript.append({"role": role, "content": content})
        else:
            print(f"MISSING source file: {source_file}")
        
        # Atlas findings to be validated
        nodes = graph.get("nodes", [])
        constraints = [n for n in nodes if n.get("node_type") == "Constraint"]
        violations = [n for n in nodes if n.get("node_type") == "ViolationEvent"]
        
        export_data.append({
            "id": conv_id,
            "transcript": full_transcript if full_transcript else "TRANSCRIPT_MISSING",
            "atlas_findings": {
                "constraints": [
                    {"id": c.get("constraint_id"), "text": c.get("text"), "type": c.get("constraint_type")}
                    for c in constraints
                ],
                "violations": [
                    {"turn_index": v.get("turn_index"), "constraint_id": v.get("constraint_id")}
                    for v in violations
                ]
            },
            "labels": {
                "correct_constraints": [], 
                "missing_constraints": [],
                "correct_violations": [],
                "false_violations": []
            }
        })
        
    with open(OUTPUT_FILE, "w") as fh:
        json.dump(export_data, fh, indent=2)
        
    print(f"Sampled {len(export_data)} conversations to {OUTPUT_FILE}")

if __name__ == "__main__":
    sample_conversations(100)
