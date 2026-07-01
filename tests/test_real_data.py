import pandas as pd

from market_opportunity.real_data import year_end_close


def test_year_end_close_requires_december_observation():
    partial_year = pd.Series(
        [100.0, 110.0],
        index=pd.to_datetime(["2026-01-02", "2026-07-01"]),
    )
    complete_year = pd.Series(
        [100.0, 110.0],
        index=pd.to_datetime(["2025-01-02", "2025-12-31"]),
    )

    assert pd.isna(year_end_close(partial_year, 2026))
    assert year_end_close(complete_year, 2025) == 110.0
