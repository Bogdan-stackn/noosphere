from flask import Flask, jsonify
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)

CITIES = [
    {"name": "Москва", "lat": 55.75, "lon": 37.62},
    {"name": "Токио", "lat": 35.68, "lon": 139.76},
    {"name": "Нью-Йорк", "lat": 40.71, "lon": -74.00},
    {"name": "Сидней", "lat": -33.86, "lon": 151.20},
    {"name": "Сан-Паулу", "lat": -23.55, "lon": -46.63},
]

@app.route("/")
def root():
    return jsonify({"message": "Noosphere server is running"})

@app.route("/events")
def get_events():
    events = []
    now = datetime.utcnow()
    for _ in range(random.randint(3, 7)):
        city = random.choice(CITIES)
        lat = city["lat"] + random.uniform(-2, 2)
        lon = city["lon"] + random.uniform(-2, 2)
        event_type = random.choice(["earthquake", "lightning", "fire"])
        magnitude = round(random.uniform(1.0, 6.5), 1) if event_type == "earthquake" else None
        events.append({
            "id": random.randint(10000, 99999),
            "type": event_type,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "magnitude": magnitude,
            "city": city["name"],
            "time": (now - timedelta(minutes=random.randint(0, 120))).isoformat() + "Z"
        })
    return jsonify({"events": events})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
