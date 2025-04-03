def create_tables(conn):
    cursor = conn.cursor()
    
    # Tariffs table remains unchanged
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tariffs (
        data_type TEXT,
        reporter_name TEXT,
        reporter_code TEXT,
        year INTEGER,
        classification TEXT,
        classification_version TEXT,
        product_code TEXT,
        mtn_categories TEXT,
        partner_code TEXT,
        partner_name TEXT,
        value REAL,
        duty_scheme_code TEXT,
        duty_scheme_name TEXT,
        simple_average REAL,
        trade_weighted REAL,
        duty_free_share REAL
    );
    """)

    # Merged Economic Impact table (combining tariff deltas and macro data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS economic_impact (
        year INTEGER PRIMARY KEY,
        avg_tariff_rate REAL,
        delta_tariff REAL,
        imports_value REAL,
        exports_value REAL,
        delta_imports REAL,
        delta_exports REAL,
        GDP REAL,
        delta_GDP REAL,
        CPI REAL,
        Unemployment_Rate REAL,
        Industrial_Production REAL
    );
    """)

    conn.commit()
