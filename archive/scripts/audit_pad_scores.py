
import json
import random
from pathlib import Path
from collections import defaultdict
import numpy as np

def analyze_pad_variance(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return f"Error loading: {e}"

    if 'messages' not in data:
        return "No messages"

    pads = []
    for m in data['messages']:
        if 'pad' in m and m['pad']:
            pads.append(tuple(sorted(m['pad'].items())))
    
    if not pads:
        return "No PAD scores"

    unique_pads = set(pads)
    is_static = len(unique_pads) <= 1
    
    return {
        "id": data.get("id", "unknown"),
        "source": data.get("source", "unknown"),
        "msg_count": len(data['messages']),
        "pad_count": len(pads),
        "unique_pads": len(unique_pads),
        "is_static": is_static,
        "sample": list(unique_pads)[:1] if unique_pads else []
    }

def main():
    data_dir = Path('/Users/zac/Documents/Documents-it/GitHub/Cartography_v2/data/v2_unified/conversations')
    all_files = list(data_dir.glob('*.json'))
    
    print(f"Total files found: {len(all_files)}")
    
    if len(all_files) < 20:
        sample = all_files
    else:
        sample = random.sample(all_files, 20)
    
    print(f"\nAnalyzing {len(sample)} random files...\n")
    print(f"{'ID':<35} | {'Source':<15} | {'Static?':<8} | {'Unique/Total'}")
    print("-" * 80)
    
    static_count = 0
    for p in sample:
        res = analyze_pad_variance(p)
        if isinstance(res, str):
            print(f"{p.name:<35} | ERROR: {res}")
            continue
            
        static_str = "YES" if res['is_static'] else "NO"
        if res['is_static']:
            static_count += 1
            
        print(f"{res['id']:<35} | {res['source']:<15} | {static_str:<8} | {res['unique_pads']}/{res['pad_count']}")

    print("-" * 80)
    print(f"Summary: {static_count}/{len(sample)} files have completely static PAD scores.")

if __name__ == "__main__":
    main()
