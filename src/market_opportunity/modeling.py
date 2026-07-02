from __future__ import annotations

from dataclasses import dataclass

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from market_opportunity.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN, feature_columns


@dataclass(frozen=True)
class TrainingResult:
    model: Pipeline
    metrics: pd.DataFrame
    predictions: pd.DataFrame
    backtest: pd.DataFrame
    feature_importance: pd.DataFrame


def time_based_split(data: pd.DataFrame, test_years: int = 2) -> tuple[pd.DataFrame, pd.DataFrame]:
    years = sorted(data["fiscal_year"].unique())
    if len(years) <= test_years:
        raise ValueError("Need more fiscal years than the requested test window.")
    cutoff_year = years[-test_years]
    train = data[data["fiscal_year"] < cutoff_year].copy()
    test = data[data["fiscal_year"] >= cutoff_year].copy()
    return train, test


def build_model(random_state: int = 42) -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    ensemble = VotingClassifier(
        estimators=[
            (
                "logistic",
                LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
            ),
            (
                "random_forest",
                RandomForestClassifier(
                    n_estimators=350,
                    min_samples_leaf=4,
                    class_weight="balanced_subsample",
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ],
        voting="soft",
        weights=[1, 2],
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", ensemble)])


def evaluate_predictions(y_true: pd.Series, probabilities: pd.Series) -> dict[str, float]:
    hard_predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "roc_auc": roc_auc_score(y_true, probabilities),
        "average_precision": average_precision_score(y_true, probabilities),
        "accuracy": accuracy_score(y_true, hard_predictions),
        "brier_score": brier_score_loss(y_true, probabilities),
    }
    return metrics


def train_time_validated_model(data: pd.DataFrame, random_state: int = 42) -> TrainingResult:
    train, test = time_based_split(data)
    model = build_model(random_state=random_state)
    model.fit(train[feature_columns()], train[TARGET_COLUMN])

    probabilities = pd.Series(
        model.predict_proba(test[feature_columns()])[:, 1],
        index=test.index,
        name="opportunity_probability",
    )
    metric_values = evaluate_predictions(test[TARGET_COLUMN], probabilities)
    metrics = pd.DataFrame(
        [{"split": "time_holdout", "train_end_year": int(train["fiscal_year"].max()), **metric_values}]
    )

    holdout_predictions = test[
        [
            "ticker",
            "company_name",
            "sector",
            "fiscal_year",
            "stock_return_next_12m",
            "sp500_return_next_12m",
            "excess_return_next_12m",
        ]
    ].copy()
    holdout_predictions["opportunity_probability"] = probabilities
    backtest = backtest_top_ranked_portfolio(holdout_predictions)

    latest_year = holdout_predictions["fiscal_year"].max()
    predictions = holdout_predictions[holdout_predictions["fiscal_year"] == latest_year].copy()
    predictions["rank"] = predictions["opportunity_probability"].rank(ascending=False, method="first")
    predictions = predictions.sort_values("opportunity_probability", ascending=False)

    importance = extract_feature_importance(model)
    return TrainingResult(
        model=model,
        metrics=metrics,
        predictions=predictions,
        backtest=backtest,
        feature_importance=importance,
    )


def backtest_top_ranked_portfolio(
    holdout_predictions: pd.DataFrame,
    top_n: int = 20,
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for fiscal_year, year_frame in holdout_predictions.groupby("fiscal_year"):
        selected = year_frame.sort_values("opportunity_probability", ascending=False).head(top_n)
        portfolio_return = selected["stock_return_next_12m"].mean()
        benchmark_return = selected["sp500_return_next_12m"].mean()
        rows.append(
            {
                "strategy": f"top_{top_n}_equal_weight",
                "fiscal_year": int(fiscal_year),
                "companies_selected": int(len(selected)),
                "portfolio_return": portfolio_return,
                "sp500_return": benchmark_return,
                "excess_return": portfolio_return - benchmark_return,
                "beat_sp500": bool(portfolio_return > benchmark_return),
            }
        )

    backtest = pd.DataFrame(rows).sort_values("fiscal_year").reset_index(drop=True)
    if backtest.empty:
        return backtest

    summary = {
        "strategy": f"top_{top_n}_equal_weight_summary",
        "fiscal_year": "all_holdout_years",
        "companies_selected": int(backtest["companies_selected"].sum()),
        "portfolio_return": backtest["portfolio_return"].mean(),
        "sp500_return": backtest["sp500_return"].mean(),
        "excess_return": backtest["excess_return"].mean(),
        "beat_sp500": bool(backtest["excess_return"].mean() > 0),
    }
    return pd.concat([backtest, pd.DataFrame([summary])], ignore_index=True)


def extract_feature_importance(model: Pipeline) -> pd.DataFrame:
    preprocessor = model.named_steps["preprocessor"]
    voting_model = model.named_steps["model"]
    transformed_feature_names = preprocessor.get_feature_names_out()
    rf = voting_model.named_estimators_["random_forest"]
    importance = pd.DataFrame(
        {
            "feature": transformed_feature_names,
            "importance": rf.feature_importances_,
        }
    )
    importance["feature"] = importance["feature"].str.replace("numeric__", "", regex=False)
    importance["feature"] = importance["feature"].str.replace("categorical__", "", regex=False)
    return importance.sort_values("importance", ascending=False).reset_index(drop=True)


def save_artifacts(
    result: TrainingResult,
    model_path,
    predictions_path,
    metrics_path,
    backtest_path,
    importance_path,
) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result.model, model_path)
    result.predictions.to_csv(predictions_path, index=False)
    result.metrics.to_csv(metrics_path, index=False)
    result.backtest.to_csv(backtest_path, index=False)
    result.feature_importance.to_csv(importance_path, index=False)


def load_model(model_path):
    return joblib.load(model_path)
