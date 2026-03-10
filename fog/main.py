from fastapi import FastAPI
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3
import json
import statistics
import requests
import threading
import time
from datetime import datetime
from backend.telemetry.models import SensorReading

app = FastAPI()

AWS_ENDPOINT = "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "fog_node_01"


sqs = boto3.client(
    'sqs',
    region_name='eu-west-1',
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET'
)

QUEUE_URL = "YOUR_QUEUE_URL"

sqs = boto3.client('sqs', region_name='eu-west-1')

while True:
    messages = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=10
    )

    for msg in messages.get('Messages', []):
        body = json.loads(msg['Body'])

        # Save to database
        SensorReading.objects.create(...)

        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=msg['ReceiptHandle']
        )


def send_to_queue(payload):
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(payload)
    )


SENSOR_TOPICS = [
    "sensors/soil",
    "sensors/temp",
    "sensors/humidity",
    "sensors/light"
]

CONTROL_TOPIC = "irrigation/control"
BACKEND_URL = "http://127.0.0.1:8000/api/ingest/"

soil_values = []
temp_values = []
light_values = []

irrigation_status = "OFF"
last_published_status = None


def sensor_callback(client, userdata, message):
    global irrigation_status

    data = json.loads(message.payload)
    sensor_type = data.get("type")
    value = data.get("value")

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

    if irrigation_status == "OFF":
        if avg_soil < 25 and (avg_temp > 28 or avg_light > 500):
            irrigation_status = "ON"

    elif irrigation_status == "ON":
        if avg_soil >= 50:
            irrigation_status = "OFF"

    print(
        f"Avg Soil: {avg_soil:.2f} | Avg Temp: {avg_temp:.2f} | Avg Light: {avg_light:.2f}")

    processed_data = {
        "sensor_id": data.get("sensor_id"),
        "type": sensor_type,
        "value": value,
        "irrigation": irrigation_status,
        "timestamp": str(datetime.now())
    }

    print(f"[{datetime.now()}] Processed:", processed_data)

    try:
        send_to_queue(processed_data)
    except:
        print("Backend not reachable")


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
            except:
                print("Control publish failed")
        time.sleep(2)


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

print("Fog node connected and subscribed.")

threading.Thread(target=control_loop, daemon=True).start()


@app.get("/status")
def get_status():
    return {
        "avg_soil": statistics.mean(soil_values) if soil_values else 0,
        "avg_temp": statistics.mean(temp_values) if temp_values else 0,
        "avg_light": statistics.mean(light_values) if light_values else 0,
        "irrigation": irrigation_status
    }
