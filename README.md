# Tariff Impact Analysis Project
This project combines trade flow analysis, inflation impact analysis, and sentiment analysis of tariff impacts using Python and SQLite.
## Project Structure
- **data/**: Raw data and filings.
- **database/**: SQLite database.
- **notebooks/**: Jupyter Notebooks for exploratory data analysis.
- **src/**: Source code modules.
  - **config.py**: Configuration settings.
  - **db_utils.py**: Database utility functions.
  - **db_manager.py**: Database initialization and management.
  - **schema.py**: Database schema definitions.
  - **trade_flow.py**: Trade flow data fetching and processing.
  - **inflation_model.py**: CPI data analysis and regression.
  - **sentiment_nlp.py**: Sentiment analysis of tariff-related text.
- **scripts/**: Utility scripts (e.g., shell scripts to run the project).
- **main.py**: Main entry point that runs the analysis.
## Usage
1. **Initialize the database:**  
   Run `python3 -m src.db_manager` to create the SQLite database and tables.
2. **Run the analysis:**  
   Execute `python3 main.py` or run the provided shell script: `./scripts/run_main.sh`
3. **Explore further:**  
   Use the notebooks in the **notebooks/** folder for exploratory data analysis.
