import random

# Cert paths — used when running this file standalone
CERT_DIR = "/Users/tejas/Documents/FogEdge/smart-irrigation/certs"
CA_PATH = f"{CERT_DIR}/AmazonRootCA1.pem"
KEY_PATH = f"{CERT_DIR}/private.pem.key"
CERT_PATH = f"{CERT_DIR}/certificate.pem.crt"


class SoilMoistureSensor:

    def __init__(self, sensor_id="soil_01", initial_level=40.0):
        self.sensor_id = sensor_id
        self.soil_level = initial_level

    def read(self, irrigation_state="OFF"):
        """Return soil moisture reading as a dict payload."""
        if irrigation_state == "ON":
            self.soil_level += random.uniform(0.8, 1.2)  # rising when watering
        else:
            self.soil_level -= random.uniform(0.9, 1.4)  # drying when off

        self.soil_level = max(0, min(100, self.soil_level))

        return {
            "sensor_id": self.sensor_id,
            "type":      "soil_moisture",
            "value":     round(self.soil_level, 2)
        }


if __name__ == "__main__":
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    import json
    import time

    CLIENT_ID = "soil_sensor_01"
    PUBLISH_TOPIC = "sensors/soil"

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(
        "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com", 8883)
    mqtt_client.configureCredentials(CA_PATH, KEY_PATH, CERT_PATH)
    mqtt_client.connect()
    print("Soil sensor connected.")

    sensor = SoilMoistureSensor()
    while True:
        payload = sensor.read()
        mqtt_client.publish(PUBLISH_TOPIC, json.dumps(payload), 1)
        print("Published:", payload)
        time.sleep(5)
