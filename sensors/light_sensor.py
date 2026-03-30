import random

# Certificate paths for AWS IoT connection
CERT_DIR = "/Users/tejas/Documents/FogEdge/smart-irrigation/certs"
CA_PATH = f"{CERT_DIR}/AmazonRootCA1.pem"
KEY_PATH = f"{CERT_DIR}/private.pem.key"
CERT_PATH = f"{CERT_DIR}/certificate.pem.crt"


class LightSensor:

    def __init__(self, sensor_id="light_01", min_lux=0, max_lux=1000):
        self.sensor_id = sensor_id
        self.min_lux = min_lux
        self.max_lux = max_lux

    def read(self, irrigation_state="OFF"):
        """Return light intensity reading as a dict payload."""
        return {
            "sensor_id": self.sensor_id,
            "type":      "light_intensity",
            "value":     round(random.uniform(self.min_lux, self.max_lux), 2)
        }


# Standalone mode
if __name__ == "__main__":
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    import json
    import time

    CLIENT_ID = "light_sensor_01"
    TOPIC = "sensors/light"

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(
        "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com", 8883)
    mqtt_client.configureCredentials(CA_PATH, KEY_PATH, CERT_PATH)
    mqtt_client.connect()
    print("Light sensor connected.")

    sensor = LightSensor()
    while True:
        payload = sensor.read()
        mqtt_client.publish(TOPIC, json.dumps(payload), 1)
        print("Published:", payload)
        time.sleep(5)
