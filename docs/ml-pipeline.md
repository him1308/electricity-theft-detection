# ML Pipeline

## Validation

Input data must include `consumer_id`, `timestamp`, and `energy_consumption`. Optional electrical and metadata fields are used when available.

Wide benchmark datasets are also supported. If the file contains `CONS_NO`, many parseable date columns, and `FLAG`, the pipeline engineers features directly from the wide matrix to avoid expanding very large files into tens of millions of rows during training.

## Feature Engineering

Features are aggregated per consumer. The pipeline captures central tendency, volatility, sudden changes, abnormal readings, peak/off-peak patterns, weekend behavior, day/night ratios, and electrical characteristics.

## Training

If reliable labels exist, the project trains a supervised Random Forest with class balancing and tracks precision, recall, F1, ROC-AUC, and accuracy.

If labels do not exist, the project trains an Isolation Forest anomaly detector and reports anomaly-specific validation statistics.

## Prediction

Prediction uses the persisted preprocessing/model bundle. It never retrains inside request handlers. Outputs contain risk score, risk level, anomaly status, and human-readable reasons.
