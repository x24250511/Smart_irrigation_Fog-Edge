import random

# Certificate paths for AWS IoT connection
CERT_DIR = "/Users/tejas/Documents/FogEdge/smart-irrigation/certs"
CA_PATH = f"{CERT_DIR}/AmazonRootCA1.pem"
KEY_PATH = f"{CERT_DIR}/private.pem.key"
CERT_PATH = f"{CERT_DIR}/certificate.pem.crt"


class TemperatureSensor:
    def __init__(self, sensor_id="temp_01"):
        self.sensor_id = sensor_id

    def read(self, irrigation_state="OFF"):
        """Return temperature reading as a dict payload."""
        if irrigation_state == "ON":
            value = random.uniform(20, 28)  # cooler when watering
        else:
            value = random.uniform(25, 35)  # warmer when dry

        return {
            "sensor_id": self.sensor_id,
            "type":      "temperature",
            "value":     round(value, 2)
        }


# Standalone mode
if __name__ == "__main__":
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    import json
    import time

    CLIENT_ID = "temp_sensor_01"
    TOPIC = "sensors/temp"

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(
        "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com", 8883)
    mqtt_client.configureCredentials(CA_PATH, KEY_PATH, CERT_PATH)
    mqtt_client.connect()
    print("Temperature sensor connected.")

    sensor = TemperatureSensor()
    while True:
        payload = sensor.read()
        mqtt_client.publish(TOPIC, json.dumps(payload), 1)
        print("Published:", payload)
        time.sleep(5)
