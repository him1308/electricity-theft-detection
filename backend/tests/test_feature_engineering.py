import pandas as pd

from ml.feature_engineering import FEATURE_COLUMNS, engineer_features


def test_engineer_features_returns_consumer_level_rows():
    df = pd.DataFrame(
        [
            {"consumer_id": "C1", "timestamp": "2026-01-01 00:00:00", "energy_consumption": 10, "voltage": 230},
            {"consumer_id": "C1", "timestamp": "2026-01-01 06:00:00", "energy_consumption": 5, "voltage": 231},
            {"consumer_id": "C2", "timestamp": "2026-01-01 00:00:00", "energy_consumption": 20, "voltage": 228},
        ]
    )

    features = engineer_features(df)

    assert set(features["consumer_id"]) == {"C1", "C2"}
    assert all(column in features.columns for column in FEATURE_COLUMNS)
    assert features[FEATURE_COLUMNS].isna().sum().sum() == 0
