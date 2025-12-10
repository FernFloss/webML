import json
import os
from datetime import datetime, timedelta

import pika

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://rabbitmq_user:rabbitmq_pass@localhost:5672/"
)
INPUT_QUEUE = os.getenv("RABBITMQ_INPUT_QUEUE", "rabbit_queue")


def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=INPUT_QUEUE, durable=True)

    cameras = [
        {
            "id_camera": "AA:BB:CC:DD:EE:01",
            "minio_bucket": "frames/AA:BB:CC:DD:EE:01/2025-02-01/frames",
            "minio_object": "frame_000186.jpg",
        },
        {
            "id_camera": "AA:BB:CC:DD:EE:02",
            "minio_bucket": "frames/AA:BB:CC:DD:EE:02/2025-02-01/frames",
            "minio_object": "frame_001721.jpg",
        },
    ]

    base_time = datetime(2025, 2, 1, 12, 0, 0)

    for i, cam in enumerate(cameras, start=0):
        ts = (base_time + timedelta(minutes=i)).isoformat() + "Z"

        msg = {
            "id_camera": cam["id_camera"],
            "timestamp": ts,
            "minio_bucket": cam["minio_bucket"],
            "minio_object": cam["minio_object"],
        }

        body = json.dumps(msg, ensure_ascii=False).encode("utf-8")

        channel.basic_publish(
            exchange="",
            routing_key=INPUT_QUEUE,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent
            ),
        )

        print(f"sent test message for camera {cam['id_camera']}: {msg}")

    connection.close()


if __name__ == "__main__":
    main()
