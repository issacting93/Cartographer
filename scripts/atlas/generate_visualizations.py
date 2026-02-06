#!/usr/bin/env python3
"""
Atlas Pipeline Visualization Suite
Generates all figures for the CUI 2026 Comprehensive Findings Report.

Data source: data/atlas_canonical/metrics/aggregate.json + graphs/*.json
Output: paper/figures/
"""

import json
import glob
import collections
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

# ============= Configuration =============

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "atlas_canonical")
METRICS_DIR = os.path.join(DATA_DIR, "metrics")
GRAPHS_DIR = os.path.join(DATA_DIR, "graphs")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "paper", "figures")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Style
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
})

# Color palette
PALETTE = {
    "Task Maintained": "#2196F3",
    "Constraint Drift": "#FF9800",
    "Agency Collapse": "#F44336",
    "Task Shift": "#9C27B0",
    "No Constraints": "#9E9E9E",
}
ARCH_PALETTE = sns.color_palette("Set2", 7)
MODE_COLORS = {
    "UNSOLICITED_ADVICE": "#2196F3",
    "PREMATURE_EXECUTION": "#FF9800",
    "EXECUTION_AVOIDANCE": "#F44336",
}
HARDNESS_COLORS = {
    "Strict": "#D32F2F",
    "Mixed": "#FF9800",
    "Flexible": "#4CAF50",
}


# ============= Data Loading =============

def load_all_metrics():
    with open(os.path.join(METRICS_DIR, "all_metrics.json")) as f:
        return pd.DataFrame(json.load(f))

def load_aggregate():
    with open(os.path.join(METRICS_DIR, "aggregate.json")) as f:
        return json.load(f)

def load_graph_data():
    """Extract node-level data from all graph files."""
    constraints = []
    mode_annotations = []
    conversations = []
    violation_turns_all = []

    for filepath in sorted(glob.glob(os.path.join(GRAPHS_DIR, "*.json"))):
        with open(filepath) as f:
            g = json.load(f)

        conv_node = None
        for n in g.get("nodes", []):
            nt = n.get("node_type", "")
            if nt == "Conversation":
                conv_node = n
                conversations.append(n)
            elif nt == "Constraint":
                constraints.append(n)
                for turn, state in n.get("state_history", []):
                    if state == "VIOLATED":
                        violation_turns_all.append(turn)
            elif nt == "InteractionMode":
                if conv_node:
                    n["_source"] = conv_node.get("source", "")
                    n["_architecture"] = conv_node.get("task_architecture", "")
                mode_annotations.append(n)

    return constraints, mode_annotations, conversations, violation_turns_all


# ============= Figure 1: Constraint Survival Distribution =============

def plot_survival_distribution(df):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Only conversations with constraints
    df_c = df[df["total_constraints"] > 0].copy()
    if df_c.empty:
        df_c = df.copy()

    sns.histplot(
        data=df_c, x="constraint_survival_rate",
        bins=20, kde=True, color="#5C6BC0", alpha=0.7, ax=ax,
        edgecolor="white", linewidth=0.5,
    )
    median_val = df_c["constraint_survival_rate"].median()
    ax.axvline(median_val, color="#F44336", linestyle="--", linewidth=2, label=f"Median: {median_val:.0%}")
    ax.set_title("Distribution of Constraint Survival Rates", fontsize=15, fontweight="bold")
    ax.set_xlabel("Constraint Survival Rate", fontsize=12)
    ax.set_ylabel("Number of Conversations", fontsize=12)
    ax.legend(fontsize=11)

    fig.savefig(os.path.join(OUTPUT_DIR, "survival_rate_dist.png"))
    plt.close(fig)
    print("  [1/9] survival_rate_dist.png")


# ============= Figure 2: The Context Cliff =============

def plot_context_cliff(violation_turns):
    fig, ax = plt.subplots(figsize=(10, 5))

    counter = collections.Counter(violation_turns)
    max_turn = min(30, max(counter.keys()) + 1) if counter else 20
    turns = list(range(max_turn))
    counts = [counter.get(t, 0) for t in turns]

    ax.bar(turns, counts, color="#FF7043", edgecolor="white", linewidth=0.5, alpha=0.85)

    # Overlay cumulative line
    cumulative = np.cumsum(counts) / max(1, sum(counts)) * 100
    ax2 = ax.twinx()
    ax2.plot(turns, cumulative, color="#1565C0", linewidth=2.5, marker="o", markersize=4, label="Cumulative %")
    ax2.set_ylabel("Cumulative % of Violations", fontsize=12, color="#1565C0")
    ax2.tick_params(axis="y", labelcolor="#1565C0")

    # Mark the half-life
    half_idx = next((i for i, c in enumerate(cumulative) if c >= 50), None)
    if half_idx is not None:
        ax2.axhline(50, color="#1565C0", linestyle=":", alpha=0.5)
        ax2.annotate(f"50% at turn {half_idx}", xy=(half_idx, 50),
                     xytext=(half_idx + 3, 60), fontsize=10,
                     arrowprops=dict(arrowstyle="->", color="#1565C0"),
                     color="#1565C0", fontweight="bold")

    ax.set_title("The Context Cliff: When Constraints Break", fontsize=15, fontweight="bold")
    ax.set_xlabel("Turn Index", fontsize=12)
    ax.set_ylabel("Violation Events", fontsize=12)
    ax.set_xticks(range(0, max_turn, 2))

    fig.savefig(os.path.join(OUTPUT_DIR, "context_cliff.png"))
    plt.close(fig)
    print("  [2/9] context_cliff.png")


# ============= Figure 3: Agency Tax by Class =============

def plot_agency_tax_by_class(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    main_classes = ["Constraint Drift", "Task Maintained", "Agency Collapse"]
    df_f = df[df["stability_class"].isin(main_classes)].copy()
    order = main_classes
    colors = [PALETTE[c] for c in order]

    # Drift velocity
    sns.barplot(data=df_f, x="stability_class", y="drift_velocity",
                order=order, palette=colors, capsize=0.1, ax=axes[0],
                edgecolor="white", linewidth=0.5)
    axes[0].set_title("Drift Velocity by Stability Class", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Violations / Turn", fontsize=11)

    # Agency tax
    sns.barplot(data=df_f, x="stability_class", y="agency_tax",
                order=order, palette=colors, capsize=0.1, ax=axes[1],
                edgecolor="white", linewidth=0.5)
    axes[1].set_title("Agency Tax by Stability Class", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Repairs / Violation", fontsize=11)

    fig.suptitle("Constraint Degradation Metrics", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "agency_tax_by_class.png"))
    plt.close(fig)
    print("  [3/9] agency_tax_by_class.png")


# ============= Figure 4: Agency Tax vs Drift Scatter =============

def plot_agency_tax_vs_drift(df):
    fig, ax = plt.subplots(figsize=(10, 7))

    main_classes = ["Task Maintained", "Constraint Drift", "Agency Collapse"]
    df_f = df[df["stability_class"].isin(main_classes)].copy()

    for cls in main_classes:
        subset = df_f[df_f["stability_class"] == cls]
        ax.scatter(
            subset["drift_velocity"], subset["agency_tax"],
            c=PALETTE[cls], label=cls, alpha=0.6, s=50, edgecolors="white", linewidth=0.3,
        )

    ax.set_title("Agency Tax vs. Drift Velocity", fontsize=15, fontweight="bold")
    ax.set_xlabel("Drift Velocity (Violations per Turn)", fontsize=12)
    ax.set_ylabel("Agency Tax (Repair Effort per Violation)", fontsize=12)
    ax.legend(title="Stability Class", fontsize=10, title_fontsize=11)

    fig.savefig(os.path.join(OUTPUT_DIR, "agency_tax_vs_drift.png"))
    plt.close(fig)
    print("  [4/9] agency_tax_vs_drift.png")


# ============= Figure 5: Agency Tax Map (Architecture) =============

def plot_agency_tax_map(agg):
    fig, ax = plt.subplots(figsize=(10, 6))

    arch_data = agg["by_architecture"]
    archs = [a for a in ["Planning", "Generation", "Transformation", "Analysis", "Information Seeking"]
             if a in arch_data]

    x = [arch_data[a]["mean_drift_velocity"] for a in archs]
    y = [arch_data[a]["mean_agency_tax"] for a in archs]
    sizes = [arch_data[a]["n"] * 2 for a in archs]

    scatter = ax.scatter(x, y, s=sizes, c=ARCH_PALETTE[:len(archs)],
                         alpha=0.8, edgecolors="white", linewidth=1.5)

    for i, arch in enumerate(archs):
        ax.annotate(f"{arch}\n(N={arch_data[arch]['n']})",
                    (x[i], y[i]), textcoords="offset points",
                    xytext=(10, 5), fontsize=9, fontweight="bold")

    ax.set_title("The Agency Tax Map: Task Architecture", fontsize=15, fontweight="bold")
    ax.set_xlabel("Drift Velocity (Violations per Turn)", fontsize=12)
    ax.set_ylabel("Agency Tax (Repair Effort)", fontsize=12)

    fig.savefig(os.path.join(OUTPUT_DIR, "agency_tax_map.png"))
    plt.close(fig)
    print("  [5/9] agency_tax_map.png")


# ============= Figure 6: Drift Risk Heatmap =============

def plot_drift_heatmap(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    archs = ["Planning", "Generation", "Transformation", "Analysis", "Information Seeking"]
    hardnesses = ["Strict", "Mixed", "Flexible"]

    matrix = np.zeros((len(archs), len(hardnesses)))
    for i, arch in enumerate(archs):
        for j, hard in enumerate(hardnesses):
            subset = df[(df["task_architecture"] == arch) & (df["constraint_hardness"] == hard)]
            if len(subset) > 0:
                matrix[i, j] = subset["drift_velocity"].mean()

    sns.heatmap(
        pd.DataFrame(matrix, index=archs, columns=hardnesses),
        annot=True, fmt=".3f", cmap="YlOrRd", ax=ax,
        linewidths=1, linecolor="white",
        cbar_kws={"label": "Mean Drift Velocity"},
    )

    ax.set_title("Drift Risk Matrix: Architecture x Hardness", fontsize=15, fontweight="bold")
    ax.set_ylabel("Task Architecture", fontsize=12)
    ax.set_xlabel("Constraint Hardness", fontsize=12)

    fig.savefig(os.path.join(OUTPUT_DIR, "drift_heatmap.png"))
    plt.close(fig)
    print("  [6/9] drift_heatmap.png")


# ============= Figure 7: Mode Violation Breakdown =============

def plot_mode_violations(mode_annotations):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Count violation types
    vtype_counts = collections.Counter()
    total_pairs = len(mode_annotations)
    for m in mode_annotations:
        vt = m.get("violation_type", "")
        if vt:
            vtype_counts[vt] += 1

    # Left: Donut chart of violation types
    labels = ["UNSOLICITED_ADVICE", "PREMATURE_EXECUTION", "EXECUTION_AVOIDANCE"]
    sizes = [vtype_counts.get(l, 0) for l in labels]
    colors = [MODE_COLORS[l] for l in labels]
    short_labels = ["Unsolicited\nAdvice", "Premature\nExecution", "Execution\nAvoidance"]

    wedges, texts, autotexts = axes[0].pie(
        sizes, labels=short_labels, colors=colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.75, textprops={"fontsize": 10},
    )
    centre_circle = plt.Circle((0, 0), 0.55, fc="white")
    axes[0].add_artist(centre_circle)
    total_v = sum(sizes)
    axes[0].text(0, 0, f"{total_v:,}\nviolations", ha="center", va="center",
                 fontsize=13, fontweight="bold")
    axes[0].set_title("Mode Violation Types", fontsize=13, fontweight="bold")

    # Right: Stacked bar by source
    sources = ["WildChat", "ChatbotArena", "OASST"]
    source_data = {s: collections.Counter() for s in sources}
    source_totals = collections.Counter()
    for m in mode_annotations:
        src = m.get("_source", "")
        source_totals[src] += 1
        vt = m.get("violation_type", "")
        if vt and src in source_data:
            source_data[src][vt] += 1

    x = np.arange(len(sources))
    width = 0.6
    bottom = np.zeros(len(sources))
    for vtype in labels:
        vals = [source_data[s].get(vtype, 0) / max(1, source_totals[s]) * 100 for s in sources]
        axes[1].bar(x, vals, width, bottom=bottom, label=vtype.replace("_", " ").title(),
                    color=MODE_COLORS[vtype], edgecolor="white", linewidth=0.5)
        bottom += vals

    axes[1].set_xticks(x)
    axes[1].set_xticklabels(sources, fontsize=10)
    axes[1].set_ylabel("% of Turn Pairs", fontsize=11)
    axes[1].set_title("Mode Violations by Source", fontsize=13, fontweight="bold")
    axes[1].legend(fontsize=9, loc="upper right")

    fig.suptitle("Mode Mismatch Analysis", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "mode_violations.png"))
    plt.close(fig)
    print("  [7/9] mode_violations.png")


# ============= Figure 8: Constraint Lifecycle Sankey-style =============

def plot_constraint_lifecycle(constraints):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Count final states
    states = collections.Counter(c.get("current_state", "") for c in constraints)
    total = len(constraints)

    labels = ["SURVIVED", "VIOLATED"]
    counts = [states.get(s, 0) for s in labels]
    colors = ["#4CAF50", "#F44336"]
    display = ["Survived", "Violated (Terminal)"]

    bars = ax.barh(display, counts, color=colors, edgecolor="white", linewidth=1, height=0.5)

    for bar, count in zip(bars, counts):
        pct = count / total * 100 if total > 0 else 0
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                f"{count} ({pct:.1f}%)", va="center", fontsize=12, fontweight="bold")

    # Add constraint hardness breakdown inside bars
    for i, state in enumerate(labels):
        hardness_counts = collections.Counter()
        for c in constraints:
            if c.get("current_state") == state:
                hardness_counts[c.get("hardness", "unknown")] += 1

    ax.set_xlim(0, max(counts) * 1.3)
    ax.set_title(f"Constraint Final States (N={total})", fontsize=15, fontweight="bold")
    ax.set_xlabel("Number of Constraints", fontsize=12)
    ax.invert_yaxis()

    # Add annotation
    ax.text(0.95, 0.95,
            f"Survival Rate: {states.get('SURVIVED', 0)/max(1,total)*100:.1f}%\n"
            f"Silent Failure: {states.get('VIOLATED', 0)/max(1,total)*100:.1f}%",
            transform=ax.transAxes, fontsize=11, va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF9C4", alpha=0.8))

    fig.savefig(os.path.join(OUTPUT_DIR, "constraint_lifecycle.png"))
    plt.close(fig)
    print("  [8/9] constraint_lifecycle.png")


# ============= Figure 9: Radar Signatures by Architecture =============

def plot_radar_signatures(agg):
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    metrics = ["mean_drift_velocity", "mean_agency_tax", "mean_mode_violation_rate",
               "mean_survival_rate", "mean_move_coverage"]
    metric_labels = ["Drift\nVelocity", "Agency\nTax", "Mode\nViolation", "Survival\nRate", "Move\nCoverage"]

    archs = ["Planning", "Generation", "Analysis", "Information Seeking", "Transformation"]
    arch_data = agg["by_architecture"]

    # Normalize each metric to [0, 1] range across architectures
    raw = {arch: [arch_data[arch][m] for m in metrics] for arch in archs if arch in arch_data}
    all_vals = np.array(list(raw.values()))
    mins = all_vals.min(axis=0)
    maxs = all_vals.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    for i, arch in enumerate(archs):
        if arch not in raw:
            continue
        vals = [(v - mins[j]) / ranges[j] for j, v in enumerate(raw[arch])]
        vals += vals[:1]
        ax.plot(angles, vals, linewidth=2, label=arch, color=ARCH_PALETTE[i])
        ax.fill(angles, vals, alpha=0.1, color=ARCH_PALETTE[i])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_title("Architecture Signatures (Normalized)", fontsize=14, fontweight="bold", pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)

    fig.savefig(os.path.join(OUTPUT_DIR, "fig_radar_signatures.png"))
    plt.close(fig)
    print("  [9/9] fig_radar_signatures.png")


# ============= Bonus: Drift Velocity by Class bar chart =============

def plot_drift_velocity_by_class(df):
    fig, ax = plt.subplots(figsize=(8, 5))

    main_classes = ["Constraint Drift", "Task Maintained", "Agency Collapse", "Task Shift"]
    df_f = df[df["stability_class"].isin(main_classes)]

    sns.barplot(data=df_f, x="stability_class", y="drift_velocity",
                order=main_classes, palette=[PALETTE[c] for c in main_classes],
                capsize=0.1, ax=ax, edgecolor="white", linewidth=0.5)

    ax.set_title("Drift Velocity by Stability Class", fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Violations / Turn", fontsize=12)

    fig.savefig(os.path.join(OUTPUT_DIR, "drift_velocity_by_class.png"))
    plt.close(fig)
    print("  [+] drift_velocity_by_class.png")


# ============= Bonus: Collapse Rates =============

def plot_collapse_rates(agg):
    fig, ax = plt.subplots(figsize=(10, 5))

    arch_data = agg["by_architecture"]
    archs = ["Planning", "Generation", "Transformation", "Analysis", "Information Seeking"]
    archs = [a for a in archs if a in arch_data]

    survival = [arch_data[a]["mean_survival_rate"] * 100 for a in archs]
    mode_viol = [arch_data[a]["mean_mode_violation_rate"] * 100 for a in archs]

    x = np.arange(len(archs))
    width = 0.35

    bars1 = ax.bar(x - width/2, survival, width, label="Constraint Survival %",
                   color="#4CAF50", edgecolor="white", alpha=0.85)
    bars2 = ax.bar(x + width/2, mode_viol, width, label="Mode Violation %",
                   color="#FF9800", edgecolor="white", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(archs, fontsize=10)
    ax.set_ylabel("Percentage", fontsize=12)
    ax.set_title("Constraint Survival vs Mode Violation by Architecture", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)

    # Add value labels
    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%",
                    ha="center", va="bottom", fontsize=8)
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%",
                    ha="center", va="bottom", fontsize=8)

    fig.savefig(os.path.join(OUTPUT_DIR, "fig_collapse_rates.png"))
    plt.close(fig)
    print("  [+] fig_collapse_rates.png")


# ============= Main =============

if __name__ == "__main__":
    print("Atlas Visualization Suite")
    print(f"  Data:   {DATA_DIR}")
    print(f"  Output: {OUTPUT_DIR}")
    print()

    # Load data
    print("Loading data...")
    df = load_all_metrics()
    agg = load_aggregate()
    constraints, mode_annotations, conversations, violation_turns = load_graph_data()
    print(f"  {len(df)} conversations, {len(constraints)} constraints, {len(mode_annotations)} mode annotations")
    print()

    # Generate figures
    print("Generating figures...")
    plot_survival_distribution(df)
    plot_context_cliff(violation_turns)
    plot_agency_tax_by_class(df)
    plot_agency_tax_vs_drift(df)
    plot_agency_tax_map(agg)
    plot_drift_heatmap(df)
    plot_mode_violations(mode_annotations)
    plot_constraint_lifecycle(constraints)
    plot_radar_signatures(agg)
    plot_drift_velocity_by_class(df)
    plot_collapse_rates(agg)

    print()
    print(f"All figures saved to {OUTPUT_DIR}")
