
from flask import Flask, jsonify
import requests
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

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

@app.route("/earthquakes")
def get_earthquakes():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    params = {
        "format": "geojson",
        "starttime": yesterday.isoformat() + "Z",
        "endtime": now.isoformat() + "Z",
        "minmagnitude": 1.0,
        "orderby": "time",
    }

    try:
        response = requests.get(USGS_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return jsonify({"error": f"USGS API error: {str(e)}"}), 502

    events = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [0, 0, 0])

        events.append({
            "id": feature.get("id"),
            "type": "earthquake",
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "time": props.get("time"),
            "latitude": coords[1],
            "longitude": coords[0],
            "depth_km": coords[2],
            "url": props.get("url"),
            "felt": props.get("felt"),
            "alert": props.get("alert"),
        })

    return jsonify({
        "count": len(events),
        "events": events,
        "metadata": {
            "source": "USGS Earthquake Hazards Program",
            "updated": now.isoformat() + "Z"
        }
    })

@app.route("/events")
def get_random_events():
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
