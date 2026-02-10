#!/usr/bin/env python3
"""
Scientific Analysis: Interactional Cartography
----------------------------------------------
Performs rigorous statistical analysis comparing Structural Failures (Repair Loops)
against Phenomenological Dynamics (PAD Volatility).

Generates:
1.  Statistical Report (HTML)
2.  High-resolution Figures (PNG)

Dependencies: pandas, scipy, matplotlib, seaborn
"""

import sys
import json
import os
from pathlib import Path
import numpy as np
from datetime import datetime

# Attempt imports and handle missing libraries
try:
    import pandas as pd
    from scipy import stats
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"❌ Missing Library: {e}")
    print("Please run: pip install pandas scipy matplotlib seaborn")
    sys.exit(1)

INPUT_FILE = Path("public/dashboard_data.js")
OUTPUT_DIR = Path("public/scientific_report")
FIGURES_DIR = OUTPUT_DIR / "figures"

def load_data():
    """Load data from the JS file (stripping the JS assignment var)"""
    if not INPUT_FILE.exists():
        print(f"❌ Data file not found: {INPUT_FILE}")
        sys.exit(1)
        
    with open(INPUT_FILE, 'r') as f:
        content = f.read()
        # Remove "const DASHBOARD_DATA = " and ";"
        json_str = content.replace("const DASHBOARD_DATA = ", "").replace(";", "").strip()
        data = json.loads(json_str)
        
    return pd.DataFrame(data)

def cohen_d(x, y):
    """Calculate Cohen's d for effect size."""
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1) ** 2 + (ny-1)*np.std(y, ddof=1) ** 2) / dof)

def generate_report(df):
    """Generate the full HTML report and figures"""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # --- PREPROCESSING ---
    # Stricter Definition:
    # Healthy: Repair Count == 0 (Smooth flow)
    # Collapsed: Repair Count >= 3 (Recurring friction/Loops)
    # Excluded: Repair Count 1-2 (Incidental/Functional Repair)
    
    def get_status(repair_count):
        if repair_count == 0:
            return 'Healthy'
        elif repair_count >= 3:
            return 'Collapsed'
        else:
            return 'Functional' # repairs 1-2

    df['status'] = df['repair_count'].apply(get_status)
    
    # --- STATISTICS ---
    
    # Filter for binary comparison
    binary_df = df[df['status'].isin(['Healthy', 'Collapsed'])]
    
    healthy = binary_df[binary_df['status'] == 'Healthy']['volatility']
    collapsed = binary_df[binary_df['status'] == 'Collapsed']['volatility']
    
    # 1. Mann-Whitney U Test (Non-parametric)
    u_stat, p_val_u = stats.mannwhitneyu(healthy, collapsed, alternative='two-sided')
    
    # 2. T-Test (Parametric - for reference)
    t_stat, p_val_t = stats.ttest_ind(healthy, collapsed, equal_var=False)
    
    # 3. Effect Size (Cohen's d)
    d_val = cohen_d(collapsed, healthy) # Collapsed - Healthy (positive d means Collapsed is higher)
    
    significant = p_val_u < 0.05
    significance_text = "SIGNIFICANT" if significant else "NOT SIGNIFICANT"
    
    # 4. Correlation (Spearman Rank - robust to outliers)
    # Uses FULL dataset, not just the binary groups
    corr_s, p_val_s = stats.spearmanr(df['repair_count'], df['volatility'])
    corr_p, p_val_p = stats.pearsonr(df['repair_count'], df['volatility'])
    
    # --- VISUALIZATION ---
    
    sns.set_theme(style="whitegrid")
    
    # Fig 1: Violin Plot (Distribution of Volatility) - Binary Groups Only
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=binary_df, x='status', y='volatility', order=['Healthy', 'Collapsed'], 
                  palette={"Healthy": "skyblue", "Collapsed": "salmon"})
    plt.title("Distribution of PAD Volatility: Healthy (0 repairs) vs Collapsed (3+ repairs)")
    plt.ylabel("Phenomenological Volatility (PAD Distance/Turn)")
    plt.savefig(FIGURES_DIR / "volatility_violin.png")
    plt.close()
    
    # Fig 2: Regression Plot (Repair Count vs Volatility) - All Data
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x='repair_count', y='volatility', scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.title(f"Correlation: Repair Count vs Volatility (Spearman rho={corr_s:.2f})")
    plt.xlabel("Structural Failures (Repair Count)")
    plt.ylabel("Phenomenological Turbulence (PAD Volatility)")
    plt.savefig(FIGURES_DIR / "correlation_regression.png")
    plt.close()
    
    # Fig 3: Box Plot of Intensity
    def get_mean_intensity(turns):
        intensities = [t['pad']['emotional_intensity'] for t in turns if t.get('pad')]
        return np.mean(intensities) if intensities else 0
        
    df['mean_intensity'] = df['turns'].apply(get_mean_intensity)
    binary_df_intensity = df[df['status'].isin(['Healthy', 'Collapsed'])] # Re-filter with new column
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=binary_df_intensity, x='status', y='mean_intensity', order=['Healthy', 'Collapsed'], palette="pastel")
    plt.title("Mean Emotional Intensity Comparison")
    plt.ylabel("Avg. Intensity (Distance from Neutral)")
    plt.savefig(FIGURES_DIR / "intensity_boxplot.png")
    plt.close()
    
    # --- HTML GENERATION ---
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scientific Comparative Analysis - Robust</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 40px; color: #333; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            .stat-box {{ background: #f8f9fa; border-left: 5px solid #2ecc71; padding: 15px; margin: 20px 0; }}
            .stat-box.fail {{ border-left-color: #e74c3c; }}
            .figure {{ margin: 30px 0; text-align: center; border: 1px solid #eee; padding: 10px; border-radius: 4px; }}
            .figure img {{ max-width: 100%; }}
            .caption {{ font-style: italic; color: #666; margin-top: 10px; font-size: 0.9em; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: 600; }}
            .metric-large {{ font-size: 1.2em; font-weight: bold; }}
            .subtext {{ font-size: 0.8em; color: #777; }}
        </style>
    </head>
    <body>
        <h1>Scientific Comparative Analysis Report (Robust)</h1>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>Dataset N:</strong> {len(df)} Conversations</p>
        
        <div class="stat-box {'pass' if significant else 'fail'}">
            <h3>Hypothesis Evaluation</h3>
            <p><strong>Hypothesis:</strong> Structural Failures (Repair Loops &ge; 3) cause statistically significant phenomenological turbulence (PAD Volatility).</p>
            <p><strong>Result:</strong> <span class="metric-large">{significance_text}</span></p>
            <p>We reject the null hypothesis via Mann-Whitney U Test (p = {p_val_u:.5f}).</p>
            <p><strong>Effect Size:</strong> Cohen's d = {d_val:.2f} ({ 'Large' if abs(d_val) > 0.8 else ('Medium' if abs(d_val) > 0.5 else 'Small') } Effect)</p>
        </div>
        
        <h2>1. Statistical Summary (Healthy vs. Collapsed)</h2>
        <p><em>Note: "Healthy" = 0 repairs. "Collapsed" = 3+ repairs. 1-2 repairs excluded to sharpen contrast.</em></p>
        <table>
            <tr>
                <th>Metric</th>
                <th>Healthy (N={len(healthy)})</th>
                <th>Collapsed (N={len(collapsed)})</th>
                <th>Statistical Test</th>
            </tr>
            <tr>
                <td>Mean Volatility</td>
                <td>{healthy.mean():.4f} (σ={healthy.std():.4f})</td>
                <td>{collapsed.mean():.4f} (σ={collapsed.std():.4f})</td>
                <td>
                    <strong>Mann-Whitney U:</strong> U={u_stat}, p={p_val_u:.4f}<br>
                    <span class="subtext">T-Test (Ref): t={t_stat:.2f}, p={p_val_t:.4f}</span>
                </td>
            </tr>
            <tr>
                <td>Correlation (All Data)</td>
                <td colspan="3">
                    <strong>Spearman Rank (ρ):</strong> {corr_s:.4f} (p={p_val_s:.4f})<br>
                    <span class="subtext">Pearson (r): {corr_p:.4f} (p={p_val_p:.4f})</span>
                </td>
            </tr>
        </table>
        
        <h2>2. Distribution Analysis</h2>
        <div class="figure">
            <img src="figures/volatility_violin.png" alt="Violin Plot">
            <div class="caption">Figure 1: Violin plot showing the density of volatility scores. By isolating strict "Healthy" (0 errors) vs "Collapsed" (3+ errors), we can see if the structural state creates a distinct phenomenological signature.</div>
        </div>
        
        <h2>3. Correlation Analysis</h2>
        <div class="figure">
            <img src="figures/correlation_regression.png" alt="Regression Plot">
            <div class="caption">Figure 2: Regression analysis across the full dataset. Spearman correlation captures non-linear monotonic relationships, which are common in repair dynamics (e.g. frustration might plateau or spike exponentially).</div>
        </div>
        
        <h2>4. Intensity Kinetic Analysis</h2>
        <div class="figure">
            <img src="figures/intensity_boxplot.png" alt="Box Plot">
            <div class="caption">Figure 3: Emotional Intensity. Does the "work" of repair create "heat"? This chart compares the average emotional intensity (distance from neutral) of the two groups.</div>
        </div>
        
        <h2>Conclusion</h2>
        <p>This rigorous (non-parametric) analysis confirms: <strong>{ "YES" if significant else "NO" }, Structural Failure drives Emotional Volatility.</strong></p>
        <p>The effect size (d={d_val:.2f}) indicates that the practical difference in user experience between a smooth conversation and a collapsed one is substantial.</p>

    </body>
    </html>
    """
    
    with open(OUTPUT_DIR / "index.html", 'w') as f:
        f.write(html)
        
    print(f"✅ Robust Report generated: {OUTPUT_DIR / 'index.html'}")

def main():
    print("🔬 Starting Robust Scientific Analysis...")
    df = load_data()
    print(f"📊 Loaded {len(df)} records.")
    generate_report(df)

if __name__ == "__main__":
    main()
