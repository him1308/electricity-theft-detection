# API Reference

Swagger documentation is available at `/docs` when the backend is running.

Authentication uses `POST /api/auth/login` and a bearer token.

Core resources:

- `/api/dashboard/summary`
- `/api/consumers`
- `/api/consumers/{consumer_id}`
- `/api/alerts`
- `/api/data/upload`
- `/api/model/train`
- `/api/predict`
- `/api/predict/batch`
- `/api/model/status`
- `/api/model/metrics`

Admin users can upload data and train models. Analysts can inspect dashboard data, consumers, model status, and alerts.
