import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
from src.db_utils import fetch_query

def run_visualizations():
    """
    Fetches merged economic impact data from the database and creates visualizations:
      1. A correlation heatmap for key variables.
      2. A scatter plot with regression lines (imports/exports vs. tariff rate).
      3. Two subplots: one for tariff changes and one for trade & GDP changes.
      4. A new plot showing how the change in tariff rates (delta_tariff) impacts each dataset separately.
    """
    # --- Load Merged Data ---
    merged_df = fetch_query("SELECT * FROM economic_impact")
    merged_df.sort_values('year', inplace=True)
    
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # --- Plot 1: Correlation Heatmap ---
    corr_vars = ['avg_tariff_rate', 'imports_value', 'exports_value', 
                 'CPI', 'Unemployment_Rate', 'Industrial_Production', 'GDP']
    corr_df = merged_df[corr_vars].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix: Tariff & Macro Data")
    corr_plot_path = os.path.join(output_folder, "correlation_matrix.png")
    plt.tight_layout()
    plt.savefig(corr_plot_path)
    plt.close()
    print(f"Correlation matrix plot saved to {corr_plot_path}")
    
    # --- Plot 2: Scatter Plot with Regression Lines ---
    X = sm.add_constant(merged_df['avg_tariff_rate'])
    model_imports = sm.OLS(merged_df['imports_value'], X).fit()
    model_exports = sm.OLS(merged_df['exports_value'], X).fit()
    
    plt.figure(figsize=(8, 5))
    plt.scatter(merged_df['avg_tariff_rate'], merged_df['imports_value'], label="Imports", color="blue")
    plt.scatter(merged_df['avg_tariff_rate'], merged_df['exports_value'], label="Exports", color="green")
    sorted_idx = merged_df['avg_tariff_rate'].argsort()
    sorted_x = merged_df['avg_tariff_rate'].iloc[sorted_idx]
    X_sorted = sm.add_constant(sorted_x)
    imports_pred = model_imports.predict(X_sorted)
    exports_pred = model_exports.predict(X_sorted)
    plt.plot(sorted_x, imports_pred, color='blue', label="Imports Regression")
    plt.plot(sorted_x, exports_pred, color='green', label="Exports Regression")
    plt.xlabel("Average Tariff Rate (Trade-Weighted)")
    plt.ylabel("Trade Value")
    plt.title("Trade Value vs. Tariff Rate")
    plt.legend()
    scatter_plot_path = os.path.join(output_folder, "scatter_regression.png")
    plt.tight_layout()
    plt.savefig(scatter_plot_path)
    plt.close()
    print(f"Scatter regression plot saved to {scatter_plot_path}")
    
    # --- Plot 3: Two Subplots (Tariff Changes and Trade/GDP Changes) ---
    years_str = merged_df['year'].astype(str).values
    x = np.arange(len(years_str))
    width = 0.25
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    fig.suptitle("Year-to-Year Changes", y=0.95, fontsize=14)
    
    # Top Subplot: Tariff Δ (bps)
    ax1.bar(x, merged_df['delta_tariff'], width, color='purple', label='Tariff Δ (bps)')
    ax1.axhline(0, color='black', linewidth=0.8)
    ax1.set_ylabel("Tariff Change (bps)")
    ax1.set_title("Year-to-Year Tariff Changes")
    ax1.legend(loc='upper left')
    
    # Bottom Subplot: Imports, Exports & GDP Δ
    ax2.bar(x - width, merged_df['delta_imports'], width, color='blue', label='Imports Δ (B USD)')
    ax2.bar(x, merged_df['delta_exports'], width, color='green', label='Exports Δ (B USD)')
    ax2.bar(x + width, merged_df['delta_GDP'], width, color='orange', label='GDP Δ (B USD)')
    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_ylabel("Change (Billions USD)")
    ax2.set_title("Year-to-Year Changes in Trade & GDP")
    ax2.set_xticks(x)
    ax2.set_xticklabels(years_str, rotation=45)
    ax2.legend(loc='upper left')
    
    two_subplot_path = os.path.join(output_folder, "year_to_year_subplots.png")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(two_subplot_path)
    plt.close()
    print(f"Year-to-year subplots saved to {two_subplot_path}")
    
    # --- New Plot 4: Impact of Delta Tariff on Each Delta Metric ---
    # Define the delta metrics and their labels.
    metrics = [
        ('delta_imports', 'Imports Δ (B USD)'),
        ('delta_exports', 'Exports Δ (B USD)'),
        ('delta_GDP', 'GDP Δ (B USD)'),
        ('cpi_delta', 'CPI Δ'),
        ('unemployment_delta', 'Unemployment Δ'),
        ('industrial_delta', 'Industrial Δ')
    ]
    
    n_metrics = len(metrics)
    n_cols = 2
    n_rows = int(np.ceil(n_metrics / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
    axes = axes.flatten()
    
    for i, (metric, label) in enumerate(metrics):
        ax = axes[i]
        # Scatter plot: delta_tariff on x-axis vs. the current metric on y-axis
        ax.scatter(merged_df['delta_tariff'], merged_df[metric], color='teal', alpha=0.7)
        # Fit a linear regression for clarity
        X_d = sm.add_constant(merged_df['delta_tariff'])
        model = sm.OLS(merged_df[metric], X_d).fit()
        sorted_idx = merged_df['delta_tariff'].argsort()
        sorted_x = merged_df['delta_tariff'].iloc[sorted_idx]
        X_sorted_d = sm.add_constant(sorted_x)
        y_pred = model.predict(X_sorted_d)
        ax.plot(sorted_x, y_pred, color='red', linewidth=2, label='Regression')
        ax.set_xlabel("Tariff Δ (bps)")
        ax.set_ylabel(label)
        ax.set_title(f"Impact of Tariff Δ on {label}")
        ax.legend()
    
    # Hide any unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')
    
    plt.suptitle("Impact of Year-to-Year Tariff Change on Each Metric", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    new_deltas_path = os.path.join(output_folder, "delta_relationships.png")
    plt.savefig(new_deltas_path)
    plt.close()
    print(f"Delta relationships plot saved to {new_deltas_path}")

def main():
    run_visualizations()

if __name__ == "__main__":
    main()
