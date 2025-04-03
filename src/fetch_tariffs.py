import os
import pandas as pd
from src.db_utils import store_dataframe

def process_tariff_data():
    """
    Processes the tariff CSV files, combines them into a unified DataFrame,
    and stores the result in the 'tariffs' table of the SQLite database.
    """
    # Define the folder containing the CSV files
    base_folder = "data/tariffs/"

    # Define file paths for the three CSVs
    imports_csv = os.path.join(base_folder, "imports.csv")
    exports_csv = os.path.join(base_folder, "exports.csv")
    applied_csv = os.path.join(base_folder, "applied.csv")

    # Define the unified columns for the final table
    unified_columns = [
        "data_type",
        "reporter_name",
        "reporter_code",
        "year",
        "classification",
        "classification_version",
        "product_code",
        "mtn_categories",
        "partner_code",
        "partner_name",
        "value",
        "duty_scheme_code",
        "duty_scheme_name",
        "simple_average",
        "trade_weighted",
        "duty_free_share"
    ]

    # --- Process Imports CSV ---
    imports_df = pd.read_csv(imports_csv)
    imports_df["data_type"] = "imports"
    for col in ["duty_scheme_code", "duty_scheme_name", "simple_average", "trade_weighted", "duty_free_share"]:
        imports_df[col] = None
    imports_df = imports_df[unified_columns]

    # --- Process Exports CSV ---
    exports_df = pd.read_csv(exports_csv)
    exports_df["data_type"] = "exports"
    for col in ["duty_scheme_code", "duty_scheme_name", "simple_average", "trade_weighted", "duty_free_share"]:
        exports_df[col] = None
    exports_df = exports_df[unified_columns]

    # --- Process Applied CSV ---
    applied_df = pd.read_csv(applied_csv)
    applied_df["data_type"] = "applied"
    for col in ["partner_code", "partner_name", "value"]:
        applied_df[col] = None
    applied_df = applied_df[unified_columns]

    # --- Combine All DataFrames ---
    unified_df = pd.concat([imports_df, exports_df, applied_df], ignore_index=True)
    print("Unified DataFrame preview:")
    print(unified_df.head())

    # --- Store into the 'tariffs' table in SQLite ---
    store_dataframe(unified_df, "tariffs")
    print("Tariff data stored successfully.")

def main():
    process_tariff_data()

if __name__ == "__main__":
    main()
