# Architecture

The application is split into a FastAPI backend, a React frontend, and a reusable ML package.

## Backend

FastAPI handles authentication, CSV ingestion, model training, prediction, alert management, and dashboard data aggregation. SQLAlchemy models represent users, consumers, readings, alerts, and model metadata.

SQLite is the default database for easy local demos. The `DATABASE_URL` setting can point to PostgreSQL without changing route or service code.

## Frontend

The React app uses Vite, Tailwind CSS, Axios, React Router, Recharts, and Lucide icons. It authenticates against the backend, stores the access token locally for the demo, and renders dashboard metrics from live APIs.

## ML Layer

The ML layer is independent of FastAPI. It receives Pandas data frames, validates and cleans them, engineers consumer-level features, trains a model, persists a Joblib bundle, and returns predictions with explanations.
