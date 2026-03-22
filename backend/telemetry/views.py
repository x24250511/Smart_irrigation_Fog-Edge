import boto3
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render

REGION = "us-east-1"
DYNAMO_TABLE = os.environ.get("DYNAMO_TABLE", "SensorReadings")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMO_TABLE)


def dashboard(request):
    return render(request, "dashboard.html")


@api_view(["GET"])
def latest_readings(request):
    try:
        # Full scan
        result = table.scan()
        items = result.get("Items", [])

        while "LastEvaluatedKey" in result:
            result = table.scan(ExclusiveStartKey=result["LastEvaluatedKey"])
            items.extend(result.get("Items", []))

        if not items:
            return Response({"irrigation": "OFF", "readings": []})

        # Sort all items by timestamp descending
        items.sort(key=lambda x: x["timestamp"], reverse=True)

        # Get latest reading per sensor_id (ensures all sensors represented)
        seen = {}
        for item in items:
            sid = item["sensor_id"]
            if sid not in seen:
                seen[sid] = item

        latest_per_sensor = list(seen.values())

        # Also get last 20 readings for charts (all sensor types)
        chart_readings = items[:20]

        # Irrigation state from most recent soil reading
        irrigation = "OFF"
        for item in items:
            if item["sensor_id"] == "soil_01":
                irrigation = item["irrigation"]
                break

        readings = [
            {
                "type":      item["type"],
                "value":     float(item["value"]),
                "timestamp": item["timestamp"]
            }
            for item in chart_readings
        ]

        return Response({
            "irrigation": irrigation,
            "readings":   readings,
            "latest":     [
                {
                    "sensor_id": item["sensor_id"],
                    "type":      item["type"],
                    "value":     float(item["value"]),
                    "irrigation": item["irrigation"],
                    "timestamp": item["timestamp"]
                }
                for item in latest_per_sensor
            ]
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
