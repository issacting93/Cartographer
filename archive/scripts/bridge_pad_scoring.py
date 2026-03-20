#!/usr/bin/env python3
"""
Bridge PAD Scoring: Atlas Edition
--------------------------------
Applies the "Conversational Cartography" PAD scoring logic (Phenomenological)
to the "Agency Collapse" Graph dataset (Structural).

Usage:
    python3 scripts/analysis/bridge_pad_scoring.py --limit 10
    python3 scripts/analysis/bridge_pad_scoring.py --all
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)

# Configuration
MODEL = "gpt-4o-mini"
INPUT_DIR = Path("data/atlas_canonical/graphs")
OUTPUT_DIR = Path("data/atlas_with_pad")

def get_openai_client() -> OpenAI:
    """Get OpenAI client, checking for API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set in .env")
        sys.exit(1)
    return OpenAI(api_key=api_key)

def extract_linear_conversation(graph_data: Dict) -> List[Dict]:
    """
    Extracts a linear sequence of messages from the Graph JSON.
    Returns a list of dicts: {'role': 'user'|'assistant', 'content': '...'}
    """
    nodes = graph_data.get("nodes", [])
    
    # Filter for Turn nodes
    turn_nodes = [n for n in nodes if n.get("node_type") == "Turn"]
    
    # Sort by turn_index
    turn_nodes.sort(key=lambda x: x.get("turn_index", 0))
    
    messages = []
    for turn in turn_nodes:
        role = turn.get("role", "unknown")
        # Find the content. In Graph, content might be in 'content_preview' or we might look for a Move?
        # Looking at chatbot_arena_0003.json, 'content_preview' seems to have the text.
        # But wait, content_preview is truncated? No, for shorter messages it looks full.
        # Let's check if there's a better source. 
        # Actually, in the graph structure, the full content might be on the node or inferred.
        # For this bridge script, content_preview is likely sufficient for PAD analysis 
        # if the full content isn't explicitly stored elsewhere in this simplified graph view.
        # However, looking at node_type="Move", there's "text_span". 
        # Let's use 'content_preview' for now as it maps 1:1 to turns.
        content = turn.get("content_preview", "")
        
        # Clean up "Model A : " prefixes if they exist (artifact of some datasets)
        if content.startswith("Model A :") or content.startswith("Model B :"):
            content = content.split(":", 1)[1].strip()
            
        messages.append({
            "role": role,
            "content": content,
            "turn_index": turn.get("turn_index")
        })
        
    return messages

def generate_pad_batch(client: OpenAI, messages: List[Dict]) -> Optional[List[Dict]]:
    """
    Sends conversation to LLM to get PAD values.
    Adapted from Convo-topo's generate-pad-with-llm-direct.py
    """
    if not messages:
        return None
        
    formatted_history = ""
    for msg in messages:
        role = msg.get('role', 'user').upper()
        content = msg.get('content', '')
        # Truncate content for prompt efficiency
        if len(content) > 500:
            content = content[:500] + "..."
        formatted_history += f"[{msg['turn_index']}] {role}: {content}\n"

    system_prompt = f"""You are an expert behavioral psychologist specializing in the PAD (Pleasure-Arousal-Dominance) emotional model.
Analyze the conversation and provide PAD scores (0.0 to 1.0) for EVERY message.

DIMENSIONS:
- Pleasure (P): Valence. 0=Negative, 1=Positive.
- Arousal (A): Activation. 0=Calm, 1=Excited/Agitated.
- Dominance (D): Control. 0=Submissive, 1=Dominant.

CRITICAL RULES:
1. Repair attempts (repeating constraints) -> High Arousal, Low Pleasure.
2. Apologies -> Low Dominance, Low Pleasure.
3. Successful task completion -> High Pleasure, Moderate Arousal.
4. Authority escalation ("I cannot do that") -> High Dominance, Low Pleasure.

OUTPUT FORMAT:
Return a JSON object with a "pad_scores" array. The array MUST contain exactly {len(messages)} objects.
Each object: {{ "p": 0.5, "a": 0.5, "d": 0.5 }}
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
        
        result = json.loads(response.choices[0].message.content)
        return result.get("pad_scores", [])
        
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return None

def inject_pad_scores(graph_data: Dict, pad_scores: List[Dict]) -> Dict:
    """
    Injects PAD scores back into the Graph Turn nodes.
    """
    nodes = graph_data.get("nodes", [])
    
    # Map PAD scores by index (assuming 1:1 mapping with sorted turns)
    # We extracted based on sorted turn_index, so simple indexing should work 
    # IF the pad_scores array length matches.
    
    # Filter Turn nodes again to get their references
    turn_nodes = [n for n in nodes if n.get("node_type") == "Turn"]
    turn_nodes.sort(key=lambda x: x.get("turn_index", 0))
    
    if len(pad_scores) != len(turn_nodes):
        print(f"⚠️ Mismatch: {len(pad_scores)} scores for {len(turn_nodes)} turns.")
        # Best effort mapping? Or just truncate/pad?
        # Let's truncate/pad safely.
        pass

    for i, turn in enumerate(turn_nodes):
        if i < len(pad_scores):
            score = pad_scores[i]
            # Calculate Intensity (Z-axis)
            # Formula: (1 - P) * 0.6 + A * 0.4
            p = score.get('p', 0.5)
            a = score.get('a', 0.5)
            d = score.get('d', 0.5)
            intensity = round(((1 - p) * 0.6) + (a * 0.4), 3)
            
            turn['pad_attributes'] = {
                'pleasure': p,
                'arousal': a,
                'dominance': d,
                'emotional_intensity': intensity
            }
            
    return graph_data

def process_file(file_path: Path, client: OpenAI):
    """Process a single file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        messages = extract_linear_conversation(data)
        if not messages:
            print(f"⏩ Skipping {file_path.name} (no messages)")
            return
            
        print(f"🧠 Scoring {file_path.name} ({len(messages)} turns)...")
        pad_scores = generate_pad_batch(client, messages)
        
        if pad_scores:
            updated_data = inject_pad_scores(data, pad_scores)
            
            output_path = OUTPUT_DIR / file_path.name
            with open(output_path, 'w') as f:
                json.dump(updated_data, f, indent=2)
            print(f"✅ Saved to {output_path}")
        else:
            print(f"❌ Failed to generate scores for {file_path.name}")
            
    except Exception as e:
        print(f"❌ Error extracting/processing {file_path.name}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, help='Limit number of files')
    parser.add_argument('--all', action='store_true', help='Process all files')
    args = parser.parse_args()

    if not INPUT_DIR.exists():
        print(f"❌ Input directory not found: {INPUT_DIR}")
        return
        
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    client = get_openai_client()
    files = list(INPUT_DIR.glob("*.json"))
    
    if args.limit:
        files = files[:args.limit]
    
    print(f"📂 Processing {len(files)} files from {INPUT_DIR}")
    
    for file_path in files:
        process_file(file_path, client)

if __name__ == "__main__":
    main()
