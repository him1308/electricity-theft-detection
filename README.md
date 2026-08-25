# Electricity Theft Detection Using Smart Meter Data

An end-to-end full-stack machine learning platform for identifying suspicious smart meter consumption patterns. The system ingests CSV meter data, engineers consumer-level behavior features, trains either anomaly-detection or supervised models, assigns 0-100 risk scores, generates alerts, and exposes the results through a professional energy analytics dashboard.

## Problem Statement

Electricity theft creates major financial losses for power distribution companies. Manual inspections are expensive, slow, difficult to scale, and poor at detecting suspicious behavior early. This project uses smart meter data and machine learning to prioritize consumers for human investigation.

Important: predictions indicate suspicious or anomalous consumption patterns. They do not independently prove electricity theft.

## Features

- FastAPI backend with validated REST APIs and Swagger docs.
- SQLAlchemy data layer with SQLite by default and PostgreSQL-ready configuration.
- CSV upload, schema validation, ingestion, and batch prediction.
- Synthetic demo dataset generator for local development only.
- Feature engineering for consumption, behavior, time-of-day, weekend, voltage/current, and power-factor signals.
- Isolation Forest anomaly detection when labels are unavailable.
- Supervised Random Forest path when labels such as `is_theft`, `theft_label`, `fraud_label`, or `label` exist.
- Logistic Regression baseline for supervised training.
- Persisted Joblib model bundles.
- Risk scoring from 0-100 with Low, Medium, High, and Critical levels.
- Human-readable explanation factors for suspicious consumers.
- JWT-style authentication with Admin and Analyst roles.
- React dashboard with charts, consumers, details, alerts, analytics, model status, and upload pages.
- Docker Compose setup.
- Meaningful ML/data tests.

## Architecture

```text
backend/
  app/
    main.py              FastAPI application
    config.py            Environment configuration
    database.py          SQLAlchemy engine/session setup
    models/              Database models
    schemas/             Pydantic API contracts
    routes/              REST endpoint modules
    services/            Ingestion, reporting, and model orchestration
  ml/
    preprocessing.py     Validation and cleaning
    feature_engineering.py
    train.py
    predict.py
    evaluate.py
    synthetic.py
  tests/
frontend/
  src/
    components/
    pages/
    services/
    hooks/
docs/
```

## Dataset Format

Required columns:

```text
consumer_id,timestamp,energy_consumption
```

Optional supported columns:

```text
voltage,current,power_factor,meter_status,location,meter_number,name,is_theft
```

Extra columns are tolerated. Missing optional columns are handled gracefully.

The app also supports the common wide electricity-theft dataset format where each row is a consumer, daily readings are stored as date columns, and the final columns are:

```text
CONS_NO,FLAG
```

For that format, `CONS_NO` is mapped to `consumer_id`, date columns are converted to consumption readings, and `FLAG` is used as the supervised training label.

## ML Methodology

Pipeline:

```text
Raw smart meter data
Validation
Cleaning
Missing value handling
Feature engineering
Scaling
Model training or loading
Risk scoring
Alert generation
Dashboard/API output
```

The default model is Isolation Forest because electricity theft labels are often unavailable or unreliable. If a reliable binary label column is present, the training path switches to a supervised Random Forest and reports classification metrics.

Feature groups include:

- Consumption statistics: mean, median, standard deviation, min, max, peak/off-peak, total usage.
- Behavioral signals: sudden drops/increases, rolling mean/std, abnormal readings, weekday/weekend, day/night ratio.
- Electrical signals: voltage, current, and power factor summaries when present.

## Risk Scoring

Risk scores are bounded from 0 to 100.

```text
0-30    Low
31-60   Medium
61-80   High
81-100  Critical
```

Scores combine model output and rule-based anomaly indicators. Alerts are generated for High and Critical consumers.

## Running Locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH="."
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

Demo credentials:

```text
admin / admin123
analyst / analyst123
```

## Validation

Run the backend test suite:

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

Run frontend linting and production build checks:

```bash
cd frontend
npm run lint
npm run build
```

## Docker

```bash
docker compose up --build
```

Then open `http://localhost:5173`.

## Key API Endpoints

```text
GET  /api/health
POST /api/auth/login
GET  /api/dashboard/summary
GET  /api/consumers
GET  /api/consumers/{consumer_id}
GET  /api/consumers/{consumer_id}/consumption
GET  /api/alerts
PATCH /api/alerts/{alert_id}/status
POST /api/data/upload
POST /api/model/train
POST /api/predict
POST /api/predict/batch
GET  /api/model/metrics
GET  /api/model/status
```

## Example Prediction Request

```json
{
  "readings": [
    {
      "consumer_id": "C10234",
      "timestamp": "2026-08-18T10:00:00",
      "energy_consumption": 2.4,
      "voltage": 229.3,
      "current": 8.1,
      "power_factor": 0.71
    }
  ]
}
```

## Evaluation Notes

For supervised theft detection, accuracy alone is not enough. This project reports precision, recall, F1, and ROC-AUC when labels are available. Recall matters because missed theft cases are costly, while precision matters because unnecessary inspections waste field resources.

For anomaly detection, the project reports anomaly counts, anomaly percentage, and score distribution statistics instead of pretending to have ground-truth accuracy.

## Data Leakage Prevention

- Scalers are fitted during training and persisted with the model bundle.
- The API never retrains during prediction requests.
- Time-series leakage should be reviewed when using real historical datasets; for production deployment, use chronological validation splits and avoid future readings in earlier predictions.

## Limitations

- Synthetic data is included only for demo and development.
- Isolation Forest flags unusual behavior, not confirmed theft.
- Geographic analysis is limited to uploaded location text.
- The JWT implementation is suitable for a portfolio/local demo; production deployments should use a hardened auth provider or mature JWT library with key rotation.
- Field verification remains required before enforcement action.

## Screenshots

Suggested submission screenshots: dashboard, consumers page, consumer details, alerts page, model page, and upload workflow.
