from src.db_manager import initialize_database
from src.visualize import run_tariff_macro_analysis
from src.fetch_macro_data import fetch_and_store_macro_data_as_economic_impact
from src.fetch_tariffs import process_tariff_data
def main():

    # Initialize the database and create tables
    print("Initializing database...")
    initialize_database()

    # fetch and store tariff data
    print("Fetching and storing tariff data...")
    process_tariff_data()
    print("Tariff data processing completed.")

    # fetch and store macroeconomic data
    print("Fetching and storing macroeconomic data...")
    fetch_and_store_macro_data_as_economic_impact()
    print("Macroeconomic data fetching and storing completed.")
    
    # Run the tariff analysis which now fetches macro data, merges it, and stores the result in economic_impact
    print("Running tariff analysis and merging macro data into economic_impact...")
    run_tariff_macro_analysis()
    print("Tariff regression and merged economic impact analysis completed.")

    
if __name__ == "__main__":
    main()
