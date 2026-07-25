from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

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

    response = requests.get(USGS_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
