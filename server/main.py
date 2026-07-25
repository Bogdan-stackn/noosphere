from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Конфигурация
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

@app.route("/")
def root():
    return jsonify({"message": "Noosphere server is running"})

@app.route("/earthquakes")
def get_earthquakes():
    """
    Возвращает все землетрясения за последние 24 часа (магнитудой >= 1.0)
    со всего мира в формате, удобном для отображения на карте.
    """
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

    except requests.RequestException as e:
        return jsonify({"error": f"Не удалось получить данные от USGS: {str(e)}"}), 502

# Оставляем старый эндпоинт для обратной совместимости (сгенерированные события)
@app.route("/events")
def get_random_events():
    # ... (твой старый код, можно не трогать, или тоже оставить)
    pass

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
