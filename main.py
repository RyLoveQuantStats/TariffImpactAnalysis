from src.db_manager import initialize_database
from src.fetch_macro_data import fetch_and_store_macro_data_as_economic_impact
from src.fetch_tariffs import process_tariff_data
from src.delta_calculations import calculate_economic_impact
from src.visuals import run_visualizations

def main():

    # Initialize the database and create tables
    print("Initializing database...")
    initialize_database()

    # fetch and store tariff data
    print("Fetching and storing tariff data...")
    #process_tariff_data()
    print("Tariff data processing completed.")

    # fetch and store macroeconomic data
    print("Fetching and storing macroeconomic data...")
    #fetch_and_store_macro_data_as_economic_impact()
    print("Macroeconomic data fetching and storing completed.")
    
    # store new reciprocal tariffs
    print("Storing new reciprocal tariffs...")
    #store_new_reciprocal_tariffs()
    print("New reciprocal tariffs stored successfully.")
    
    # calculate economic impact
    print("Calculating economic impact...")
    calculate_economic_impact()
    print("Economic impact calculation completed.")

    # Run visualizations
    print("Generating visualizations...")
    run_visualizations()
    print("Visualizations generated.")

    
if __name__ == "__main__":
    main()
