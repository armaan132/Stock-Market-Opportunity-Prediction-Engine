# Architecture

The project is structured as a small, end-to-end machine learning platform. Each layer has a narrow responsibility so the system is easy to test, extend, and explain.

## System Flow

```text
S&P 500 list, SEC filings, yfinance prices, CSV files, or synthetic demo data
        |
        v
SQLite ingestion layer
        |
        v
Modeling frame join
        |
        v
Feature engineering
        |
        v
Time-based train/test split
        |
        v
Ensemble classifier
        |
        v
Metrics, rankings, feature importance, model artifact
        |
        v
Streamlit dashboard
```

## Source Layout

```text
app/
  streamlit_app.py              Interactive dashboard

src/market_opportunity/
  cli.py                        Command-line entrypoint
  config.py                     Central paths and settings
  features.py                   Modeling feature creation
  modeling.py                   Model definition, validation, metrics, artifacts
  pipeline.py                   Ingestion and training orchestration
  storage.py                    SQLite persistence and loading
  real_data.py                  Real S&P 500, SEC, and yfinance data ingestion
  synthetic.py                  Offline demo universe generation
  explain.py                    Feature-driver helpers

sql/
  schema.sql                    Relational table definitions

tests/
  test_features.py              Feature engineering regression tests
```

## Key Design Decisions

- The default local database is SQLite because it is simple to run and review. The schema is intentionally compatible with a later PostgreSQL migration.
- The default data source uses real public APIs: SEC Company Facts for annual fundamentals and yfinance for price returns.
- Synthetic data is retained as an explicit offline/demo mode, not as the primary project claim.
- Validation is time-based rather than randomly shuffled. This better reflects financial forecasting, where future observations must not leak into training.
- The saved prediction table contains the latest fiscal year only, while metrics are computed on a multi-year time holdout.
- Generated model artifacts and processed datasets are excluded from git to keep the repository lightweight and reproducible.

## Extension Points

- Move from SQLite to PostgreSQL for larger datasets and multi-user workflows.
- Add Financial Modeling Prep, Alpha Vantage, Polygon, or another paid fundamentals provider for richer fields.
- Add XGBoost, calibrated classifiers, or regression models for expected return estimation.
- Add SHAP summaries for deeper local and global explanation.
- Add scheduled retraining and model version tracking.
