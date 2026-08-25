from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def supervised_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float | None]:
    metrics: dict[str, float | None] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": None,
    }
    if len(set(y_true)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_score))
    return metrics


def anomaly_metrics(scores: np.ndarray, predictions: np.ndarray) -> dict[str, float | None]:
    anomalies = int((predictions == -1).sum())
    total = len(predictions)
    return {
        "accuracy": None,
        "precision": None,
        "recall": None,
        "f1_score": None,
        "roc_auc": None,
        "anomaly_count": anomalies,
        "anomaly_percentage": float(anomalies / total * 100) if total else 0.0,
        "score_mean": float(np.mean(scores)) if total else 0.0,
        "score_std": float(np.std(scores)) if total else 0.0,
    }
