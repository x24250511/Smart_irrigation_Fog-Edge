from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SensorReading
from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboard.html")


@api_view(["POST"])
def receive_from_fog(request):
    data = request.data

    SensorReading.objects.create(
        sensor_id=data["sensor_id"],
        sensor_type=data["type"],
        value=data["value"],
        irrigation_state=data.get("irrigation", "OFF")
    )

    return Response({"status": "stored"})


@api_view(["GET"])
def latest_readings(request):
    readings = SensorReading.objects.order_by("-timestamp")[:20]

    irrigation = None
    if readings:
        irrigation = readings[0].irrigation_state

    return Response({
        "irrigation": irrigation,
        "readings": [
            {
                "type": r.sensor_type,
                "value": r.value,
                "timestamp": r.timestamp
            }
            for r in readings
        ]
    })

    return Response(data)
