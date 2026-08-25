import pandas as pd

from ml.train import train_model
from ml.wide_format import engineer_wide_features, is_wide_format, wide_to_long_recent


def test_wide_dataset_supports_cons_no_flag_shape(tmp_path):
    df = pd.DataFrame(
        {
            "1/1/2014": [1.0, 4.0, 0.2, 5.0],
            "1/2/2014": [1.2, 3.8, 0.1, 4.7],
            "1/3/2014": [1.1, 0.3, 0.1, 4.8],
            "1/4/2014": [1.3, 0.2, 0.1, 4.9],
            "1/5/2014": [1.4, 0.1, 0.1, 5.1],
            "1/6/2014": [1.5, 0.1, 0.2, 5.0],
            "1/7/2014": [1.6, 0.1, 0.1, 5.2],
            "CONS_NO": ["C1", "C2", "C3", "C4"],
            "FLAG": [0, 1, 1, 0],
        }
    )

    assert is_wide_format(df)
    features = engineer_wide_features(df)
    recent = wide_to_long_recent(df, days=2)
    metadata = train_model(df, str(tmp_path / "wide.joblib"))

    assert features.shape[0] == 4
    assert len(recent) == 8
    assert metadata["features"] == 22
