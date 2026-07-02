# Financial Forecasting and Market Opportunity Analysis

An end-to-end data science and machine learning project that analyzes historical financial statement data to estimate the probability that publicly traded companies will outperform the broader market over the following 12 months.

Rather than attempting to predict short-term stock prices, this project focuses on long-term company fundamentals and interpretable machine learning techniques to understand the factors that contribute to sustained market outperformance.

---

## Purpose

The primary goal of this project is educational.

This repository is being developed to build a strong foundation in statistics, machine learning, data engineering, SQL, and software engineering by implementing each stage of a real-world data science workflow from scratch.

The emphasis is on understanding the underlying concepts, making design decisions independently, and developing interview-ready technical skills.

---

## Current Implementation

This repository now contains a runnable market opportunity prediction platform:

- A real-data ingestion layer for S&P 500 companies using SEC Company Facts and yfinance
- A CSV ingestion path for saved or vendor-provided financial datasets
- A synthetic demo mode for offline testing only
- SQLite storage for financial statements and forward returns
- Feature engineering for growth, profitability, leverage, valuation, cash flow, R&D, and sector variables
- Time-based validation to avoid training on future observations
- An ensemble classifier using Logistic Regression and Random Forest models
- Model metrics, ranked company predictions, and feature importance artifacts
- A Streamlit dashboard for exploring opportunity rankings and model drivers

The default task estimates:

> Given company fundamentals at fiscal year T, what is the probability that the company outperforms the S&P 500 over the next 12 months?

---

## Quickstart

```bash
make setup
make train
make app
```

By default, `make train` fetches real S&P 500 company fundamentals from the SEC and real market return data from yfinance. The default command limits the run to 120 S&P 500 companies so the project is practical on a laptop. Use `--limit 0` to request the full index.

Equivalent manual commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
market-opportunity train
streamlit run app/streamlit_app.py
```

Real-data examples:

```bash
market-opportunity train --source real --limit 120 --min-year 2014
market-opportunity train --source real --limit 0 --min-year 2014
```

Offline/demo examples:

```bash
market-opportunity train --source synthetic
market-opportunity train --source csv
```

Real API sources:

- S&P 500 constituents: Wikipedia's S&P 500 constituents table
- Annual fundamentals: SEC Company Facts API
- Stock and S&P 500 benchmark prices: yfinance

## Documentation

- [Architecture](docs/ARCHITECTURE.md): system flow, source layout, and design decisions
- [Data Contract](docs/DATA_CONTRACT.md): required input columns and generated outputs
- [Modeling](docs/MODELING.md): target definition, features, validation, model, and metrics
- [Project Structure](docs/PROJECT_STRUCTURE.md): tracked files, generated files, and directory conventions
- [Contributing](CONTRIBUTING.md): development workflow, commit style, and pull request checklist
- [Changelog](CHANGELOG.md): readable project history

### Expected Raw Data

`data/raw/financials.csv` should contain:

```text
ticker,company_name,sector,fiscal_year,revenue,earnings,profit_margin,operating_margin,free_cash_flow,debt,equity,assets,current_ratio,market_cap,pe_ratio,pb_ratio,rd_spending,employee_growth
```

`data/raw/prices.csv` should contain:

```text
ticker,fiscal_year,sp500_return_next_12m,stock_return_next_12m,close_price_year_end
```

Generated artifacts are written to:

- `data/processed/market_opportunity.sqlite`
- `data/processed/modeling_frame.csv`
- `data/processed/model_metrics.csv`
- `data/processed/backtest_results.csv`
- `data/processed/latest_predictions.csv`
- `data/processed/feature_importance.csv`
- `models/opportunity_model.joblib`

---

## Objectives

- Build an end-to-end machine learning pipeline
- Collect and manage financial data
- Design a relational database for financial datasets
- Perform exploratory data analysis
- Engineer predictive financial features
- Train and compare multiple machine learning models
- Evaluate model performance using appropriate statistical metrics
- Backtest top-ranked model picks against the S&P 500 on holdout years
- Interpret predictions using explainable AI techniques
- Build an interactive dashboard for model visualization

---

## Prediction Task

Given all publicly available financial information about a company at time **T**, estimate the probability that the company will outperform the S&P 500 over the next 12 months.

Additional analyses include:

- Predicting expected annual returns
- Comparing sector performance
- Ranking companies by predicted opportunity
- Identifying the financial metrics most strongly associated with future market performance

---

## Technology Stack

### Programming

- Python
- SQL

### Data Engineering

- SQLite
- Pandas
- NumPy

### Machine Learning

- Scikit-Learn
- Logistic Regression
- Random Forest
- Ensemble Classification

### Visualization

- Matplotlib
- Streamlit

### Development

- Git
- GitHub
- Jupyter Notebook

### Planned Extensions

- PostgreSQL for larger datasets and multi-user workflows
- XGBoost model comparison
- SHAP-based global and per-company explanations
- Scheduled retraining and model versioning

---

## Machine Learning Models

The project progressively develops and compares multiple predictive models.

- Linear Regression
- Logistic Regression
- Decision Trees
- Random Forest
- XGBoost
- Ensemble Models

---

## Example Features

Potential predictive variables include:

- Revenue Growth
- Earnings Growth
- Profit Margin
- Operating Margin
- Free Cash Flow
- Debt-to-Equity Ratio
- Current Ratio
- Return on Equity
- Return on Assets
- Price-to-Earnings Ratio
- Price-to-Book Ratio
- Market Capitalization
- R&D Spending
- Employee Growth
- Industry
- Sector

---

## Repository Structure

```
project/
│
├── app/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── docs/
├── models/
├── sql/
├── src/
├── tests/
│
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Makefile
├── README.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## Development Roadmap

### Phase 1

- Project setup
- Financial data collection
- Database design
- Data ingestion pipeline

### Phase 2

- Data cleaning
- Exploratory data analysis
- Feature engineering

### Phase 3

- Baseline models
- Model evaluation
- Hyperparameter tuning

### Phase 4

- Explainability using SHAP
- Ensemble learning
- Model comparison

### Phase 5

- Interactive dashboard
- Documentation
- Deployment

---

## Learning Goals

This project is intended to strengthen knowledge in:

- Statistics
- Machine Learning
- Feature Engineering
- Data Engineering
- SQL
- Model Evaluation
- Explainable AI
- Software Engineering
- Financial Data Analysis

---

## Disclaimer

This project is intended solely for educational and research purposes. It is designed to explore statistical learning and predictive modeling techniques and should not be interpreted as financial or investment advice.
