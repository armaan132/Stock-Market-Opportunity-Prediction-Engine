# Modeling

The current model estimates the probability that a company will outperform the S&P 500 over the following 12 months.

## Target

```text
outperformed_sp500 = stock_return_next_12m > sp500_return_next_12m
```

The target is binary because the first production-like objective is ranking companies by probability of market outperformance. Expected return regression can be added as a separate task later.

## Features

The model uses features available at fiscal year `T`:

- Revenue growth
- Earnings growth
- Profit margin
- Operating margin
- Free cash flow margin
- Debt-to-equity ratio
- Current ratio
- Return on equity
- Return on assets
- Price-to-earnings ratio
- Price-to-book ratio
- Log market capitalization
- R&D spending as a share of revenue
- Employee growth
- Sector

In real-data mode, these values are derived from SEC Company Facts filings and joined to forward price returns from yfinance.

## Validation

The validation split is time-based:

- Train on earlier fiscal years
- Evaluate on the most recent holdout years
- Exclude partial current-year forward returns

This is more appropriate than a random split for financial forecasting because it reduces the risk of future information leaking into training.

## Model

The current production pipeline is a soft-voting classifier:

- Logistic Regression for a stable linear baseline
- Random Forest for nonlinear interactions and feature importance

Numeric features are median-imputed and scaled. Categorical features are imputed and one-hot encoded. The preprocessing and classifier are saved together as one `scikit-learn` pipeline.

## Metrics

The training command writes:

- ROC AUC
- Average precision
- Accuracy
- Brier score

ROC AUC and average precision evaluate ranking quality. Brier score evaluates probability calibration quality.

## Interpretation

The current dashboard shows Random Forest feature importance from the ensemble. This is a useful first-pass global explanation. A future SHAP integration can add richer global and per-company explanations.
