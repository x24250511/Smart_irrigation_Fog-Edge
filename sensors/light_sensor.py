from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import random

AWS_ENDPOINT = "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "light_sensor_01"
TOPIC = "sensors/light"

mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(AWS_ENDPOINT, 8883)
mqtt_client.configureCredentials(
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/AmazonRootCA1.pem",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-private.pem.key",
    "/Users/tejas/Documents/Fog&Edge/smart-irrigation/certs/03ee31c7039a0cfcccc3fbe837231a2e74e78c13b13b2e32c3c111758c119c14-certificate.pem.crt"
)

mqtt_client.connect()

while True:
    light_value = random.uniform(0, 1000)

    payload = {
        "sensor_id": "light_01",
        "type": "light_intensity",
        "value": round(light_value, 2)
    }

    mqtt_client.publish(TOPIC, json.dumps(payload), 1)
    print("Published:", payload)

    time.sleep(5)
