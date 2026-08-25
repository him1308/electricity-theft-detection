from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.evaluate import anomaly_metrics, supervised_metrics
from ml.feature_engineering import FEATURE_COLUMNS, engineer_features
from ml.preprocessing import clean_dataframe
from ml.wide_format import engineer_wide_features, is_wide_format, labels_from_wide


LABEL_COLUMNS = ["is_theft", "theft_label", "fraud_label", "label"]


def _label_column(df: pd.DataFrame) -> str | None:
    for column in LABEL_COLUMNS:
        if column in df.columns:
            return column
    return None


def train_model(raw_df: pd.DataFrame, model_path: str) -> dict[str, Any]:
    if is_wide_format(raw_df):
        features = engineer_wide_features(raw_df)
        labels = labels_from_wide(raw_df, features)
        label_column = "wide_label" if labels is not None else None
    else:
        cleaned = clean_dataframe(raw_df)
        features = engineer_features(cleaned)
        labels = None
        label_column = _label_column(cleaned)
        if label_column:
            consumer_labels = cleaned.groupby("consumer_id")[label_column].max().reindex(features["consumer_id"]).fillna(0).astype(int)
            labels = consumer_labels.to_numpy()
    model_type = "anomaly"

    if label_column and labels is not None:
        unique_labels, label_counts = np.unique(labels, return_counts=True)
        if len(unique_labels) > 1 and label_counts.min() >= 2 and labels.sum() >= 2:
            model_type = "supervised"

    X = features[FEATURE_COLUMNS].to_numpy()

    if model_type == "supervised" and labels is not None:
        test_size = max(0.25, len(np.unique(labels)) / len(labels))
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=test_size, random_state=42, stratify=labels
        )
        classifier = RandomForestClassifier(
            n_estimators=180,
            class_weight="balanced",
            min_samples_leaf=2,
            random_state=42,
        )
        pipeline = Pipeline([("scaler", StandardScaler()), ("model", classifier)])
        pipeline.fit(X_train, y_train)
        probability = pipeline.predict_proba(X_test)[:, 1]
        y_pred = (probability >= 0.5).astype(int)
        metrics = supervised_metrics(y_test, y_pred, probability)
        baseline = Pipeline([("scaler", StandardScaler()), ("model", LogisticRegression(class_weight="balanced", max_iter=500))])
        baseline.fit(X_train, y_train)
        notes = "Supervised Random Forest trained with Logistic Regression baseline. Recall and precision should be reviewed before field deployment."
    else:
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", IsolationForest(n_estimators=220, contamination="auto", random_state=42)),
            ]
        )
        pipeline.fit(X)
        raw_scores = pipeline.named_steps["model"].score_samples(pipeline.named_steps["scaler"].transform(X))
        predictions = pipeline.named_steps["model"].predict(pipeline.named_steps["scaler"].transform(X))
        metrics = anomaly_metrics(raw_scores, predictions)
        notes = "Isolation Forest anomaly model. Scores flag suspicious consumption patterns and require human verification."

    bundle = {
        "pipeline": pipeline,
        "feature_columns": FEATURE_COLUMNS,
        "model_type": model_type,
        "version": "1.0.0",
        "trained_consumers": features["consumer_id"].tolist(),
    }
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)

    return {
        "model_name": "RandomForestClassifier" if model_type == "supervised" else "IsolationForest",
        "model_type": model_type,
        "version": "1.0.0",
        "samples": int(len(features)),
        "features": int(len(FEATURE_COLUMNS)),
        "metrics": metrics,
        "notes": notes,
    }
