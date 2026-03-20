#!/usr/bin/env python3
"""
Generate a Sankey diagram showing Human Role → AI Role flows for V2 Unified (N=2577).

Uses the dominant (highest probability) role from each conversation's
classification distribution.
"""

import json
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Role display names
HUMAN_ROLES = {
    'information-seeker': 'Information-Seeker',
    'provider': 'Provider',
    'director': 'Director',
    'collaborator': 'Collaborator',
    'social-expressor': 'Social-Expressor',
    'relational-peer': 'Relational-Peer',
}

AI_ROLES = {
    'expert-system': 'Expert-System',
    'learning-facilitator': 'Learning-Facilitator',
    'advisor': 'Advisor',
    'co-constructor': 'Co-Constructor',
    'social-facilitator': 'Social-Facilitator',
    'relational-peer': 'Relational-Peer',
}

# Colors
HUMAN_COLORS = {
    'information-seeker': '#4A90D9',
    'provider': '#5BA85B',
    'director': '#E67E22',
    'collaborator': '#9B59B6',
    'social-expressor': '#E74C3C',
    'relational-peer': '#1ABC9C',
}

AI_COLORS = {
    'expert-system': '#2C3E50',
    'learning-facilitator': '#27AE60',
    'advisor': '#F39C12',
    'co-constructor': '#8E44AD',
    'social-facilitator': '#C0392B',
    'relational-peer': '#16A085',
}


def load_conversations():
    """Load conversations from V2 unified dataset."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data' / 'v2_unified' / 'conversations'
    
    print(f"Loading conversations from {data_dir}...")

    conversations = []
    
    files = list(data_dir.glob('*.json'))
    print(f"Found {len(files)} JSON files.")
    
    for f in files:
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
            
        classification = data.get('classification') or {}
        human_role_obj = classification.get('humanRole') or {}
        ai_role_obj = classification.get('aiRole') or {}
        human_dist = human_role_obj.get('distribution', {})
        ai_dist = ai_role_obj.get('distribution', {})

        # Normalize AI roles
        if 'facilitator' in ai_dist:
            val = ai_dist.pop('facilitator')
            ai_dist['learning-facilitator'] = ai_dist.get('learning-facilitator', 0) + val

        # Get dominant roles
        human_role = max(human_dist, key=human_dist.get) if human_dist else None
        ai_role = max(ai_dist, key=ai_dist.get) if ai_dist else None

        if human_role and ai_role:
            # Map any unexpected roles if necessary (or skip)
            if human_role not in HUMAN_ROLES:
                # print(f"Skipping unknown human role: {human_role}")
                continue
            if ai_role not in AI_ROLES:
                # print(f"Skipping unknown AI role: {ai_role}")
                continue
                
            conversations.append((human_role, ai_role))

    return conversations


def draw_sankey(flows, output_path):
    """Draw a Sankey diagram of human→AI role flows."""
    # Count flows
    flow_counts = defaultdict(int)
    for h, a in flows:
        flow_counts[(h, a)] += 1

    total = len(flows)

    # Get unique roles in order of frequency
    human_counts = defaultdict(int)
    ai_counts = defaultdict(int)
    for h, a in flows:
        human_counts[h] += 1
        ai_counts[a] += 1

    human_order = sorted(human_counts, key=human_counts.get, reverse=True)
    ai_order = sorted(ai_counts, key=ai_counts.get, reverse=True)

    # Layout parameters
    fig, ax = plt.subplots(figsize=(14, 8))

    left_x = 0.15
    right_x = 0.85
    node_width = 0.04
    y_padding = 0.02
    min_height = 0.008

    # Calculate node heights (proportional to count)
    usable_height = 1.0 - (max(len(human_order), len(ai_order)) + 1) * y_padding

    def compute_positions(order, counts):
        total_count = sum(counts[r] for r in order)
        positions = {}
        y = 1.0 - y_padding
        for role in order:
            h = max(counts[role] / total_count * usable_height, min_height)
            positions[role] = (y - h, y, h)
            y -= h + y_padding
        return positions

    human_pos = compute_positions(human_order, human_counts)
    ai_pos = compute_positions(ai_order, ai_counts)

    # Track how much of each node has been used for flows
    human_used = {r: 0.0 for r in human_order}
    ai_used = {r: 0.0 for r in ai_order}

    # Sort flows by size (draw largest first for better visibility)
    sorted_flows = sorted(flow_counts.items(), key=lambda x: x[1], reverse=True)

    # Draw flows
    for (h_role, a_role), count in sorted_flows:
        if count == 0:
            continue

        h_bottom, h_top, h_height = human_pos[h_role]
        a_bottom, a_top, a_height = ai_pos[a_role]

        # Flow height proportional to count relative to source node
        flow_h_height = (count / human_counts[h_role]) * h_height
        flow_a_height = (count / ai_counts[a_role]) * a_height

        # Starting Y positions within each node
        h_y_start = h_top - human_used[h_role]
        h_y_end = h_y_start - flow_h_height
        a_y_start = a_top - ai_used[a_role]
        a_y_end = a_y_start - flow_a_height

        human_used[h_role] += flow_h_height
        ai_used[a_role] += flow_a_height

        # Draw curved flow
        color = HUMAN_COLORS.get(h_role, '#AAAAAA')
        alpha = max(0.15, min(0.6, count / total * 8))

        n_points = 50
        t = np.linspace(0, 1, n_points)
        x_vals = left_x + node_width + t * (right_x - left_x - node_width)
        # Cubic bezier for smooth curve
        top_y = (1 - t)**3 * h_y_start + 3*(1-t)**2*t * h_y_start + 3*(1-t)*t**2 * a_y_start + t**3 * a_y_start
        bot_y = (1 - t)**3 * h_y_end + 3*(1-t)**2*t * h_y_end + 3*(1-t)*t**2 * a_y_end + t**3 * a_y_end

        ax.fill_between(x_vals, bot_y, top_y, color=color, alpha=alpha, linewidth=0)

    # Draw nodes
    for role in human_order:
        bottom, top, height = human_pos[role]
        color = HUMAN_COLORS.get(role, '#AAAAAA')
        rect = mpatches.FancyBboxPatch(
            (left_x, bottom), node_width, height,
            boxstyle="round,pad=0.003", facecolor=color, edgecolor='white', linewidth=1.5
        )
        ax.add_patch(rect)
        # Label
        label = HUMAN_ROLES.get(role, role)
        count = human_counts[role]
        pct = count / total * 100
        ax.text(left_x - 0.01, bottom + height / 2,
                f'{label}\n({count}, {pct:.0f}%)',
                ha='right', va='center', fontsize=9, fontweight='bold', color=color)

    for role in ai_order:
        bottom, top, height = ai_pos[role]
        color = AI_COLORS.get(role, '#AAAAAA')
        rect = mpatches.FancyBboxPatch(
            (right_x, bottom), node_width, height,
            boxstyle="round,pad=0.003", facecolor=color, edgecolor='white', linewidth=1.5
        )
        ax.add_patch(rect)
        label = AI_ROLES.get(role, role)
        count = ai_counts[role]
        pct = count / total * 100
        ax.text(right_x + node_width + 0.01, bottom + height / 2,
                f'{label}\n({count}, {pct:.0f}%)',
                ha='left', va='center', fontsize=9, fontweight='bold', color=color)

    # Headers
    ax.text(left_x + node_width / 2, 1.02, 'Human Role',
            ha='center', va='bottom', fontsize=13, fontweight='bold', color='#333')
    ax.text(right_x + node_width / 2, 1.02, 'AI Role',
            ha='center', va='bottom', fontsize=13, fontweight='bold', color='#333')

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.02, 1.08)
    ax.axis('off')
    ax.set_title(f'Human → AI Role Flows ({total} conversations)',
                 fontsize=15, fontweight='bold', pad=20, color='#222')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Sankey saved to: {output_path}")

    # Print flow table
    print(f"\nTop 15 role pairings (of {len(flow_counts)}):")
    for (h, a), count in sorted_flows[:15]:
        pct = count / total * 100
        print(f"  {HUMAN_ROLES.get(h, h):22s} → {AI_ROLES.get(a, a):22s}  {count:4d} ({pct:5.1f}%)")


if __name__ == '__main__':
    conversations = load_conversations()
    print(f"Loaded {len(conversations)} conversations with role pairs")

    output = Path(__file__).parent.parent / 'paper' / 'figures' / 'role_sankey_all.png'
    draw_sankey(conversations, output)
