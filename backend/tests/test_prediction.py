from pathlib import Path

from ml.predict import risk_level
from ml.synthetic import generate_synthetic_readings
from ml.train import train_model
from ml.predict import predict_dataframe


def test_risk_level_boundaries():
    assert risk_level(30) == "Low"
    assert risk_level(60) == "Medium"
    assert risk_level(80) == "High"
    assert risk_level(100) == "Critical"


def test_training_and_prediction_output(tmp_path: Path):
    df = generate_synthetic_readings(consumers=16, days=12)
    model_path = tmp_path / "model.joblib"

    metadata = train_model(df, str(model_path))
    results = predict_dataframe(df, str(model_path))

    assert model_path.exists()
    assert metadata["samples"] == 16
    assert len(results) == 16
    assert all(0 <= item["risk_score"] <= 100 for item in results)
    assert all(item["reasons"] for item in results)
