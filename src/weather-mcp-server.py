import sys
import json
import requests

def send_response(result, request_id):
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

def send_error(message, request_id, code=-32000):
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message
        }
    }
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

def get_city_coordinates(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    res = requests.get(url).json()

    if "results" not in res or len(res["results"]) == 0:
        return None

    first = res["results"][0]
    return first["latitude"], first["longitude"]

def get_weather_data(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,precipitation_probability"
    )
    return requests.get(url).json()

def handle_get_weather(params, request_id):
    city = params.get("city")

    # Step 1: geocode city
    coords = get_city_coordinates(city)
    if coords is None:
        send_error(f"City '{city}' not found", request_id)
        return

    lat, lon = coords

    # Step 2: get actual weather
    weather = get_weather_data(lat, lon)
    current = weather.get("current", {})

    temp = current.get("temperature_2m")
    rain_prob = current.get("precipitation_probability")

    result = {
        "temperature": temp,
        "rain_probability": rain_prob,
        "description": f"In {city}, the temperature is {temp}°C with a {rain_prob}% chance of rain."
    }

    send_response(result, request_id)

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "get_weather":
            handle_get_weather(params, request_id)
        else:
            send_error(f"Unknown method '{method}'", request_id, code=-32601)

if __name__ == "__main__":
    main()
