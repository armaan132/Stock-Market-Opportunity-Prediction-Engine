from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from market_opportunity.config import SETTINGS  # noqa: E402
from market_opportunity.pipeline import train  # noqa: E402


st.set_page_config(page_title="Market Opportunity Engine", layout="wide")

st.title("Market Opportunity Engine")

source = st.sidebar.selectbox("Data Source", ["real", "csv", "synthetic"])
company_limit = st.sidebar.number_input(
    "S&P 500 Companies",
    min_value=25,
    max_value=503,
    value=120,
    step=25,
    disabled=source != "real",
)
min_year = st.sidebar.number_input("Minimum Fiscal Year", min_value=2000, max_value=2025, value=2014)

if st.sidebar.button("Run Pipeline", type="primary"):
    with st.spinner("Fetching data and training ensemble model with time-based validation..."):
        train(source=source, limit=int(company_limit), min_year=int(min_year))
    st.sidebar.success("Pipeline complete")

if not SETTINGS.predictions_csv.exists():
    st.info("Run the pipeline to generate predictions, metrics, and feature drivers.")
    st.stop()

predictions = pd.read_csv(SETTINGS.predictions_csv)
metrics = pd.read_csv(SETTINGS.metrics_csv)
importance = pd.read_csv(SETTINGS.feature_importance_csv)

top_count = st.sidebar.slider("Companies", 10, 100, 25, step=5)
sector = st.sidebar.selectbox("Sector", ["All"] + sorted(predictions["sector"].unique().tolist()))

filtered = predictions if sector == "All" else predictions[predictions["sector"] == sector]
filtered = filtered.sort_values("opportunity_probability", ascending=False).head(top_count)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies Scored", f"{len(predictions):,}")
col2.metric("ROC AUC", f"{metrics.loc[0, 'roc_auc']:.3f}")
col3.metric("Average Precision", f"{metrics.loc[0, 'average_precision']:.3f}")
col4.metric("Brier Score", f"{metrics.loc[0, 'brier_score']:.3f}")

left, right = st.columns([2, 1])

with left:
    st.subheader("Opportunity Ranking")
    st.dataframe(
        filtered[
            [
                "rank",
                "ticker",
                "company_name",
                "sector",
                "fiscal_year",
                "opportunity_probability",
                "excess_return_next_12m",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )

with right:
    st.subheader("Key Drivers")
    st.bar_chart(importance.head(12).set_index("feature")["importance"])

st.subheader("Probability Distribution")
st.bar_chart(predictions.set_index("ticker")["opportunity_probability"].sort_values(ascending=False).head(50))
