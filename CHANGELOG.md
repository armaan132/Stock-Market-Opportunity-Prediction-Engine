# Changelog

All notable project changes should be summarized here so the repository has a readable history beyond raw git commits.

## Unreleased

- Implemented the first runnable end-to-end market opportunity prediction platform.
- Added synthetic demo data generation for 120 public-company-like tickers across 10+ fiscal years.
- Added SQLite-backed ingestion for financial statement data and forward market returns.
- Added feature engineering for growth, margins, leverage, valuation, returns on capital, cash flow, R&D, and sector.
- Added time-based model validation and saved evaluation metrics.
- Added a soft-voting ensemble classifier using Logistic Regression and Random Forest models.
- Added ranked latest-year opportunity predictions and feature importance output.
- Added a Streamlit dashboard for model metrics, opportunity rankings, probability distribution, and feature drivers.
- Added tests, linting configuration, packaging metadata, and repository documentation.
