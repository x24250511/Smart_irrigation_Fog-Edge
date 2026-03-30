import sys
import os

# Add sensors directory to path — must be before sensor imports
sys.path.insert(0, "/Users/tejas/Documents/FogEdge/smart-irrigation/sensors")

from soil_sensor import SoilMoistureSensor
from temprature_sensor import TemperatureSensor
from humidity_sensor import HumiditySensor
from light_sensor import LightSensor

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
from datetime import datetime

# ── IoT Core config ──────────────────────────────────────────────
AWS_ENDPOINT = "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID    = "fog_node_01"
TOPIC        = "irrigation/telemetry"

# ── Certificate paths ────────────────────────────────────────────
CERT_DIR  = "/Users/tejas/Documents/FogEdge/smart-irrigation/certs"
CA_PATH   = f"{CERT_DIR}/AmazonRootCA1.pem"
KEY_PATH  = f"{CERT_DIR}/private.pem.key"
CERT_PATH = f"{CERT_DIR}/certificate.pem.crt"

# ── Irrigation thresholds ────────────────────────────────────────
LOW_THRESHOLD     = 25
HIGH_THRESHOLD    = 50
DISPATCH_INTERVAL = 5

# ── Initialise sensors ───────────────────────────────────────────
soil_sensor     = SoilMoistureSensor()
temp_sensor     = TemperatureSensor()
humidity_sensor = HumiditySensor()
light_sensor    = LightSensor()

# ── State ────────────────────────────────────────────────────────
irrigation_state = "OFF"


def apply_irrigation_logic(soil_value):
    """Hysteresis-based fog-layer irrigation decision."""
    global irrigation_state
    if irrigation_state == "OFF" and soil_value < LOW_THRESHOLD:
        irrigation_state = "ON"
    elif irrigation_state == "ON" and soil_value > HIGH_THRESHOLD:
        irrigation_state = "OFF"
    return irrigation_state


def connect_mqtt():
    """Connect fog node to AWS IoT Core via MQTT over TLS."""
    client = AWSIoTMQTTClient(CLIENT_ID)
    client.configureEndpoint(AWS_ENDPOINT, 8883)
    client.configureCredentials(CA_PATH, KEY_PATH, CERT_PATH)
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureOfflinePublishQueueing(-1)
    client.configureDrainingFrequency(2)
    client.configureConnectDisconnectTimeout(10)
    client.configureMQTTOperationTimeout(5)
    client.connect()
    print("Fog node connected to AWS IoT Core.")
    return client


# ── Main ─────────────────────────────────────────────────────────
print("Fog node starting...")
mqtt_client = connect_mqtt()

while True:
    try:
        timestamp = datetime.utcnow().isoformat()

        # Read soil first — needed for irrigation decision
        soil_data  = soil_sensor.read(irrigation_state)
        irrigation = apply_irrigation_logic(soil_data["value"])

        # Read all sensors
        readings = [
            soil_data,
            temp_sensor.read(irrigation),
            humidity_sensor.read(irrigation),
            light_sensor.read(irrigation),
        ]

        # Publish each to IoT Core → rule → SQS → DynamoDB
        for reading in readings:
            payload = {
                "sensor_id":  reading["sensor_id"],
                "type":       reading["type"],
                "value":      reading["value"],
                "irrigation": irrigation,
                "timestamp":  timestamp
            }
            mqtt_client.publish(TOPIC, json.dumps(payload), 1)
            print(f"[{payload['type']}] {payload['value']} | Irrigation: {irrigation}")

        time.sleep(DISPATCH_INTERVAL)

    except KeyboardInterrupt:
        print("Fog node stopped.")
        break

    except Exception as e:
        print("Error:", e)
        time.sleep(5)