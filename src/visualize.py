import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
from src.db_utils import fetch_query, store_dataframe

def run_tariff_macro_analysis():
    """
    This function:
      1. Loads and processes tariff data from the 'tariffs' table,
         aggregating by year to obtain average tariff rates (from applied data)
         and total imports and exports.
      2. Loads macroeconomic data (including GDP) from the 'economic_impact' table.
      3. Merges the tariff data with macro data on year.
      4. Performs regression analysis of trade values on tariff rates.
      5. Computes year-to-year differences (deltas) for tariffs, imports, exports, and GDP,
         and stores these deltas in a new table 'tariff_changes'.
      6. Computes and prints a correlation matrix for tariff rates, trade values, and macro indicators.
      7. Creates and saves visualizations:
           - A scatter plot with regression lines (trade vs. tariff rate)
           - A two-subplot figure: 
               Top: Year-to-year changes in tariff rates (bps)
               Bottom: Grouped bar chart of year-to-year changes in imports (B USD), exports (B USD), and GDP (B USD)
           - A heatmap of the correlation matrix.
    """
    # -----------------------------
    # Part 1: Load and Process Tariff Data
    # -----------------------------
    tariffs_df = fetch_query("SELECT * FROM tariffs")
    tariffs_df['year'] = tariffs_df['year'].astype(int)
    
    # Separate by data_type
    applied_df = tariffs_df[tariffs_df['data_type'] == 'applied']
    imports_df = tariffs_df[tariffs_df['data_type'] == 'imports']
    exports_df = tariffs_df[tariffs_df['data_type'] == 'exports']
    
    # Aggregate tariff data by year (using trade_weighted as tariff measure)
    applied_agg = applied_df.groupby('year')['trade_weighted'].mean().reset_index()
    applied_agg.rename(columns={'trade_weighted': 'avg_tariff_rate'}, inplace=True)
    
    # Aggregate imports and exports (summing trade values)
    imports_agg = imports_df.groupby('year')['value'].sum().reset_index()
    imports_agg.rename(columns={'value': 'imports_value'}, inplace=True)
    
    exports_agg = exports_df.groupby('year')['value'].sum().reset_index()
    exports_agg.rename(columns={'value': 'exports_value'}, inplace=True)
    
    # Merge aggregated tariff data
    analysis_df = pd.merge(applied_agg, imports_agg, on='year', how='inner')
    analysis_df = pd.merge(analysis_df, exports_agg, on='year', how='inner')
    analysis_df.sort_values('year', inplace=True)
    
    print("Merged Tariff Data:")
    print(analysis_df)
    
    # -----------------------------
    # Part 2: Regression Analysis on Tariff vs. Trade
    # -----------------------------
    X = sm.add_constant(analysis_df['avg_tariff_rate'])
    model_imports = sm.OLS(analysis_df['imports_value'], X).fit()
    model_exports = sm.OLS(analysis_df['exports_value'], X).fit()
    print("Regression Summary for Imports:")
    print(model_imports.summary())
    print("Regression Summary for Exports:")
    print(model_exports.summary())
    
    # -----------------------------
    # Part 3: Compute Year-to-Year Differences (Deltas) and Save to DB
    # -----------------------------
    # Compute deltas for tariff rate (in basis points), imports and exports (in billions USD)
    analysis_df['delta_tariff'] = analysis_df['avg_tariff_rate'].diff() * 100  
    analysis_df['delta_imports'] = analysis_df['imports_value'].diff() / 1e9  
    analysis_df['delta_exports'] = analysis_df['exports_value'].diff() / 1e9  
    
    # -----------------------------
    # Part 4: Load Macro Data and Merge with Tariff Data
    # Fetch macro data from the temporary table (created by fetch_economic_impact.py)
    macro_df = fetch_query("SELECT * FROM economic_impact")
    # Extract year from the Date column and remove the Date field if present
    macro_df['year'] = pd.to_datetime(macro_df['Date']).dt.year
    macro_df = macro_df.drop(columns=['Date'], errors='ignore')
    macro_df = macro_df.drop_duplicates(subset='year')
    
    # Merge tariff aggregated data with macro data on year
    merged_df = pd.merge(analysis_df, macro_df, on='year', how='inner')
    merged_df.sort_values('year', inplace=True)
    
    # Compute delta for GDP (assuming GDP is in billions USD already)
    merged_df['delta_GDP'] = merged_df['GDP'].diff()
    
    # Drop rows with NaN in any of the delta columns
    merged_df.dropna(subset=['delta_tariff', 'delta_imports', 'delta_exports', 'delta_GDP'], inplace=True)
    
    # Create the final merged DataFrame with all desired columns
    economic_df = merged_df[['year', 'avg_tariff_rate', 'delta_tariff', 'imports_value', 'exports_value',
                               'delta_imports', 'delta_exports', 'GDP', 'delta_GDP', 'CPI',
                               'Unemployment_Rate', 'Industrial_Production']].copy()
    # Store the merged data into the economic_impact table
    store_dataframe(economic_df, "economic_impact")
    print("Merged economic impact data saved to table 'economic_impact':")
    print(economic_df.head())

    
    # -----------------------------
    # Part 5: Correlation Analysis
    # -----------------------------
    corr_vars = ['avg_tariff_rate', 'imports_value', 'exports_value', 
                 'CPI', 'Unemployment_Rate', 'Industrial_Production', 'GDP']
    corr_df = merged_df[corr_vars].corr()
    print("Correlation Matrix:")
    print(corr_df)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix: Tariff & Macro Data")
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    corr_plot_path = os.path.join(output_folder, "correlation_matrix.png")
    plt.tight_layout()
    plt.savefig(corr_plot_path)
    plt.close()
    print(f"Correlation matrix plot saved to {corr_plot_path}")
    
    # -----------------------------
    # Part 6: Visualizations (Tariff & Trade)
    # -----------------------------
    # Plot 1: Scatter Plot with Regression Lines
    plt.figure(figsize=(8, 5))
    plt.scatter(analysis_df['avg_tariff_rate'], analysis_df['imports_value'], 
                label="Imports Data Points", color="blue")
    plt.scatter(analysis_df['avg_tariff_rate'], analysis_df['exports_value'], 
                label="Exports Data Points", color="green")
    
    sorted_idx = analysis_df['avg_tariff_rate'].argsort()
    sorted_x = analysis_df['avg_tariff_rate'].iloc[sorted_idx]
    X_sorted = sm.add_constant(sorted_x)
    imports_pred = model_imports.predict(X_sorted)
    exports_pred = model_exports.predict(X_sorted)
    
    plt.plot(sorted_x, imports_pred, color='blue', label="Imports Regression Line")
    plt.plot(sorted_x, exports_pred, color='green', label="Exports Regression Line")
    
    plt.xlabel("Average Tariff Rate (Trade-Weighted)")
    plt.ylabel("Trade Value")
    plt.title("Trade Value vs. Tariff Rate")
    plt.legend()
    plt.tight_layout()
    scatter_plot_path = os.path.join(output_folder, "scatter_regression.png")
    plt.savefig(scatter_plot_path)
    plt.close()
    
    # Plot 2: Two Subplots - Tariff Changes (top) and Trade & GDP Changes (bottom)
    years_str = merged_df['year'].astype(str).values
    x = np.arange(len(years_str))
    # Adjust bar width for three groups in the lower subplot
    width = 0.25
    
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    fig.suptitle("Year-to-Year Tariff, Trade, & GDP Changes", y=0.95, fontsize=14)
    
    # Top Subplot: Tariff Δ (Bar Chart)
    ax1.bar(x, merged_df['delta_tariff'], width, color='purple', label='Tariff Δ (bps)')
    ax1.axhline(0, color='black', linewidth=0.8)
    ax1.set_ylabel("Tariff Change (bps)")
    ax1.set_title("Year-to-Year Tariff Changes", fontsize=12)
    ax1.legend(loc='upper left')
    
    # Bottom Subplot: Imports, Exports, & GDP Δ (Grouped Bar Chart)
    rects1 = ax2.bar(x - width, merged_df['delta_imports'], width, color='blue', label='Imports Δ (B USD)')
    rects2 = ax2.bar(x, merged_df['delta_exports'], width, color='green', label='Exports Δ (B USD)')
    rects3 = ax2.bar(x + width, merged_df['delta_GDP'], width, color='orange', label='GDP Δ (B USD)')
    
    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_ylabel("Change (Billions USD)")
    ax2.set_title("Year-to-Year Changes in Trade & GDP", fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(years_str, rotation=45)
    ax2.legend(loc='upper left')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    delta_plot_path = os.path.join(output_folder, "year_to_year_subplots.png")
    plt.savefig(delta_plot_path)
    plt.close()
    
    print(f"Plots saved in folder: {output_folder}")

if __name__ == "__main__":
    run_tariff_macro_analysis()
