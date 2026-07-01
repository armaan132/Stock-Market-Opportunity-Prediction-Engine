# Data Contract

The default pipeline fetches real S&P 500 data from public APIs and writes normalized CSV files to `data/raw/`. The same schema can also be supplied manually through CSV files. Synthetic data is available only through `--source synthetic` for offline demos and tests.

## Real API Sources

| Source | Purpose |
| --- | --- |
| Wikipedia S&P 500 table | Current S&P 500 ticker universe, company names, and sectors |
| SEC Company Facts API | Annual financial statement fundamentals from public filings |
| yfinance | Historical stock prices and S&P 500 benchmark prices |

## `data/raw/financials.csv`

One row per company and fiscal year.

| Column | Type | Description |
| --- | --- | --- |
| `ticker` | string | Company ticker or stable identifier |
| `company_name` | string | Company display name |
| `sector` | string | Sector classification |
| `fiscal_year` | integer | Fiscal year for the financial statement |
| `revenue` | float | Annual revenue |
| `earnings` | float | Net earnings |
| `profit_margin` | float | Earnings divided by revenue |
| `operating_margin` | float | Operating income divided by revenue |
| `free_cash_flow` | float | Annual free cash flow |
| `debt` | float | Total debt |
| `equity` | float | Shareholders' equity |
| `assets` | float | Total assets |
| `current_ratio` | float | Current assets divided by current liabilities |
| `market_cap` | float | Market capitalization at the observation date |
| `pe_ratio` | float | Price-to-earnings ratio |
| `pb_ratio` | float | Price-to-book ratio |
| `rd_spending` | float | Research and development spending |
| `employee_growth` | float | Year-over-year employee growth rate |

## `data/raw/prices.csv`

One row per company and fiscal year. The return columns must be measured after the fiscal-year observation date.

| Column | Type | Description |
| --- | --- | --- |
| `ticker` | string | Company ticker or stable identifier |
| `fiscal_year` | integer | Fiscal year matching `financials.csv` |
| `sp500_return_next_12m` | float | S&P 500 forward 12-month return |
| `stock_return_next_12m` | float | Company forward 12-month return |
| `close_price_year_end` | float | Company year-end close price |

## Generated Outputs

| File | Description |
| --- | --- |
| `data/processed/market_opportunity.sqlite` | SQLite database containing raw financials and return labels |
| `data/processed/modeling_frame.csv` | Engineered feature table used for model training |
| `data/processed/model_metrics.csv` | Time-holdout model metrics |
| `data/processed/latest_predictions.csv` | Latest-year ranked opportunity probabilities |
| `data/processed/feature_importance.csv` | Random Forest feature importance values from the ensemble |
| `models/opportunity_model.joblib` | Serialized trained pipeline |

## Leakage Rules

- Do not use future returns, future fundamentals, analyst revisions, or post-observation labels as model features.
- `stock_return_next_12m` and `sp500_return_next_12m` are labels only.
- Forward-return labels are created only when the ending calendar year has a December close. Partial current-year returns are excluded.
- Any future data provider integration should preserve point-in-time availability.
