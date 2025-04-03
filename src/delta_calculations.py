import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src.db_utils import fetch_query, store_dataframe

def calculate_economic_impact():
    """
    Loads tariff data from the 'tariffs' table and macro data (CPI, Unemployment_Rate, 
    Industrial_Production, GDP) from the 'economic_impact' table (previously loaded).
    It then:
      - Aggregates tariff data (average tariff rate from applied data, total imports and exports).
      - Merges the tariff aggregates with the macro data on year.
      - Computes year-to-year differences (deltas) for:
            * Tariff rate (delta_tariff, in basis points),
            * Imports and exports (delta_imports, delta_exports in billions USD),
            * GDP (delta_GDP),
            * CPI (cpi_delta),
            * Unemployment Rate (unemployment_delta),
            * Industrial Production (industrial_delta).
      - Overwrites the 'economic_impact' table with the merged results.
    """
    # --- Part 1: Process Tariff Data from the 'tariffs' table ---
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
    
    # --- Part 2: (Optional) Regression Analysis ---
    X = sm.add_constant(analysis_df['avg_tariff_rate'])
    model_imports = sm.OLS(analysis_df['imports_value'], X).fit()
    model_exports = sm.OLS(analysis_df['exports_value'], X).fit()
    print("Regression Summary for Imports:")
    print(model_imports.summary())
    print("Regression Summary for Exports:")
    print(model_exports.summary())
    
    # --- Part 3: Compute Year-to-Year Differences for Tariff Data ---
    analysis_df['delta_tariff'] = analysis_df['avg_tariff_rate'].diff() * 100  # in bps
    analysis_df['delta_imports'] = analysis_df['imports_value'].diff() / 1e9   # in billions USD
    analysis_df['delta_exports'] = analysis_df['exports_value'].diff() / 1e9   # in billions USD
    
    # --- Part 4: Load Macro Data from the economic_impact table ---
    # (Assuming your macro data has already been loaded into economic_impact without the delta columns)
    macro_df = fetch_query("SELECT * FROM economic_impact")
    # We assume macro_df already has CPI, Unemployment_Rate, Industrial_Production, GDP and year.
    macro_df = macro_df.drop_duplicates(subset='year')
    
    # --- Part 5: Merge Tariff and Macro Data ---
    merged_df = pd.merge(analysis_df, macro_df[['year', 'GDP', 'CPI', 'Unemployment_Rate', 'Industrial_Production']], 
                         on='year', how='inner')
    merged_df.sort_values('year', inplace=True)
    
    # Compute delta for GDP (assumed to be in billions USD already)
    merged_df['delta_GDP'] = merged_df['GDP'].diff()
    
    # --- Part 6: Compute New Deltas for Macro Indicators ---
    merged_df['cpi_delta'] = merged_df['CPI'].diff()
    merged_df['unemployment_delta'] = merged_df['Unemployment_Rate'].diff()
    merged_df['industrial_delta'] = merged_df['Industrial_Production'].diff()
    
    # Drop rows with NaN in any of the key delta columns
    merged_df.dropna(subset=['delta_tariff', 'delta_imports', 'delta_exports', 'delta_GDP',
                               'cpi_delta', 'unemployment_delta', 'industrial_delta'], inplace=True)
    
    # --- Part 7: Create Final Merged DataFrame and Store ---
    economic_df = merged_df[['year', 'avg_tariff_rate', 'delta_tariff', 'imports_value', 'exports_value',
                               'delta_imports', 'delta_exports', 'GDP', 'delta_GDP', 'CPI',
                               'Unemployment_Rate', 'Industrial_Production', 'cpi_delta',
                               'unemployment_delta', 'industrial_delta']].copy()
    
    store_dataframe(economic_df, "economic_impact")
    print("Merged economic impact data saved to table 'economic_impact':")
    print(economic_df.head())

def main():
    calculate_economic_impact()

if __name__ == "__main__":
    main()
