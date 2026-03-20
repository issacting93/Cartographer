#!/usr/bin/env python3
"""
Download OpenAssistant conversations, building proper conversation trees.

Usage:
    python3 scripts/download_oasst.py [--limit N] [--min-messages N]
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datasets import load_dataset


def build_conversation_trees(dataset, min_messages: int = 4, max_conversations: Optional[int] = None):
    """Build conversation trees from OpenAssistant dataset."""
    messages_by_id: Dict[str, Dict[str, Any]] = {}

    print("  Building message tree...")
    for item in dataset:
        message_id = item.get('message_id')
        parent_id = item.get('parent_id')
        text = item.get('text', '').strip()
        role = item.get('role', 'user')

        if not text or not message_id:
            continue
        if role == 'prompter':
            role = 'user'
        elif role != 'assistant':
            continue

        messages_by_id[message_id] = {
            'id': message_id,
            'parent_id': parent_id,
            'text': text,
            'role': role,
            'children': []
        }

    for msg_id, msg in messages_by_id.items():
        if msg['parent_id'] and msg['parent_id'] in messages_by_id:
            messages_by_id[msg['parent_id']]['children'].append(msg_id)

    root_messages = [msg for msg in messages_by_id.values() if not msg['parent_id']]
    print(f"  Found {len(root_messages)} root messages")

    def traverse_tree(msg_id: str, conversation: List[Dict]) -> List[Dict]:
        if msg_id not in messages_by_id:
            return conversation
        msg = messages_by_id[msg_id]
        conversation.append({'role': msg['role'], 'content': msg['text']})
        for child_id in msg['children']:
            conversation = traverse_tree(child_id, conversation)
        return conversation

    conversations = []
    for root_msg in root_messages:
        messages = traverse_tree(root_msg['id'], [])
        if len(messages) >= min_messages:
            conversations.append(messages)
            if max_conversations and len(conversations) >= max_conversations:
                break

    return conversations


def main():
    parser = argparse.ArgumentParser(description="Download OpenAssistant conversations")
    parser.add_argument("--limit", type=int, default=500, help="Max conversations")
    parser.add_argument("--min-messages", type=int, default=4, help="Minimum messages per conversation")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / 'data' / 'conversations_raw'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("OpenAssistant Downloader")
    print(f"  Min messages: {args.min_messages}")
    print(f"  Limit: {args.limit}")
    print("=" * 60)

    print("\n  Loading dataset...")
    dataset = load_dataset("OpenAssistant/oasst1", split="train")

    conversations_list = build_conversation_trees(
        dataset, min_messages=args.min_messages, max_conversations=args.limit
    )

    saved = 0
    for i, messages in enumerate(conversations_list):
        conv_id = f"oasst-{i:04d}"
        conv = {
            "id": conv_id,
            "source": "oasst",
            "messages": messages
        }
        file_path = output_dir / f"{conv_id}.json"
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conv, f, indent=2, ensure_ascii=False)
            saved += 1
            print(f"  Saved {conv_id}: {len(messages)} messages")

    print(f"\nSaved {saved} new conversations")


if __name__ == "__main__":
    main()
