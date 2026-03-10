from django.db import models


class SensorReading(models.Model):
    sensor_id = models.CharField(max_length=50)
    sensor_type = models.CharField(max_length=50)
    value = models.FloatField()
    irrigation_state = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor_type} - {self.value}"
