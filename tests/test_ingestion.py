"""Unit Test ingestion."""

import json
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dags.ingestion.data_transform import transform

CURRENT_DIR = Path(__file__).resolve().parent


@pytest.fixture
def api_json():
    """Raw data as is it received from Yahoo! Finance's API"""

    # Opening JSON file
    with open(f"{CURRENT_DIR}/test.json", "r", encoding="utf8") as openfile:

        # Reading from json file
        stocks = json.load(openfile)

    return stocks


def test_data_transform(api_json):  # pylint: disable=redefined-outer-name
    """Test transform data."""

    df_expected = pd.DataFrame(
        [
            [
                "2024-01-02",
                "goog",
                139.6000061035,
                140.6150054932,
                137.7400054932,
                139.5599975586,
                139.4013671875,
                20071900,
            ]
        ],
        columns=[
            "date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
        ],
    ).set_index("date")

    df_actual = transform(api_json, "goog")
    assert_frame_equal(df_actual, df_expected)
