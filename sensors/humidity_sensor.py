import random

# Certificate
CERT_DIR = "/Users/tejas/Documents/FogEdge/smart-irrigation/certs"
CA_PATH = f"{CERT_DIR}/AmazonRootCA1.pem"
KEY_PATH = f"{CERT_DIR}/private.pem.key"
CERT_PATH = f"{CERT_DIR}/certificate.pem.crt"


class HumiditySensor:

    def __init__(self, sensor_id="humidity_01"):
        self.sensor_id = sensor_id

    def read(self, irrigation_state="OFF"):
        """Return humidity reading as a dict payload."""
        if irrigation_state == "ON":
            value = random.uniform(55, 90)  # higher when irrigating
        else:
            value = random.uniform(40, 70)  # lower when dry

        return {
            "sensor_id": self.sensor_id,
            "type":      "humidity",
            "value":     round(value, 2)
        }


# Standalone mode
if __name__ == "__main__":
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    import json
    import time

    CLIENT_ID = "humidity_sensor_01"
    TOPIC = "sensors/humidity"

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(
        "a1oldafst0eivb-ats.iot.us-east-1.amazonaws.com", 8883)
    mqtt_client.configureCredentials(CA_PATH, KEY_PATH, CERT_PATH)
    mqtt_client.connect()
    print("Humidity sensor connected.")

    sensor = HumiditySensor()
    while True:
        payload = sensor.read()
        mqtt_client.publish(TOPIC, json.dumps(payload), 1)
        print("Published:", payload)
        time.sleep(5)
