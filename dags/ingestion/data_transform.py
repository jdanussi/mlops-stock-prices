"""Transform module."""

import pandas as pd


def transform(data, symbol):
    """Transform function."""
    df = pd.DataFrame(data).rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    df["symbol"] = symbol
    df = df[["date", "symbol", "open", "high", "low", "close", "adj_close", "volume"]]
    df = df.set_index("date")

    return df
