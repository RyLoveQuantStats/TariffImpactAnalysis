import pandas as pd
from fredapi import Fred
from src.config import FRED_API_KEY
from src.db_utils import store_dataframe

def fetch_and_store_macro_data_as_economic_impact():
    """
    Fetches key macroeconomic indicators from FRED, resamples the data to only include
    the first available observation for each year (typically January 1), filters the data
    for the period 1996-2024, adds a 'year' column, and stores the result in a new 
    database table called "economic_impact".
    
    Macroeconomic series fetched:
      - CPI (Consumer Price Index for All Urban Consumers: All Items, 'CPIAUCSL')
      - Unemployment Rate ('UNRATE')
      - Industrial Production Index ('INDPRO')
      - GDP (Gross Domestic Product, 'GDP')
    """
    # Initialize the Fred client using your API key from config.py
    fred = Fred(api_key=FRED_API_KEY)
    
    # Fetch macroeconomic indicators from FRED
    cpi = fred.get_series('CPIAUCSL')
    unrate = fred.get_series('UNRATE')
    indpro = fred.get_series('INDPRO')
    gdp = fred.get_series('GDP')
    
    # Convert each series to a DataFrame and reset the index so that Date becomes a column.
    cpi_df = cpi.to_frame(name="CPI").reset_index().rename(columns={"index": "Date"})
    unrate_df = unrate.to_frame(name="Unemployment_Rate").reset_index().rename(columns={"index": "Date"})
    indpro_df = indpro.to_frame(name="Industrial_Production").reset_index().rename(columns={"index": "Date"})
    gdp_df = gdp.to_frame(name="GDP").reset_index().rename(columns={"index": "Date"})
    
    # Merge all DataFrames on 'Date' using an outer join to preserve all data points.
    macro_df = pd.merge(cpi_df, unrate_df, on="Date", how="outer")
    macro_df = pd.merge(macro_df, indpro_df, on="Date", how="outer")
    macro_df = pd.merge(macro_df, gdp_df, on="Date", how="outer")
    
    # Convert 'Date' to datetime and sort
    macro_df['Date'] = pd.to_datetime(macro_df['Date'])
    macro_df.sort_values("Date", inplace=True)
    
    # Resample to Annual Start ('AS') - take the first available observation for each year.
    macro_df = macro_df.set_index("Date").resample("AS").first().reset_index()
    
    # Filter data for the period 1996-2024
    start_date = pd.to_datetime("1996-01-01")
    end_date = pd.to_datetime("2024-12-31")
    macro_df = macro_df[(macro_df['Date'] >= start_date) & (macro_df['Date'] <= end_date)]
    
    # Add a 'year' column extracted from the Date.
    macro_df['year'] = macro_df['Date'].dt.year
    
    # Store the resulting DataFrame in the database under the table 'economic_impact'
    store_dataframe(macro_df, "economic_impact")
    
    print("Macro data stored in table 'economic_impact' (Annual data from 1996 to 2024):")
    print(macro_df.head())

if __name__ == "__main__":
    fetch_and_store_macro_data_as_economic_impact()
