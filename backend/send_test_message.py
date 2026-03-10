import boto3
import json

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/022966827464/irrigation-queue"

sqs = boto3.client("sqs", region_name="us-east-1")

message = {
    "sensor_id": "field-1",
    "moisture": 32,
    "temperature": 28
}

response = sqs.send_message(
    QueueUrl=QUEUE_URL,
    MessageBody=json.dumps(message)
)

print("Message sent:", response["MessageId"])
