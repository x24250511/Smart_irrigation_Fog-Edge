from fastapi import FastAPI
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import statistics
import requests
import threading
import time
from datetime import datetime

app = FastAPI()


AWS_ENDPOINT = "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "fog_node_01"
LOW_THRESHOLD = 20
HIGH_THRESHOLD = 30
SENSOR_TOPICS = [
    "sensors/soil",
    "sensors/temp",
    "sensors/humidity",
    "sensors/light"
]


CONTROL_TOPIC = "irrigation/control"

BACKEND_URL = "http://irrigation-env.eba-ejg4mp8y.us-east-1.elasticbeanstalk.com/ingest/"

soil_values = []
temp_values = []
light_values = []

LOW_THRESHOLD = 25
HIGH_THRESHOLD = 50

irrigation_status = "OFF"
last_published_status = None


def sensor_callback(client, userdata, message):
    global irrigation_status

    try:
        data = json.loads(message.payload)
        sensor_type = data.get("type")
        value = float(data.get("value"))

    except Exception as e:
        print("Invalid payload:", e)
        return

    if sensor_type == "soil_moisture":
        soil_values.append(value)
        soil_values[:] = soil_values[-5:]

    elif sensor_type == "temperature":
        temp_values.append(value)
        temp_values[:] = temp_values[-5:]

    elif sensor_type == "light_intensity":
        light_values.append(value)
        light_values[:] = light_values[-5:]

    avg_soil = statistics.mean(soil_values) if soil_values else 0
    avg_temp = statistics.mean(temp_values) if temp_values else 0
    avg_light = statistics.mean(light_values) if light_values else 0

    # Smart irrigation logic
    if irrigation_status == "OFF" and avg_soil < LOW_THRESHOLD:
        irrigation_status = "ON"

    elif irrigation_status == "ON" and avg_soil > HIGH_THRESHOLD:
        irrigation_status = "OFF"
    processed_payload = {
        "sensor_id": data.get("sensor_id"),
        "type": sensor_type,
        "value": value,
        "avg_soil": round(avg_soil, 2),
        "avg_temp": round(avg_temp, 2),
        "avg_light": round(avg_light, 2),
        "irrigation": irrigation_status,
        "timestamp": str(datetime.utcnow())
    }

    print("Processed:", processed_payload)

    try:
        response = requests.post(
            BACKEND_URL, json=processed_payload, timeout=5)
        print("Backend Response:", response.status_code)
    except Exception as e:
        print("Backend not reachable:", e)


# ================= CONTROL LOOP ================= #

def control_loop():
    global last_published_status

    while True:
        if irrigation_status != last_published_status:
            try:
                mqtt_client.publish(
                    CONTROL_TOPIC,
                    json.dumps({"status": irrigation_status}),
                    1
                )
                print("Control Published:", irrigation_status)
                last_published_status = irrigation_status
            except Exception as e:
                print("Control publish failed:", e)

        time.sleep(2)


# ================= MQTT SETUP ================= #

mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(AWS_ENDPOINT, 8883)
mqtt_client.configureCredentials(
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/AmazonRootCA1.pem",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-private.pem.key",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-certificate.pem.crt"
)

mqtt_client.connect()

for topic in SENSOR_TOPICS:
    mqtt_client.subscribe(topic, 1, sensor_callback)

print("Fog node connected and subscribed to sensors.")

# Start control thread
threading.Thread(target=control_loop, daemon=True).start()
# Keep main thread alive
while True:
    time.sleep(10)


# ================= STATUS ENDPOINT ================= #

@app.get("/status")
def get_status():
    return {
        "avg_soil": statistics.mean(soil_values) if soil_values else 0,
        "avg_temp": statistics.mean(temp_values) if temp_values else 0,
        "avg_light": statistics.mean(light_values) if light_values else 0,
        "irrigation": irrigation_status
    }
