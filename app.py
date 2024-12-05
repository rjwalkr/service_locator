import csv
from flask import Flask, jsonify

app = Flask(__name__)

# Path to the CSV file
SERVICES_CSV_PATH = "services.csv"

# Load services from the CSV file
def load_services():
    services = {}
    try:
        with open(SERVICES_CSV_PATH, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                service_name = row["service_name"]
                services[service_name] = {
                    "host": row["host"],
                    "port": int(row["port"]),
                }
    except FileNotFoundError:
        print(f"Error: CSV file '{SERVICES_CSV_PATH}' not found.")
    return services

# Initialize services
SERVICES = load_services()

@app.route("/service/<service_name>", methods=["GET"])
def get_service(service_name):
    """
    Endpoint to fetch service details by name.
    """
    service = SERVICES.get(service_name)
    if service:
        return jsonify(service)
    return jsonify({"error": "Service not found"}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4000)
