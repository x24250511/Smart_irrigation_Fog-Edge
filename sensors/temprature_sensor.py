from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import random

AWS_ENDPOINT = "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "temp_sensor_01"
TOPIC = "sensors/temp"

mqtt_client = AWSIoTMQTTClient(CLIENT_ID)

mqtt_client.configureEndpoint(AWS_ENDPOINT, 8883)
mqtt_client.configureCredentials(
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/AmazonRootCA1.pem",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-private.pem.key",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-certificate.pem.crt"
)

mqtt_client.connect()

while True:
    temp_value = random.uniform(20, 35)

    payload = {
        "sensor_id": "temp_01",
        "type": "temperature",
        "value": round(temp_value, 2)
    }

    mqtt_client.publish(TOPIC, json.dumps(payload), 1)
    print("Published:", payload)

    time.sleep(5)
