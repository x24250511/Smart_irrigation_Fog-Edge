from telemetry.models import SensorReading
import boto3
import json
import os
import time
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_irrigation.settings")
django.setup()


sqs = boto3.client("sqs", region_name="us-east-1")
queue_url = os.environ.get("SQS_QUEUE_URL")

print("SQS Worker started...")

while True:
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

        messages = response.get("Messages", [])

        for message in messages:
            body = json.loads(message["Body"])

            SensorReading.objects.create(
                device_id=body["device_id"],
                moisture=body["moisture"],
                temperature=body["temperature"]
            )

            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"]
            )

            print("Message processed and deleted.")

    except Exception as e:
        print("Error:", str(e))
        time.sleep(5)
