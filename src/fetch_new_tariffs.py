import sqlite3
from src.config import DB_PATH  # Update if you store your DB path differently

def store_new_reciprocal_tariffs():
    """
    Creates a new table 'new_tariffs' (if not exists)
    and inserts the hard-coded  tariff data extracted from the images.
    'tariff_charged_us' and 'usa_discounted_tariff' are stored as numeric percentages
    (e.g. 67.0 means 67%).
    """
    # Hard-coded data from the two images:
    tariff_data = [
        # Image 1
        {"country": "China",             "tariff_charged_us": 67.0, "usa_discounted_tariff": 34.0},
        {"country": "European Union",    "tariff_charged_us": 39.0, "usa_discounted_tariff": 20.0},
        {"country": "Vietnam",           "tariff_charged_us": 64.0, "usa_discounted_tariff": 22.0},
        {"country": "Taiwan",            "tariff_charged_us": 52.0, "usa_discounted_tariff": 26.0},
        {"country": "Japan",             "tariff_charged_us": 50.0, "usa_discounted_tariff": 24.0},
        {"country": "India",             "tariff_charged_us": 54.0, "usa_discounted_tariff": 28.0},
        {"country": "South Korea",       "tariff_charged_us": 62.0, "usa_discounted_tariff": 28.0},
        {"country": "Thailand",          "tariff_charged_us": 72.0, "usa_discounted_tariff": 36.0},
        {"country": "Switzerland",       "tariff_charged_us": 64.0, "usa_discounted_tariff": 32.0},
        {"country": "Indonesia",         "tariff_charged_us": 59.0, "usa_discounted_tariff": 30.0},
        {"country": "Malaysia",          "tariff_charged_us": 40.0, "usa_discounted_tariff": 25.0},
        {"country": "Cambodia",          "tariff_charged_us": 63.0, "usa_discounted_tariff": 32.0},
        {"country": "United Kingdom",    "tariff_charged_us": 48.0, "usa_discounted_tariff": 20.0},
        {"country": "South Africa",      "tariff_charged_us": 55.0, "usa_discounted_tariff": 22.0},
        {"country": "Brazil",            "tariff_charged_us": 60.0, "usa_discounted_tariff": 20.0},
        {"country": "Bangladesh",        "tariff_charged_us": 44.0, "usa_discounted_tariff": 20.0},
        {"country": "Singapore",         "tariff_charged_us": 18.0, "usa_discounted_tariff": 10.0},
        {"country": "Israel",            "tariff_charged_us": 40.0, "usa_discounted_tariff": 20.0},
        {"country": "Philippines",       "tariff_charged_us": 37.0, "usa_discounted_tariff": 19.0},
        {"country": "Chile",             "tariff_charged_us": 14.0, "usa_discounted_tariff": 10.0},
        {"country": "Australia",         "tariff_charged_us": 13.0, "usa_discounted_tariff": 10.0},
        {"country": "Pakistan",          "tariff_charged_us": 38.0, "usa_discounted_tariff": 19.0},
        {"country": "Turkey",            "tariff_charged_us": 58.0, "usa_discounted_tariff": 28.0},
        {"country": "Sri Lanka",         "tariff_charged_us": 60.0, "usa_discounted_tariff": 25.0},

        # Image 2
        {"country": "Peru",              "tariff_charged_us": 10.0, "usa_discounted_tariff": 10.0},
        {"country": "Nicaragua",         "tariff_charged_us": 36.0, "usa_discounted_tariff": 18.0},
        {"country": "Norway",            "tariff_charged_us": 30.0, "usa_discounted_tariff": 17.0},
        {"country": "Costa Rica",        "tariff_charged_us": 17.0, "usa_discounted_tariff": 10.0},
        {"country": "Jordan",            "tariff_charged_us": 15.0, "usa_discounted_tariff": 10.0},
        {"country": "Dominican Republic","tariff_charged_us": 14.0, "usa_discounted_tariff": 10.0},
        {"country": "United Arab Emirates","tariff_charged_us": 20.0, "usa_discounted_tariff": 10.0},
        {"country": "Argentina",         "tariff_charged_us": 20.0, "usa_discounted_tariff": 10.0},
        {"country": "Ecuador",           "tariff_charged_us": 10.0, "usa_discounted_tariff": 10.0},
        {"country": "Guatemala",         "tariff_charged_us": 15.0, "usa_discounted_tariff": 10.0},
        {"country": "Honduras",          "tariff_charged_us": 10.0, "usa_discounted_tariff": 10.0},
        {"country": "Madagascar",        "tariff_charged_us": 40.0, "usa_discounted_tariff": 20.0},
        {"country": "Myanmar (Burma)",   "tariff_charged_us": 38.0, "usa_discounted_tariff": 20.0},
        {"country": "Tunisia",           "tariff_charged_us": 54.0, "usa_discounted_tariff": 28.0},
        {"country": "Kazakhstan",        "tariff_charged_us": 24.0, "usa_discounted_tariff": 10.0},
        {"country": "Serbia",            "tariff_charged_us": 25.0, "usa_discounted_tariff": 10.0},
        {"country": "Egypt",             "tariff_charged_us": 18.0, "usa_discounted_tariff": 10.0},
        {"country": "El Salvador",       "tariff_charged_us": 15.0, "usa_discounted_tariff": 10.0},
        {"country": "Côte d'Ivoire",     "tariff_charged_us": 15.0, "usa_discounted_tariff": 10.0},
        {"country": "Laos",              "tariff_charged_us": 48.0, "usa_discounted_tariff": 20.0},
        {"country": "Trinidad and Tobago","tariff_charged_us": 74.0, "usa_discounted_tariff": 30.0},
        {"country": "Morocco",           "tariff_charged_us": 10.0, "usa_discounted_tariff": 10.0},
    ]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create a new table (if not exists) to store these rates
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS new_tariffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        tariff_charged_us REAL,
        usa_discounted_tariff REAL
    );
    """
    cur.execute(create_table_sql)

    # Optional: Clear existing data in case you want to refresh each run
    # cur.execute("DELETE FROM new_tariffs;")

    # Insert the data
    insert_sql = """
    INSERT INTO new_tariffs (country, tariff_charged_us, usa_discounted_tariff)
    VALUES (?, ?, ?)
    """
    for row in tariff_data:
        cur.execute(insert_sql, (
            row["country"],
            row["tariff_charged_us"],
            row["usa_discounted_tariff"]
        ))

    conn.commit()
    conn.close()

    print("New reciprocal tariffs have been successfully stored in 'new_tariffs' table.")

if __name__ == "__main__":
    store_new_reciprocal_tariffs()
