from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import random

AWS_ENDPOINT = "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "soil_sensor_01"

PUBLISH_TOPIC = "sensors/soil"
CONTROL_TOPIC = "irrigation/control"

soil_level = 40
irrigation_status = "OFF"


def control_callback(client, userdata, message):
    global irrigation_status
    payload = json.loads(message.payload)
    irrigation_status = payload.get("status", "OFF")
    print("Irrigation Status Updated:", irrigation_status)


mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(AWS_ENDPOINT, 8883)
mqtt_client.configureCredentials(
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/AmazonRootCA1.pem",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-private.pem.key",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-certificate.pem.crt"
)

mqtt_client.connect()
mqtt_client.subscribe(CONTROL_TOPIC, 1, control_callback)

while True:
    if irrigation_status  "ON":
        # 🌱 Slow watering
        soil_level += random.uniform(0.8, 1.2)
    else:
        # 🌞 Slow drying
        soil_level -= random.uniform(1.4, 0.9)

    soil_level = max(0, min(100, soil_level))

    payload = {
        "sensor_id": "soil_01",
        "type": "soil_moisture",
        "value": round(soil_level, 2)
    }

    mqtt_client.publish(PUBLISH_TOPIC, json.dumps(payload), 1)
    print("Published:", payload)

    time.sleep(5)
