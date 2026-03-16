import boto3
import json
import time
import random
from datetime import datetime


REGION = "us-east-1"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/022966827464/irrigation-queue"

LOW_THRESHOLD = 25    # Turn ON irrigation
HIGH_THRESHOLD = 50    # Turn OFF irrigation
DISPATCH_INTERVAL = 3  # seconds


# AWS SQS CLIENT

sqs = boto3.client("sqs", region_name=REGION)


# IRRIGATION STATE (HYSTERESIS)

irrigation_state = "OFF"


def apply_irrigation_logic(avg_soil):
    global irrigation_state

    if irrigation_state == "OFF" and avg_soil < LOW_THRESHOLD:
        irrigation_state = "ON"

    elif irrigation_state == "ON" and avg_soil > HIGH_THRESHOLD:
        irrigation_state = "OFF"

    return irrigation_state


def generate_sensor_data():
    soil = round(random.uniform(15, 40), 2)
    temp = round(random.uniform(20, 35), 2)
    humidity = round(random.uniform(40, 80), 2)

    return soil, temp, humidity


def send_to_sqs(payload):
    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(payload)
        )
        print("Sent:", payload)

    except Exception as e:
        print("SQS Error:", e)


# ----------------------------
# MAIN LOOP
# ----------------------------

print("Fog node started...")

while True:
    try:
        soil, temp, humidity = generate_sensor_data()

        irrigation = apply_irrigation_logic(soil)

        timestamp = datetime.utcnow().isoformat()

        # Send each sensor type as separate message
        messages = [
            {
                "sensor_id": "soil_01",
                "type": "soil_moisture",
                "value": soil,
                "irrigation": irrigation,
                "timestamp": timestamp
            },
            {
                "sensor_id": "temp_01",
                "type": "temperature",
                "value": temp,
                "irrigation": irrigation,
                "timestamp": timestamp
            },
            {
                "sensor_id": "humidity_01",
                "type": "humidity",
                "value": humidity,
                "irrigation": irrigation,
                "timestamp": timestamp
            }
        ]

        for message in messages:
            send_to_sqs(message)

        time.sleep(DISPATCH_INTERVAL)

    except KeyboardInterrupt:
        print("Fog node stopped.")
        break

    except Exception as e:
        print("Unexpected Error:", e)
        time.sleep(5)
