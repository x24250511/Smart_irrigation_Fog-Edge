import boto3
import json
import os
import time
from decimal import Decimal

# Config
REGION = "us-east-1"
QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
DYNAMO_TABLE = os.environ.get("DYNAMO_TABLE", "SensorReadings")

if not QUEUE_URL:
    raise ValueError("SQS_QUEUE_URL environment variable not set")

# AWS clients
sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMO_TABLE)

print(f"SQS Worker started...")
print(f"Queue:  {QUEUE_URL}")
print(f"Table:  {DYNAMO_TABLE}")

while True:
    try:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

        messages = response.get("Messages", [])

        for message in messages:
            body = json.loads(message["Body"])

            table.put_item(Item={
                "sensor_id":  body["sensor_id"],
                "timestamp":  body["timestamp"],
                "type":       body["type"],
                "value":      Decimal(str(body["value"])),
                "irrigation": body["irrigation"]
            })

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"]
            )

            print(
                f"Saved: [{body['type']}] {body['value']} | irrigation: {body['irrigation']} | {body['timestamp']}")

    except Exception as e:
        print("Error:", str(e))
        time.sleep(5)
