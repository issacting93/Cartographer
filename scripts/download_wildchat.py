#!/usr/bin/env python3
"""
Download and process conversations from WildChat-1M dataset.
WildChat contains 838k conversations from ChatGPT interactions in the wild.

Usage:
    python3 scripts/download_wildchat.py [--max N] [--min-messages N] [--max-messages N]
"""

import json
import hashlib
import argparse
import random
from pathlib import Path
from typing import Dict, List, Optional
from datasets import load_dataset


def load_wildchat_dataset(split: str = 'train', max_conversations: Optional[int] = None):
    """Load WildChat dataset from HuggingFace."""
    print(f"Loading WildChat dataset (split: {split})...")
    dataset = load_dataset("allenai/WildChat-1M", split=split)
    print(f"Loaded {len(dataset)} conversations")

    if max_conversations and len(dataset) > max_conversations:
        indices = random.sample(range(len(dataset)), max_conversations)
        dataset = dataset.select(indices)
        print(f"Sampled {max_conversations} conversations")

    return dataset


def convert_wildchat_to_our_format(wildchat_conv: Dict) -> Optional[Dict]:
    """Convert WildChat conversation format to our format."""
    conversation = wildchat_conv.get('conversation', [])
    if not conversation or len(conversation) < 2:
        return None

    messages = []
    for turn in conversation:
        role = turn.get('role', '')
        content = turn.get('content', '')
        if role in ['user', 'assistant'] and content:
            messages.append({'role': role, 'content': content})

    if len(messages) < 2:
        return None

    conv_hash = wildchat_conv.get('conversation_hash', '')
    if not conv_hash:
        content_str = ''.join([m.get('content', '') for m in messages])
        conv_hash = hashlib.md5(content_str.encode()).hexdigest()[:16]

    timestamp = wildchat_conv.get('timestamp', None)
    if timestamp and hasattr(timestamp, 'isoformat'):
        timestamp = timestamp.isoformat()

    return {
        'id': f'wildchat_{conv_hash}',
        'source': 'wildchat',
        'messages': messages,
        'metadata': {
            'model': wildchat_conv.get('model', 'unknown'),
            'timestamp': timestamp,
            'turn_count': wildchat_conv.get('turn', len(messages)),
            'language': wildchat_conv.get('language', 'unknown'),
            'toxic': wildchat_conv.get('toxic', False),
            'redacted': wildchat_conv.get('redacted', False),
        }
    }


def filter_conversations(conversations: List[Dict],
                         min_messages: int = 3,
                         max_messages: int = 50,
                         exclude_toxic: bool = True,
                         languages: Optional[List[str]] = None) -> List[Dict]:
    """Filter conversations based on criteria."""
    filtered = []
    lang_map = {
        'english': 'en', 'chinese': 'zh', 'spanish': 'es', 'french': 'fr',
        'german': 'de', 'japanese': 'ja', 'korean': 'ko', 'russian': 'ru'
    }

    for conv in conversations:
        if not conv:
            continue
        messages = conv.get('messages', [])
        metadata = conv.get('metadata', {})

        if len(messages) < min_messages or len(messages) > max_messages:
            continue
        if exclude_toxic and metadata.get('toxic', False):
            continue

        if languages:
            conv_lang = metadata.get('language', 'unknown').lower()
            if conv_lang in lang_map:
                conv_lang = lang_map[conv_lang]
            if not any(conv_lang.startswith(lang.lower()) for lang in languages):
                continue

        filtered.append(conv)

    return filtered


def main():
    parser = argparse.ArgumentParser(description="Download WildChat conversations")
    parser.add_argument("--max", type=int, default=2000, help="Max conversations to download")
    parser.add_argument("--min-messages", type=int, default=3, help="Minimum messages")
    parser.add_argument("--max-messages", type=int, default=50, help="Maximum messages")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / 'data' / 'conversations_raw'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("WildChat Dataset Downloader")
    print(f"  Max conversations: {args.max}")
    print(f"  Message range: {args.min_messages}-{args.max_messages}")
    print(f"  Output: {output_dir}")
    print("=" * 60)

    dataset = load_wildchat_dataset(split='train', max_conversations=args.max * 2)

    print("\nConverting...")
    our_conversations = []
    for i, wc in enumerate(dataset):
        if i % 500 == 0:
            print(f"  Processed {i}/{len(dataset)}...")
        conv = convert_wildchat_to_our_format(wc)
        if conv:
            our_conversations.append(conv)

    print(f"Converted {len(our_conversations)} conversations")

    filtered = filter_conversations(
        our_conversations,
        min_messages=args.min_messages,
        max_messages=args.max_messages,
        exclude_toxic=True,
        languages=['en', 'English']
    )
    print(f"Filtered to {len(filtered)} conversations")

    if len(filtered) > args.max:
        filtered = random.sample(filtered, args.max)

    saved = 0
    for conv in filtered:
        conv_id = conv.get('id', 'unknown')
        output_file = output_dir / f"{conv_id}.json"
        if not output_file.exists():
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conv, f, indent=2, ensure_ascii=False)
            saved += 1

    print(f"\nSaved {saved} new conversations to {output_dir}")


if __name__ == '__main__':
    main()
