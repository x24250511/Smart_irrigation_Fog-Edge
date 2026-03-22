import random


class SoilMoistureSensor:
    """
    Simulates soil moisture with realistic behaviour.
    Soil level rises when irrigation is ON, drops when OFF.
    """

    def __init__(self, sensor_id="soil_01", initial_level=40.0):
        self.sensor_id = sensor_id
        self.soil_level = initial_level

    def read(self, irrigation_state="OFF"):
        if irrigation_state == "ON":
            self.soil_level += random.uniform(0.8, 1.5)
        else:
            self.soil_level -= random.uniform(0.8, 1.4)

        self.soil_level = max(0, min(100, self.soil_level))

        return {
            "sensor_id": self.sensor_id,
            "type":      "soil_moisture",
            "value":     round(self.soil_level, 2)
        }


class TemperatureSensor:
    """Simulates ambient temperature in Celsius."""

    def __init__(self, sensor_id="temp_01"):
        self.sensor_id = sensor_id

    def read(self, irrigation_state="OFF"):
        # Slight cooling effect when irrigation is ON
        base = 20 if irrigation_state == "ON" else 25
        return {
            "sensor_id": self.sensor_id,
            "type":      "temperature",
            "value":     round(random.uniform(base, base + 10), 2)
        }


class HumiditySensor:
    """Simulates relative humidity percentage."""

    def __init__(self, sensor_id="humidity_01"):
        self.sensor_id = sensor_id

    def read(self, irrigation_state="OFF"):
        # Higher humidity when irrigation is ON
        low = 55 if irrigation_state == "ON" else 40
        high = 90 if irrigation_state == "ON" else 70
        return {
            "sensor_id": self.sensor_id,
            "type":      "humidity",
            "value":     round(random.uniform(low, high), 2)
        }


class LightSensor:
    """Simulates light intensity in lux."""

    def __init__(self, sensor_id="light_01"):
        self.sensor_id = sensor_id

    def read(self, irrigation_state="OFF"):
        return {
            "sensor_id": self.sensor_id,
            "type":      "light_intensity",
            "value":     round(random.uniform(0, 1000), 2)
        }
