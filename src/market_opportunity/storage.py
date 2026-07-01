from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(database_path)


def save_tables(database_path: Path, financials: pd.DataFrame, prices: pd.DataFrame) -> None:
    with connect(database_path) as conn:
        financials.to_sql("financials", conn, if_exists="replace", index=False)
        prices.to_sql("market_returns", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_financials_ticker_year ON financials(ticker, fiscal_year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_returns_ticker_year ON market_returns(ticker, fiscal_year)")


def load_modeling_frame(database_path: Path) -> pd.DataFrame:
    query = """
        SELECT
            f.*,
            r.sp500_return_next_12m,
            r.stock_return_next_12m,
            r.close_price_year_end
        FROM financials f
        JOIN market_returns r
          ON f.ticker = r.ticker
         AND f.fiscal_year = r.fiscal_year
    """
    with connect(database_path) as conn:
        return pd.read_sql_query(query, conn)
