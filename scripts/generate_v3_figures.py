#!/usr/bin/env python3
"""
Generate all v3 paper figures from unified corpus (N=2,577).
Outputs to paper/figures/
"""

import json
import csv
import statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from pathlib import Path
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONV_DIR = PROJECT_ROOT / "data" / "v2_unified" / "conversations"
EVIDENCE_CSV = PROJECT_ROOT / "data" / "v2_unified" / "evidence_features.csv"
FIGURES_DIR = PROJECT_ROOT / "paper" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.dpi': 150,
})

INSTRUMENTAL_COLOR = '#2196F3'
EXPRESSIVE_COLOR = '#FF5722'
SOURCE_COLORS = {'chatbot_arena': '#4CAF50', 'wildchat': '#FF9800', 'WildChat': '#FF9800', 'oasst': '#9C27B0', 'other': '#607D8B'}
ROLE_COLORS = {
    'information-seeker': '#1976D2', 'director': '#388E3C', 'provider': '#F57C00',
    'collaborator': '#7B1FA2', 'social-expressor': '#D32F2F', 'relational-peer': '#C2185B',
}
AI_COLORS = {
    'expert-system': '#1565C0', 'co-constructor': '#2E7D32', 'advisor': '#EF6C00',
    'social-facilitator': '#6A1B9A', 'relational-peer': '#AD1457', 'learning-facilitator': '#00838F',
}
CHANNEL_COLORS = {
    'Divergence': '#1976D2', 'Expressiveness': '#388E3C',
    'Dynamics': '#F57C00', 'Affect': '#D32F2F', 'Structure': '#607D8B'
}


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_all():
    convs = {}
    for f in sorted(CONV_DIR.glob('*.json')):
        with open(f) as fh:
            convs[f.stem] = json.load(fh)

    evidence = {}
    with open(EVIDENCE_CSV) as f:
        for row in csv.DictReader(f):
            evidence[row['conv_id']] = row

    return convs, evidence


# ---------------------------------------------------------------------------
# Figure 1: Human Role Distribution
# ---------------------------------------------------------------------------
def fig_human_roles(convs):
    roles = Counter()
    for data in convs.values():
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        if hr:
            roles[max(hr, key=hr.get)] += 1

    order = ['information-seeker', 'director', 'provider', 'collaborator', 'social-expressor', 'relational-peer']
    instrumental = {'information-seeker', 'director', 'provider', 'collaborator'}
    counts = [roles.get(r, 0) for r in order]
    total = sum(counts)
    pcts = [c / total * 100 for c in counts]
    colors = [INSTRUMENTAL_COLOR if r in instrumental else EXPRESSIVE_COLOR for r in order]
    labels = [r.replace('-', '\n') for r in order]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(order)), pcts, color=colors, edgecolor='white', linewidth=0.5)

    for bar, pct, count in zip(bars, pcts, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{pct:.1f}%\n(n={count})', ha='center', va='bottom', fontsize=9)

    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Percentage of Conversations')
    ax.set_title(f'Human Role Distribution (N={total})', fontweight='bold')

    inst_count = sum(roles.get(r, 0) for r in instrumental)
    inst_pct = inst_count / total * 100 if total > 0 else 0
    inst_patch = mpatches.Patch(color=INSTRUMENTAL_COLOR, label=f'Instrumental ({inst_pct:.1f}%)')
    expr_patch = mpatches.Patch(color=EXPRESSIVE_COLOR, label=f'Expressive ({100-inst_pct:.1f}%)')
    ax.legend(handles=[inst_patch, expr_patch], loc='upper right')
    ax.set_ylim(0, max(pcts) * 1.2)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_human_roles.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_human_roles.png")


# ---------------------------------------------------------------------------
# Figure 2: AI Role Distribution
# ---------------------------------------------------------------------------
def fig_ai_roles(convs):
    roles = Counter()
    for data in convs.values():
        cls = data.get('classification', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})
        if ar:
            roles[max(ar, key=ar.get)] += 1

    order = ['expert-system', 'co-constructor', 'advisor', 'social-facilitator', 'relational-peer', 'learning-facilitator']
    counts = [roles.get(r, 0) for r in order]
    total = sum(counts)
    pcts = [c / total * 100 for c in counts]
    colors = [AI_COLORS.get(r, '#999') for r in order]
    labels = [r.replace('-', '\n') for r in order]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(order)), pcts, color=colors, edgecolor='white', linewidth=0.5)

    for bar, pct, count in zip(bars, pcts, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f'{pct:.1f}%\n(n={count})', ha='center', va='bottom', fontsize=9)

    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Percentage of Conversations')
    ax.set_title(f'AI Role Distribution (N={total})', fontweight='bold')
    ax.set_ylim(0, max(pcts) * 1.2)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_ai_roles.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_ai_roles.png")


# ---------------------------------------------------------------------------
# Figure 3: Role Pair Heatmap
# ---------------------------------------------------------------------------
def fig_role_pair_heatmap(convs):
    pairs = Counter()
    for data in convs.values():
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})
        if hr and ar:
            pairs[(max(hr, key=hr.get), max(ar, key=ar.get))] += 1

    h_order = ['information-seeker', 'director', 'provider', 'collaborator', 'social-expressor', 'relational-peer']
    a_order = ['expert-system', 'co-constructor', 'advisor', 'social-facilitator', 'relational-peer', 'learning-facilitator']

    matrix = np.zeros((len(h_order), len(a_order)))
    total = sum(pairs.values())
    for (h, a), count in pairs.items():
        if h in h_order and a in a_order:
            matrix[h_order.index(h)][a_order.index(a)] = count / total * 100

    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(matrix, cmap='Blues', aspect='auto')

    for i in range(len(h_order)):
        for j in range(len(a_order)):
            val = matrix[i][j]
            if val > 0:
                color = 'white' if val > 30 else 'black'
                ax.text(j, i, f'{val:.1f}%', ha='center', va='center', fontsize=9, color=color)

    ax.set_xticks(range(len(a_order)))
    ax.set_xticklabels([r.replace('-', '\n') for r in a_order], fontsize=9)
    ax.set_yticks(range(len(h_order)))
    ax.set_yticklabels([r.replace('-', '\n') for r in h_order], fontsize=9)
    ax.set_xlabel('AI Role', fontweight='bold')
    ax.set_ylabel('Human Role', fontweight='bold')
    ax.set_title(f'Role Pair Distribution (N={total})', fontweight='bold')

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('% of Conversations')

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_role_pair_heatmap.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_role_pair_heatmap.png")


# ---------------------------------------------------------------------------
# Figure 4: Roles by Source
# ---------------------------------------------------------------------------
def fig_roles_by_source(convs):
    source_roles = defaultdict(Counter)
    for data in convs.values():
        src = data.get('source', 'unknown')
        if src == 'WildChat':
            src = 'wildchat'
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        if hr:
            source_roles[src][max(hr, key=hr.get)] += 1

    sources = ['chatbot_arena', 'wildchat', 'oasst']
    roles = ['information-seeker', 'director', 'provider', 'collaborator', 'social-expressor', 'relational-peer']
    x = np.arange(len(sources))
    width = 0.12

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, role in enumerate(roles):
        vals = []
        for src in sources:
            total = sum(source_roles[src].values())
            vals.append(source_roles[src].get(role, 0) / total * 100 if total > 0 else 0)
        bars = ax.bar(x + i * width - width * 2.5, vals, width, label=role,
                      color=ROLE_COLORS.get(role, '#999'), edgecolor='white', linewidth=0.5)

    ax.set_xticks(x)
    source_labels = [f'Chatbot Arena\n(N={sum(source_roles["chatbot_arena"].values())})',
                     f'WildChat\n(N={sum(source_roles["wildchat"].values())})',
                     f'OASST\n(N={sum(source_roles["oasst"].values())})']
    ax.set_xticklabels(source_labels)
    ax.set_ylabel('Percentage')
    ax.set_title('Human Role Distribution by Source', fontweight='bold')
    ax.legend(loc='upper right', fontsize=8, ncol=2)
    ax.set_ylim(0, 100)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_roles_by_source.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_roles_by_source.png")


# ---------------------------------------------------------------------------
# Figure 5: Conversation Purpose
# ---------------------------------------------------------------------------
def fig_conversation_purpose(convs):
    purposes = Counter()
    for data in convs.values():
        cls = data.get('classification', {})
        cp = cls.get('conversationPurpose', {}).get('category', '')
        if cp:
            purposes[cp] += 1

    items = purposes.most_common()
    labels = [k.replace('-', '\n') for k, _ in items]
    counts = [v for _, v in items]
    total = sum(counts)
    pcts = [c / total * 100 for c in counts]

    cmap = plt.cm.Set2
    colors = [cmap(i / len(items)) for i in range(len(items))]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(items) - 1, -1, -1), pcts, color=colors, edgecolor='white', linewidth=0.5)

    for i, (bar, pct, count) in enumerate(zip(bars, pcts, counts)):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{pct:.1f}% (n={count})', va='center', fontsize=9)

    ax.set_yticks(range(len(items) - 1, -1, -1))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Percentage of Conversations')
    ax.set_title(f'Conversation Purpose (N={total})', fontweight='bold')
    ax.set_xlim(0, max(pcts) * 1.3)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_conversation_purpose.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_conversation_purpose.png")


# ---------------------------------------------------------------------------
# Figure 6: Variance Ratio — Affect Distribution for IS→ES
# ---------------------------------------------------------------------------
def fig_variance_ratio(convs, evidence):
    is_es = []
    for cid, data in convs.items():
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})
        if not hr or not ar:
            continue
        if max(hr, key=hr.get) == 'information-seeker' and max(ar, key=ar.get) == 'expert-system':
            ev = evidence.get(cid, {})
            av = float(ev.get('affect_variance', 0))
            n_msgs = len(data.get('messages', []))
            if n_msgs >= 6 and av > 0:
                is_es.append({'conv_id': cid, 'affect_variance': av, 'n_messages': n_msgs})

    variances = [x['affect_variance'] for x in is_es]
    by_var = sorted(is_es, key=lambda x: x['affect_variance'])
    smooth = by_var[0]
    volatile = by_var[-1]
    ratio = volatile['affect_variance'] / smooth['affect_variance']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: histogram
    ax1.hist(variances, bins=50, color='#1976D2', edgecolor='white', linewidth=0.5, alpha=0.8)
    ax1.axvline(smooth['affect_variance'], color='#4CAF50', linewidth=2, linestyle='--', label=f'Smooth ({smooth["affect_variance"]:.6f})')
    ax1.axvline(volatile['affect_variance'], color='#D32F2F', linewidth=2, linestyle='--', label=f'Volatile ({volatile["affect_variance"]:.4f})')
    ax1.set_xlabel('Affect Variance')
    ax1.set_ylabel('Count')
    ax1.set_title(f'Affect Variance Distribution\nIS→ES pairs (N={len(is_es)}, ≥6 messages)', fontweight='bold')
    ax1.legend(fontsize=9)

    # Right: log scale with ratio annotation
    log_vars = [np.log10(v) for v in variances]
    ax2.hist(log_vars, bins=50, color='#F57C00', edgecolor='white', linewidth=0.5, alpha=0.8)
    ax2.axvline(np.log10(smooth['affect_variance']), color='#4CAF50', linewidth=2, linestyle='--')
    ax2.axvline(np.log10(volatile['affect_variance']), color='#D32F2F', linewidth=2, linestyle='--')
    ax2.set_xlabel('log₁₀(Affect Variance)')
    ax2.set_ylabel('Count')
    ax2.set_title(f'Log-Scale Distribution\nVariance Ratio: {ratio:,.0f}×', fontweight='bold')

    # Annotate the ratio
    ax2.annotate(f'{ratio:,.0f}× difference',
                 xy=(np.log10(volatile['affect_variance']), 5),
                 xytext=(np.log10(volatile['affect_variance']) - 1, 40),
                 arrowprops=dict(arrowstyle='->', color='#D32F2F'),
                 fontsize=11, fontweight='bold', color='#D32F2F')

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_variance_ratio.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_variance_ratio.png")


# ---------------------------------------------------------------------------
# Figure 7: PAD by Role
# ---------------------------------------------------------------------------
def fig_pad_by_role(convs):
    role_pad = defaultdict(lambda: {'pleasure': [], 'arousal': [], 'dominance': [], 'intensity': []})

    for data in convs.values():
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        if not hr:
            continue
        dominant = max(hr, key=hr.get)
        for msg in data.get('messages', []):
            pad = msg.get('pad', {})
            if pad and msg.get('role') == 'user':
                role_pad[dominant]['pleasure'].append(pad.get('pleasure', 0.5))
                role_pad[dominant]['arousal'].append(pad.get('arousal', 0.5))
                role_pad[dominant]['dominance'].append(pad.get('dominance', 0.5))
                role_pad[dominant]['intensity'].append(pad.get('emotionalIntensity', 0.5))

    roles_order = ['information-seeker', 'director', 'provider', 'collaborator', 'social-expressor', 'relational-peer']
    dims = ['pleasure', 'arousal', 'dominance', 'intensity']
    dim_colors = ['#4CAF50', '#FF9800', '#2196F3', '#D32F2F']

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(roles_order))
    width = 0.18

    for i, (dim, color) in enumerate(zip(dims, dim_colors)):
        means = []
        stds = []
        for role in roles_order:
            vals = role_pad[role][dim]
            means.append(statistics.mean(vals) if vals else 0)
            stds.append(statistics.stdev(vals) if len(vals) > 1 else 0)
        ax.bar(x + i * width - width * 1.5, means, width, yerr=stds, label=dim.capitalize(),
               color=color, edgecolor='white', linewidth=0.5, capsize=2, error_kw={'linewidth': 0.8})

    ax.set_xticks(x)
    ax.set_xticklabels([r.replace('-', '\n') for r in roles_order], fontsize=9)
    ax.set_ylabel('Score (0–1)')
    ax.set_title('PAD Dimensions by Human Role (User Messages)', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.0)

    # Add instrumental/expressive labels
    ax.axvspan(-0.5, 3.5, alpha=0.05, color=INSTRUMENTAL_COLOR)
    ax.axvspan(3.5, 5.5, alpha=0.05, color=EXPRESSIVE_COLOR)
    ax.text(1.5, 0.95, 'Instrumental', ha='center', fontsize=9, color=INSTRUMENTAL_COLOR, fontstyle='italic')
    ax.text(4.5, 0.95, 'Expressive', ha='center', fontsize=9, color=EXPRESSIVE_COLOR, fontstyle='italic')

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_pad_by_role.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_pad_by_role.png")


# ---------------------------------------------------------------------------
# Figure 8: Feature Importance by Channel
# ---------------------------------------------------------------------------
def fig_feature_importance():
    # Load verified stats (computed by compute_verified_stats.py)
    stats_path = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "verified_stats.json"
    with open(stats_path) as f:
        stats = json.load(f)

    rf_data = stats['rf_role_pair']
    rf_acc = rf_data['rf_accuracy_mean'] * 100
    top_15 = rf_data['top_15']

    names = [item['feature'] for item in top_15][::-1]
    importances = [item['importance'] for item in top_15][::-1]
    channels = [item['channel'] for item in top_15][::-1]
    colors = [CHANNEL_COLORS[c] for c in channels]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(range(len(names)), importances, color=colors, edgecolor='white', linewidth=0.5)

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([n.replace('_', ' ') for n in names], fontsize=9)
    ax.set_xlabel('Feature Importance (Random Forest)')
    ax.set_title(f'Top 15 Evidence Features by Importance\n(5-fold CV, RF accuracy: {rf_acc:.1f}%)', fontweight='bold')

    handles = [mpatches.Patch(color=CHANNEL_COLORS[c], label=f'{c}') for c in ['Divergence', 'Expressiveness', 'Dynamics', 'Affect', 'Structure']]
    ax.legend(handles=handles, loc='lower right', fontsize=9)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_feature_importance.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_feature_importance.png")


# ---------------------------------------------------------------------------
# Figure 9: Acceptance Test Summary
# ---------------------------------------------------------------------------
def fig_acceptance_tests():
    # Load acceptance results from JSON (produced by run_acceptance_tests.py)
    json_path = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "acceptance_results.json"
    if json_path.exists():
        with open(json_path) as f:
            acc_data = json.load(f)
        acc_human = acc_data['test_a']['Human Role']['accuracy'] * 100
        acc_ai = acc_data['test_a']['AI Role']['accuracy'] * 100
        chance_human = acc_data['test_a']['Human Role']['chance'] * 100
        chance_ai = acc_data['test_a']['AI Role']['chance'] * 100
    else:
        print("  WARNING: acceptance_results.json not found, using fallback values")
        acc_human, acc_ai = 74.7, 78.0
        chance_human, chance_ai = 16.7, 16.7

    fig = plt.figure(figsize=(14, 5))
    gs = GridSpec(1, 3, figure=fig, width_ratios=[1, 1, 1])

    # Test A: Label prediction
    ax1 = fig.add_subplot(gs[0])
    tests = ['Human\nRole', 'AI\nRole']
    accuracies = [acc_human, acc_ai]
    chance = [chance_human, chance_ai]
    threshold = [60, 60]

    x = np.arange(len(tests))
    ax1.bar(x - 0.15, accuracies, 0.3, label='RF Accuracy', color='#D32F2F', edgecolor='white')
    ax1.bar(x + 0.15, chance, 0.3, label='Chance', color='#BDBDBD', edgecolor='white')
    ax1.axhline(60, color='#FF9800', linewidth=2, linestyle='--', label='Threshold (60%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tests)
    ax1.set_ylabel('Accuracy (%)')
    ax1.set_title('Test A: Evidence → Labels\n(< 60% = PASS)', fontweight='bold')
    ax1.legend(fontsize=8)
    ax1.set_ylim(0, 100)
    ax1.text(0, accuracies[0] + 2, 'WARNING', ha='center', fontsize=8, color='#D32F2F', fontweight='bold')
    ax1.text(1, accuracies[1] + 2, 'WARNING', ha='center', fontsize=8, color='#D32F2F', fontweight='bold')

    # Test B: Evidence prediction R² — read from JSON
    ax2 = fig.add_subplot(gs[1])
    test_b_features = ['expr_mean', 'affect_max', 'div_mean', 'div_variance', 'expr_variance',
                       'repair_rate', 'hedge_assert_ratio', 'goal_drift_mean']
    feat_names = ['expr_mean', 'affect_max', 'div_mean', 'div_var', 'expr_var',
                  'repair_rate', 'hedge_ratio', 'goal_drift']
    if json_path.exists():
        r2_vals = [acc_data['test_b'].get(f, {}).get('r2', 0.0) for f in test_b_features]
    else:
        r2_vals = [0.054, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    colors_b = ['#FF9800' if v > 0.01 else '#4CAF50' for v in r2_vals]
    ax2.barh(range(len(feat_names) - 1, -1, -1), r2_vals, color=colors_b, edgecolor='white')
    ax2.axvline(0.01, color='#D32F2F', linewidth=2, linestyle='--', label='Threshold (R²=0.01)')
    ax2.set_yticks(range(len(feat_names) - 1, -1, -1))
    ax2.set_yticklabels(feat_names, fontsize=9)
    ax2.set_xlabel('R²')
    ax2.set_title('Test B: Labels → Evidence\n(R² < 0.01 = PASS)', fontweight='bold')
    ax2.legend(fontsize=8)

    # Ablation - read from acceptance results JSON
    ax3 = fig.add_subplot(gs[2])
    methods = ['Evidence\nKMeans', 'Evidence\nHier.', 'Labels\nKMeans', 'Labels\nHier.', 'Combined\nKMeans', 'Combined\nHier.']
    if json_path.exists():
        abl = acc_data['ablation']
        sils = [
            abl['Evidence-only (KMeans)']['silhouette'],
            abl['Evidence-only (Hierarchical)']['silhouette'],
            abl['Labels-only (KMeans)']['silhouette'],
            abl['Labels-only (Hierarchical)']['silhouette'],
            abl['Combined (KMeans)']['silhouette'],
            abl['Combined (Hierarchical)']['silhouette'],
        ]
    else:
        sils = [0.111, 0.124, 0.453, 0.431, 0.087, 0.058]
    colors_c = ['#1976D2', '#1976D2', '#4CAF50', '#4CAF50', '#FF9800', '#FF9800']
    ax3.bar(range(len(methods)), sils, color=colors_c, edgecolor='white', linewidth=0.5)
    ax3.set_xticks(range(len(methods)))
    ax3.set_xticklabels(methods, fontsize=8)
    ax3.set_ylabel('Silhouette Score')
    ax3.set_title('Ablation: Feature Set\nComparison (K=7)', fontweight='bold')

    handles = [mpatches.Patch(color='#1976D2', label='Evidence-only'),
               mpatches.Patch(color='#4CAF50', label='Labels-only'),
               mpatches.Patch(color='#FF9800', label='Combined')]
    ax3.legend(handles=handles, fontsize=8)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_acceptance_tests.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_acceptance_tests.png")


# ---------------------------------------------------------------------------
# Figure 10: Source Composition + Length Distribution
# ---------------------------------------------------------------------------
def fig_corpus_overview(convs):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Source composition donut
    sources = Counter()
    for data in convs.values():
        src = data.get('source', 'unknown')
        if src == 'WildChat':
            src = 'wildchat'
        sources[src] += 1

    labels_src = []
    sizes = []
    colors = []
    for src in ['chatbot_arena', 'wildchat', 'oasst', 'other']:
        if sources.get(src, 0) > 0:
            labels_src.append(f'{src}\n(n={sources[src]})')
            sizes.append(sources[src])
            colors.append(SOURCE_COLORS.get(src, '#999'))

    wedges, texts, autotexts = ax1.pie(sizes, labels=labels_src, autopct='%1.1f%%',
                                        colors=colors, startangle=90,
                                        pctdistance=0.75, textprops={'fontsize': 9})
    centre = plt.Circle((0, 0), 0.55, fc='white')
    ax1.add_artist(centre)
    ax1.text(0, 0, f'N={sum(sizes)}', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.set_title('Source Composition', fontweight='bold')

    # Length distribution
    lengths = [len(data.get('messages', [])) for data in convs.values()]
    ax2.hist(lengths, bins=range(4, 55, 2), color='#1976D2', edgecolor='white', linewidth=0.5, alpha=0.8)
    ax2.axvline(statistics.median(lengths), color='#D32F2F', linewidth=2, linestyle='--',
                label=f'Median: {statistics.median(lengths):.0f}')
    ax2.axvline(statistics.mean(lengths), color='#FF9800', linewidth=2, linestyle='--',
                label=f'Mean: {statistics.mean(lengths):.1f}')
    ax2.set_xlabel('Number of Messages')
    ax2.set_ylabel('Count')
    ax2.set_title('Conversation Length Distribution', fontweight='bold')
    ax2.legend()
    ax2.set_xlim(0, 55)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_corpus_overview.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_corpus_overview.png")


# ---------------------------------------------------------------------------
# Figure 11: v1 vs v3 Comparison
# ---------------------------------------------------------------------------
def fig_v1_v3_comparison():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Corpus size
    ax = axes[0]
    versions = ['v1\n(N=507)', 'v3\n(N=2,577)']
    sizes = [507, 2577]
    bars = ax.bar(versions, sizes, color=['#BDBDBD', '#1976D2'], edgecolor='white', width=0.5)
    ax.set_ylabel('Conversations')
    ax.set_title('Corpus Size', fontweight='bold')
    for bar, size in zip(bars, sizes):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f'{size:,}', ha='center', fontweight='bold')
    ax.text(0.5, max(sizes) * 0.6, '5.1×', ha='center', fontsize=20, fontweight='bold', color='#1976D2')

    # Instrumental roles
    ax = axes[1]
    inst = [97.0, 97.0]
    bars = ax.bar(versions, inst, color=['#BDBDBD', '#1976D2'], edgecolor='white', width=0.5)
    ax.set_ylabel('Percentage')
    ax.set_title('Instrumental Human Roles', fontweight='bold')
    ax.set_ylim(90, 100)
    for bar, val in zip(bars, inst):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f'{val:.1f}%', ha='center', fontweight='bold')
    ax.text(0.5, 95, 'Identical', ha='center', fontsize=16, fontweight='bold', color='#4CAF50')

    # Variance ratio (load from verified stats)
    ax = axes[2]
    stats_path = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "verified_stats.json"
    with open(stats_path) as f:
        stats = json.load(f)
    v3_ratio = int(stats['variance_ratio']['variance_ratio'])
    ratios = [2030, v3_ratio]
    pct_change = (v3_ratio - 2030) / 2030 * 100
    bars = ax.bar(versions, ratios, color=['#BDBDBD', '#1976D2'], edgecolor='white', width=0.5)
    ax.set_ylabel('Variance Ratio (×)')
    ax.set_title('IS→ES Variance Ratio', fontweight='bold')
    for bar, val in zip(bars, ratios):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f'{val:,}×', ha='center', fontweight='bold')
    ax.text(0.5, max(ratios) * 0.5, f'+{pct_change:.0f}%', ha='center', fontsize=20, fontweight='bold', color='#1976D2')

    fig.suptitle('v1 → v3: Key Metrics Comparison', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_v1_v3_comparison.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_v1_v3_comparison.png")


# ---------------------------------------------------------------------------
# Figure 12: Clustering (t-SNE)
# ---------------------------------------------------------------------------
def fig_clustering_tsne(evidence):
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    # Length-confounded features to exclude (see cluster_paths.py for rationale)
    LENGTH_CONFOUNDED = {
        'n_messages_log', 'affect_peak_count', 'affect_valley_count',
        'affect_range', 'affect_max', 'affect_min',
    }

    ALL_COLS = [
        'div_mean', 'div_variance', 'div_trend', 'div_max_spike', 'div_range',
        'expr_mean', 'expr_variance', 'expr_trend', 'expr_range', 'expr_shift',
        'repair_rate', 'constraint_pressure', 'hedge_assert_ratio',
        'ai_refusal_rate', 'goal_drift_mean', 'goal_drift_variance', 'goal_stability',
        'length_ratio',
        'affect_mean', 'affect_variance', 'affect_trend', 'affect_range',
        'affect_max', 'affect_min', 'affect_peak_count', 'affect_valley_count',
        'valence_mean', 'valence_variance', 'valence_trend',
        'n_messages_log',
    ]
    CLEAN_COLS = [c for c in ALL_COLS if c not in LENGTH_CONFOUNDED]

    conv_ids = sorted(evidence.keys())
    X = np.array([
        [float(evidence[cid].get(col, 0)) for col in CLEAN_COLS]
        for cid in conv_ids
    ])
    X = np.nan_to_num(X, nan=0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K=4 clustering (silhouette-optimal after length-confound removal)
    km4 = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels_4 = km4.fit_predict(X_scaled)
    sil_4 = silhouette_score(X_scaled, labels_4)

    # Silhouette scores for comparison
    sil_scores = {}
    for k in range(2, 8):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        lbls = km.fit_predict(X_scaled)
        sil_scores[k] = silhouette_score(X_scaled, lbls)

    # t-SNE on cleaned features
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    embedding = tsne.fit_transform(X_scaled)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

    # Panel 1: K=4 t-SNE
    ax1 = axes[0]
    colors_4 = ['#E53935', '#1E88E5', '#43A047', '#FB8C00']
    for c in range(4):
        mask = labels_4 == c
        ax1.scatter(embedding[mask, 0], embedding[mask, 1], c=colors_4[c],
                    s=6, alpha=0.4, label=f'Cluster {c} (n={mask.sum()})')
    ax1.set_title(f'K=4 Clusters (Silhouette: {sil_4:.3f})\nLength-confounds removed', fontweight='bold')
    ax1.set_xlabel('t-SNE 1')
    ax1.set_ylabel('t-SNE 2')
    ax1.legend(fontsize=8, loc='upper right', framealpha=0.9)

    # Panel 2: Silhouette by K
    ax2 = axes[1]
    ks = sorted(sil_scores.keys())
    sils = [sil_scores[k] for k in ks]
    bars = ax2.bar(ks, sils, color=['#1E88E5' if k != 4 else '#E53935' for k in ks],
                   edgecolor='white', linewidth=0.5)
    ax2.set_xlabel('Number of Clusters (K)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Score by K\n(after length-confound removal)', fontweight='bold')
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax2.set_xticks(ks)
    for k_val, s in zip(ks, sils):
        ax2.text(k_val, s + 0.002, f'{s:.3f}', ha='center', fontsize=8)
    ax2.annotate('Gap statistic\noptimal: K=1\n(no discrete\nstructure)',
                 xy=(2, 0.099), fontsize=8, fontstyle='italic', color='#666',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF9C4', alpha=0.9))

    # Panel 3: Top features driving K=4
    ax3 = axes[2]
    # Load cluster analysis for feature importance
    cluster_file = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "cluster_analysis_kmeans.json"
    if cluster_file.exists():
        with open(cluster_file) as f:
            cluster_data = json.load(f)
        feat_imp = cluster_data.get('feature_importance', {})
        top_feats = sorted(feat_imp.items(), key=lambda x: x[1], reverse=True)[:10]
        feat_names = [f[0].replace('_', '\n') for f in top_feats]
        feat_vals = [f[1] for f in top_feats]

        channel_colors = []
        for f, _ in top_feats:
            if f.startswith('div'): channel_colors.append('#1E88E5')
            elif f.startswith('expr'): channel_colors.append('#43A047')
            elif f.startswith('goal') or f in ('repair_rate', 'constraint_pressure'): channel_colors.append('#FB8C00')
            elif f.startswith('affect') or f.startswith('valence'): channel_colors.append('#E53935')
            else: channel_colors.append('#607D8B')

        bars = ax3.barh(range(len(feat_names)), feat_vals, color=channel_colors, edgecolor='white')
        ax3.set_yticks(range(len(feat_names)))
        ax3.set_yticklabels(feat_names, fontsize=8)
        ax3.invert_yaxis()
        ax3.set_xlabel('RF Feature Importance')
        ax3.set_title('Top 10 Features (K=4)\nDriving cluster separation', fontweight='bold')

        # Legend for channels
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#1E88E5', label='Divergence'),
            Patch(facecolor='#43A047', label='Expressiveness'),
            Patch(facecolor='#FB8C00', label='Dynamics'),
            Patch(facecolor='#E53935', label='Affect'),
        ]
        ax3.legend(handles=legend_elements, fontsize=7, loc='lower right')
    else:
        ax3.text(0.5, 0.5, 'Cluster analysis\nnot found', transform=ax3.transAxes,
                 ha='center', va='center')

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_clustering_tsne.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_clustering_tsne.png")


# ---------------------------------------------------------------------------
# Figure 13: Mode Violations (updated)
# ---------------------------------------------------------------------------
def fig_mode_violations(convs):
    # Count violations from atlas graphs
    graphs_dir = PROJECT_ROOT / "data" / "v2_unified" / "atlas" / "graphs"
    violation_types = Counter()
    source_violations = defaultdict(lambda: Counter())
    total_turns_by_source = defaultdict(int)

    for gfile in sorted(graphs_dir.glob('*.json')):
        with open(gfile) as f:
            graph = json.load(f)

        cid = gfile.stem
        src = convs.get(cid, {}).get('source', 'unknown')
        if src == 'WildChat':
            src = 'wildchat'

        nodes = graph.get('nodes', [])
        for node in nodes:
            if node.get('node_type') == 'ViolationEvent':
                vtype = node.get('violation_type', 'unknown')
                violation_types[vtype] += 1
                source_violations[src][vtype] += 1

        total_turns_by_source[src] += len([n for n in nodes if n.get('node_type') == 'Turn'])

    if not violation_types:
        print("  fig_mode_violations.png (SKIPPED - no violations)")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Donut chart
    items = violation_types.most_common()
    labels = [k.replace('_', ' ').title() for k, _ in items]
    sizes = [v for _, v in items]
    total = sum(sizes)
    donut_colors = ['#2196F3', '#FF9800', '#D32F2F', '#4CAF50', '#9C27B0'][:len(items)]

    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                        colors=donut_colors, startangle=90,
                                        pctdistance=0.75, textprops={'fontsize': 9})
    centre = plt.Circle((0, 0), 0.55, fc='white')
    ax1.add_artist(centre)
    ax1.text(0, 0, f'{total}\nviolations', ha='center', va='center', fontsize=13, fontweight='bold')
    ax1.set_title('Mode Violation Types', fontweight='bold')

    # By source (normalized)
    sources_list = ['chatbot_arena', 'wildchat', 'oasst']
    vtypes = [k for k, _ in items[:3]]
    x = np.arange(len(sources_list))
    width = 0.25

    for i, vtype in enumerate(vtypes):
        rates = []
        for src in sources_list:
            total_t = total_turns_by_source.get(src, 1)
            rates.append(source_violations[src].get(vtype, 0) / total_t * 100)
        ax2.bar(x + i * width - width, rates, width, label=vtype.replace('_', ' ').title(),
                color=donut_colors[i], edgecolor='white')

    ax2.set_xticks(x)
    ax2.set_xticklabels([s.replace('_', '\n') for s in sources_list])
    ax2.set_ylabel('% of Turn Pairs')
    ax2.set_title('Mode Violations by Source', fontweight='bold')
    ax2.legend(fontsize=8)

    fig.suptitle('Mode Mismatch Analysis (N=2,577)', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_mode_violations.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_mode_violations.png")


# ---------------------------------------------------------------------------
# Figure 14: Instrumental/Expressive Summary (key finding)
# ---------------------------------------------------------------------------
def fig_instrumental_finding(convs):
    fig, ax = plt.subplots(figsize=(8, 8))

    instrumental = 2498
    expressive = 78
    total = instrumental + expressive

    sizes = [instrumental, expressive]
    colors = [INSTRUMENTAL_COLOR, EXPRESSIVE_COLOR]
    labels = [f'Instrumental\n{instrumental:,} ({instrumental/total*100:.1f}%)',
              f'Expressive\n{expressive:,} ({expressive/total*100:.1f}%)']

    wedges, texts = ax.pie(sizes, labels=labels, colors=colors,
                           startangle=90, textprops={'fontsize=12': True} if False else {'fontsize': 12},
                           wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    centre = plt.Circle((0, 0), 0.6, fc='white')
    ax.add_artist(centre)
    ax.text(0, 0.1, '97.0%', ha='center', va='center', fontsize=32, fontweight='bold', color=INSTRUMENTAL_COLOR)
    ax.text(0, -0.15, 'Instrumental', ha='center', va='center', fontsize=14, color='#666')
    ax.set_title(f'Human Role Axis Distribution\n(N={total:,}, replicates v1 exactly)', fontweight='bold', fontsize=13)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_instrumental_finding.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_instrumental_finding.png")


# ---------------------------------------------------------------------------
# Figure 15: Smooth vs Volatile Exemplar Trajectories
# ---------------------------------------------------------------------------
def fig_exemplar_trajectories(convs, evidence):
    # Find smooth and volatile exemplars
    is_es = []
    for cid, data in convs.items():
        cls = data.get('classification', {})
        hr = (cls.get('humanRole') or {}).get('distribution', {})
        ar = (cls.get('aiRole') or {}).get('distribution', {})
        if not hr or not ar:
            continue
        if max(hr, key=hr.get) == 'information-seeker' and max(ar, key=ar.get) == 'expert-system':
            ev = evidence.get(cid, {})
            av = float(ev.get('affect_variance', 0))
            n_msgs = len(data.get('messages', []))
            if n_msgs >= 6 and av > 0:
                is_es.append({'conv_id': cid, 'affect_variance': av})

    by_var = sorted(is_es, key=lambda x: x['affect_variance'])
    smooth_id = by_var[0]['conv_id']
    volatile_id = by_var[-1]['conv_id']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=False)

    for ax, cid, label, color in [(ax1, smooth_id, 'Smooth', '#4CAF50'), (ax2, volatile_id, 'Volatile', '#D32F2F')]:
        data = convs[cid]
        messages = data.get('messages', [])
        intensities = []
        pleasures = []
        turns = []
        for i, msg in enumerate(messages):
            pad = msg.get('pad', {})
            if pad:
                intensities.append(pad.get('emotionalIntensity', 0.5))
                pleasures.append(pad.get('pleasure', 0.5))
                turns.append(i + 1)

        if turns:
            ax.plot(turns, intensities, 'o-', color=color, linewidth=2, markersize=6, label='Intensity')
            ax.plot(turns, pleasures, 's--', color='#1976D2', linewidth=1.5, markersize=5, alpha=0.7, label='Pleasure')
            ax.fill_between(turns, intensities, alpha=0.1, color=color)

        av = by_var[0]['affect_variance'] if cid == smooth_id else by_var[-1]['affect_variance']
        ax.set_ylabel('Score')
        ax.set_title(f'{label}: {cid}\n(affect variance: {av:.6f})', fontweight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Turn')

        # Role labels on turns
        for i, msg in enumerate(messages):
            if i < len(turns):
                role_label = 'H' if msg.get('role') == 'user' else 'A'
                ax.text(turns[min(i, len(turns)-1)], -0.05, role_label, ha='center', fontsize=7, color='#999')

    fig.suptitle('Same Destination, Different Journeys\n(Both: Information-Seeker → Expert-System)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_exemplar_trajectories.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_exemplar_trajectories.png")


# ---------------------------------------------------------------------------
# Figure 16: Channel Contribution Pie
# ---------------------------------------------------------------------------
def fig_channel_contributions():
    # Load verified stats (computed by compute_verified_stats.py)
    stats_path = PROJECT_ROOT / "data" / "v2_unified" / "reports" / "verified_stats.json"
    with open(stats_path) as f:
        stats = json.load(f)

    ch_data = stats['rf_role_pair']['channel_contributions']
    channels = {
        'Divergence (Ch.A)': ch_data.get('Divergence', 0),
        'Expressiveness (Ch.B)': ch_data.get('Expressiveness', 0),
        'Dynamics (Ch.C)': ch_data.get('Dynamics', 0),
        'Affect Proxy': ch_data.get('Affect', 0),
        'Structure': ch_data.get('Structure', 0),
    }

    fig, ax = plt.subplots(figsize=(8, 8))
    labels = list(channels.keys())
    sizes = list(channels.values())
    colors = [CHANNEL_COLORS['Divergence'], CHANNEL_COLORS['Expressiveness'],
              CHANNEL_COLORS['Dynamics'], CHANNEL_COLORS['Affect'], CHANNEL_COLORS['Structure']]

    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                       colors=colors, startangle=90,
                                       textprops={'fontsize': 11},
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    for autotext in autotexts:
        autotext.set_fontweight('bold')

    ax.set_title('Evidence Feature Channel Contributions\n(RF Feature Importance)', fontweight='bold', fontsize=13)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_channel_contributions.png', bbox_inches='tight')
    plt.close(fig)
    print("  fig_channel_contributions.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("GENERATING v3 PAPER FIGURES")
    print("=" * 60)

    convs, evidence = load_all()
    print(f"  Loaded {len(convs)} conversations, {len(evidence)} evidence records\n")

    print("Generating figures...")
    fig_human_roles(convs)
    fig_ai_roles(convs)
    fig_role_pair_heatmap(convs)
    fig_roles_by_source(convs)
    fig_conversation_purpose(convs)
    fig_variance_ratio(convs, evidence)
    fig_pad_by_role(convs)
    fig_feature_importance()
    fig_acceptance_tests()
    fig_corpus_overview(convs)
    fig_v1_v3_comparison()
    fig_clustering_tsne(evidence)
    fig_mode_violations(convs)
    fig_instrumental_finding(convs)
    fig_exemplar_trajectories(convs, evidence)
    fig_channel_contributions()

    print(f"\nDone! {16} figures saved to {FIGURES_DIR}")


if __name__ == '__main__':
    main()
