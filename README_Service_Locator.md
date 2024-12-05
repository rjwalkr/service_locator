
# Service Locator for Local Network Services

## **1. Problem Statement**

When developing Python applications that rely on local network services, hardcoding server hostnames or IP addresses becomes problematic. 
If a server's hostname or IP address changes, all clients using those services need to be updated, leading to maintenance headaches. 

### Key Challenges:
- **Dependency on Hardcoded Addresses**: Applications are tied to specific hostnames/IPs.
- **Fragile Client Code**: Changes to the service's location (e.g., moving from `pi5` to `pi7`) require modifying all dependent client code.
- **Scaling Issues**: Adding new services or moving existing ones becomes complex and error-prone.

### Objective:
To abstract the service location so that:
1. Clients request a **service by name** (e.g., `auth_devs`) without embedding server identity (hostname/IP).
2. The system dynamically resolves the service's address (hostname and port) at runtime.

---

## **2. Solution Overview**

We propose a **Service Locator** system that acts as an intermediary between clients and services. 

### Key Features:
1. **Service Name Abstraction**: Clients request services by name.
2. **Dynamic Resolution**: The service locator provides the hostname and port for requested services.
3. **Centralized Configuration**: Services are defined in a single place (`services.csv`), avoiding duplication.

### Workflow:
1. The **Service Locator** runs as a Flask application on the loopback address (`127.0.0.1`) of each client machine.
2. A **CSV file** stores the mapping of service names to their hostnames and ports.
3. Clients query the Service Locator to resolve service locations dynamically:
   ```python
   connection = ns.location("auth_devs")
   ```
4. The client uses the resolved hostname and port to connect to the service.

---

## **3. Reasoning Behind the Approach**

### Why Use a Loopback Service Locator?
- **Always Available**: The loopback address (`127.0.0.1`) is constant and accessible.
- **Dynamic Updates**: The locator provides flexibility to change service locations without altering client code.
- **Low Overhead**: Running a lightweight Flask app on `127.0.0.1` avoids the need for external dependencies or infrastructure.

### Why Use a CSV File for Configuration?
- **Simple and Human-Readable**: Easy to edit, backup, and manage.
- **Dynamic Management**: Services can be updated dynamically by reloading the CSV file at runtime.
- **Lightweight**: No need for a full database during initial implementation.

---

## **4. Implementation Details**

### Directory Structure
The project will reside under `~/core/service_locator` with the following structure:
```
~/core/service_locator/
│
├── app.py             # Main Flask application
├── services.csv       # CSV file for service definitions
├── venv/              # Virtual environment
├── logs/              # Logs (optional, for debugging)
└── README.md          # Documentation
```

### CSV File Format
The `services.csv` file defines the services:
```csv
service_name,host,port
auth_devs,pi7.local,5001
network_scan,pi7.local,5002
kasa_project,pi7.local,5003
```

### Flask Application (`app.py`)
The Service Locator is implemented as a Flask app:
```python
import csv
from flask import Flask, jsonify

app = Flask(__name__)

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

SERVICES = load_services()

@app.route("/service/<service_name>", methods=["GET"])
def get_service(service_name):
    service = SERVICES.get(service_name)
    if service:
        return jsonify(service)
    return jsonify({"error": "Service not found"}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4000)
```

### Client API
A reusable library simplifies client integration:
```python
import requests

class ServiceLocator:
    def __init__(self, base_url="http://127.0.0.1:4000"):
        self.base_url = base_url

    def location(self, service_name):
        response = requests.get(f"{self.base_url}/service/{service_name}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise Exception(f"Service '{service_name}' not found")
        else:
            response.raise_for_status()

# Singleton-style usage
ns = ServiceLocator()

# Example Usage
try:
    connection = ns.location("auth_devs")
    print(f"auth_devs is at {connection['host']}:{connection['port']}")
except Exception as e:
    print(f"Error: {e}")
```

---

## **5. Future Enhancements**

### Ideas to Explore After MVP:
1. **Dynamic Reloading**:
   - Add an endpoint (`/reload_services`) to reload the CSV without restarting the locator.
2. **Broadcast Discovery**:
   - Allow clients to send a broadcast query instead of relying on `127.0.0.1`.
3. **Service Registration**:
   - Enable services to register themselves dynamically with the locator.
4. **Caching**:
   - Cache resolved services for faster lookups.
5. **Distributed Locator**:
   - Use a central service discovery mechanism (e.g., Consul or etcd) for larger networks.

---

## **6. Steps to Get Started**

### On `pi7`:
1. Create the project directory:
   ```bash
   mkdir -p ~/core/service_locator
   cd ~/core/service_locator
   ```
2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask
   ```
3. Add the `app.py` and `services.csv` files.
4. Run the Flask app:
   ```bash
   python app.py
   ```

### On Client Machines:
1. Copy the client library (`ServiceLocator` class).
2. Query the service locator at `127.0.0.1` for service information.

---

## **7. Immediate Focus**
1. Build and test the Service Locator on `pi7`.
2. Write test cases for service resolution.
3. Deploy the runtime code to another machine for validation.
4. Refine based on feedback and expand functionality incrementally.
