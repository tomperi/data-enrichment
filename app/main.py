import logging
from flask import Flask, escape, request
from http.client import HTTPException
from osm import count_schools
from geo import validate_coordinates

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

@app.route('/ping')
def hello():
    return "Pong"

@app.route('/api/enrich', methods=["POST"])
def enrich():
    payload = request.json
    errors = []

    for i, item in enumerate(payload.get("data")):
        lat = item.get("Latitude")
        long = item.get("Longitude")
    
        try: 
            if validate_coordinates(lat, long):
                if count := count_schools(lat, long):
                    item["Schools"] = count
                else:
                    logging.error("Unable to get school count")
            else:
                raise ValueError(f"Illegal coordinates ({lat}, {long})")
        except ValueError as e:
            errors.append({"item": i, "error": str(e)})

    if errors:
        payload["Errors"] = errors

    return payload

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5050)

