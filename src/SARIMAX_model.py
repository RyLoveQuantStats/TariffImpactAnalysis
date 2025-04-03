import os
import sqlite3
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from src.config import DB_PATH, OUTPUT_PATH

def load_economic_impact():
    """
    Load economic impact data from the economic_impact table.
    Converts the 'year' column into a DateTimeIndex.
    Assumes the table includes at least columns: 'year', 'GDP', 'CPI',
    'Unemployment_Rate', and 'Industrial_Production'.
    """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM economic_impact WHERE year >= 1996 ORDER BY year"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['year'] = df['year'].astype(int)
    df['date'] = pd.to_datetime(df['year'], format='%Y')
    df.set_index('date', inplace=True)
    return df

def compute_deltas(economic_df):
    """
    Compute year-to-year differences (deltas) for GDP, CPI, Unemployment_Rate,
    and Industrial_Production. These deltas are what we will forecast.
    """
    economic_df['delta_GDP'] = economic_df['GDP'].diff()
    economic_df['cpi_delta'] = economic_df['CPI'].diff()
    economic_df['unemployment_delta'] = economic_df['Unemployment_Rate'].diff()
    economic_df['industrial_delta'] = economic_df['Industrial_Production'].diff()
    # Drop the first row with NaN differences
    economic_df = economic_df.dropna(subset=['delta_GDP', 'cpi_delta', 'unemployment_delta', 'industrial_delta'])
    return economic_df

def load_new_tariffs():
    """
    Load new tariff data from the new_tariffs table.
    The table contains columns: country, tariff_charged_us, and usa_discounted_tariff.
    """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM new_tariffs"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def aggregate_new_tariff(new_tariff_df):
    """
    Aggregate new tariff data to obtain a single measure.
    Here we use the average of the 'tariff_charged_us' values.
    """
    avg_tariff = new_tariff_df['tariff_charged_us'].mean()
    return avg_tariff

def build_and_forecast_arimax(economic_df, exog_value, forecast_date, target_column, order=(1,1,0)):
    """
    Build an ARIMAX model to forecast the delta change of a specified macro variable
    using the aggregated new tariff measure as an exogenous regressor.
    
    Parameters:
        economic_df  : DataFrame with a DateTimeIndex containing historical delta values of target_column.
        exog_value   : The aggregated new tariff measure (e.g., average tariff_charged_us).
        forecast_date: A DateTime index value for the forecast period.
        target_column: The delta column to forecast (e.g., 'delta_GDP', 'cpi_delta', etc.).
        order        : The (p,d,q) order for the ARIMAX model.
    
    Returns:
        The forecasted delta value for target_column for forecast_date and the model summary.
    """
    endog = economic_df[target_column]
    # Create an exogenous series that is constant (the aggregated new tariff) over the historical period.
    exog = pd.Series(exog_value, index=economic_df.index, name='new_delta_tariff')
    model = SARIMAX(endog, exog=exog, order=order)
    model_fit = model.fit(disp=False)
    new_exog = pd.DataFrame({'new_delta_tariff': [exog_value]}, index=[forecast_date])
    forecast = model_fit.get_forecast(steps=1, exog=new_exog)
    return forecast.predicted_mean.values[0], model_fit.summary()

if __name__ == "__main__":
    # STEP 1: Load historical economic impact data and compute deltas.
    economic_df = load_economic_impact()
    economic_df = compute_deltas(economic_df)
    
    # STEP 2: Load new tariff data and aggregate the tariff measure.
    new_tariff_df = load_new_tariffs()
    aggregated_new_tariff = aggregate_new_tariff(new_tariff_df)
    print("Aggregated New Tariff (avg of tariff_charged_us):", aggregated_new_tariff)
    
    # STEP 3: Define forecast date (one year after the latest available date).
    last_year = economic_df.index[-1].year
    forecast_date = pd.to_datetime(str(last_year + 1), format='%Y')
    
    # STEP 4: Define the delta variables to forecast.
    target_deltas = ['delta_GDP', 'cpi_delta', 'unemployment_delta', 'industrial_delta']
    
    forecasts = {}
    summaries = {}
    for target in target_deltas:
        fc, summary = build_and_forecast_arimax(economic_df, aggregated_new_tariff, forecast_date, target)
        forecasts[target] = fc
        summaries[target] = summary
        print("Forecasted {} for {}: {:.2f}".format(target, forecast_date.year, fc))
    
    # STEP 5: Create a multi-panel (2x2) plot for the historical delta series and forecasts.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    axes = axes.flatten()  # Flatten the 2D array for easy iteration

    for i, target in enumerate(target_deltas):
        ax = axes[i]
        # Plot historical delta values.
        ax.plot(economic_df.index, economic_df[target], marker='o', label='Historical ' + target)
        # Mark the last historical data point.
        last_value = economic_df[target].iloc[-1]
        ax.plot(economic_df.index[-1], last_value, 'bo', label='Last Year ({})'.format(economic_df.index[-1].year))
        # Plot the forecasted delta.
        ax.plot(forecast_date, forecasts[target], 'ro', label='Forecast ({})'.format(forecast_date.year))
        # Draw a vertical line indicating the forecast start.
        ax.axvline(economic_df.index[-1], color='gray', linestyle='--', label='Forecast Start')
        ax.set_title(f"{target} Forecast vs. Last Year")
        ax.set_xlabel("Year")
        ax.set_ylabel(target)
        ax.legend()

    plt.tight_layout()
    # Save the multi-panel figure to the outputs folder.
    save_path = os.path.join(OUTPUT_PATH, "SARIMAX_ECONOMIC_FORECAST.png")
    plt.savefig(save_path)
    plt.show()
