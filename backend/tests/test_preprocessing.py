import pandas as pd
import pytest

from ml.preprocessing import clean_dataframe, validate_dataframe


def test_validation_rejects_missing_required_columns():
    result = validate_dataframe(pd.DataFrame({"consumer_id": ["C1"]}))

    assert not result.is_valid
    assert "Missing required columns" in result.errors[0]


def test_clean_dataframe_normalizes_and_drops_bad_rows():
    df = pd.DataFrame(
        {
            "consumer_id": ["C1", "C1", "C2"],
            "timestamp": ["2026-01-01", "bad-date", "2026-01-02"],
            "energy_consumption": ["10.5", "11", "-2"],
        }
    )

    cleaned = clean_dataframe(df)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["energy_consumption"] == 10.5


def test_clean_dataframe_raises_for_invalid_schema():
    with pytest.raises(ValueError):
        clean_dataframe(pd.DataFrame({"timestamp": ["2026-01-01"]}))
