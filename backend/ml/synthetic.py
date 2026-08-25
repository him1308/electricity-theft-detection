from __future__ import annotations

from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


def generate_synthetic_readings(consumers: int = 80, days: int = 45, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    rows: list[dict[str, object]] = []
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
    locations = ["North Zone", "South Zone", "Industrial Feeder", "Market Circle", "Residential East"]

    suspicious_ids = set(random.sample(range(consumers), max(6, consumers // 8)))
    for index in range(consumers):
        consumer_id = f"C{10000 + index}"
        location = random.choice(locations)
        baseline = random.uniform(3.2, 14.5)
        is_suspicious = index in suspicious_ids
        drop_day = random.randint(days // 3, max(days // 3 + 1, days - 8))

        for day in range(days):
            for hour in [0, 6, 12, 18]:
                timestamp = start + timedelta(days=day, hours=hour)
                peak_factor = 1.35 if hour == 18 else 0.78 if hour == 0 else 1.0
                weekend_factor = 1.12 if timestamp.weekday() >= 5 else 1.0
                consumption = baseline * peak_factor * weekend_factor + np.random.normal(0, baseline * 0.12)
                if is_suspicious and day >= drop_day:
                    consumption *= random.uniform(0.25, 0.55)
                if is_suspicious and random.random() < 0.04:
                    consumption *= random.uniform(0.05, 0.25)
                rows.append(
                    {
                        "consumer_id": consumer_id,
                        "timestamp": timestamp,
                        "energy_consumption": max(0.05, round(float(consumption), 3)),
                        "voltage": round(random.uniform(210, 242), 2),
                        "current": round(random.uniform(2, 28), 2),
                        "power_factor": round(random.uniform(0.68 if is_suspicious else 0.82, 0.99), 3),
                        "meter_status": "Demo Data",
                        "location": location,
                        "meter_number": f"SM-{index:05d}",
                        "name": f"Consumer {index + 1}",
                        "is_theft": int(is_suspicious),
                    }
                )
    return pd.DataFrame(rows)
