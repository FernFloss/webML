import json
import pika
import os
from datetime import datetime, timedelta

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://rabbitmq_user:rabbitmq_pass@localhost:5672/"
)
INPUT_QUEUE = os.getenv("RABBITMQ_INPUT_QUEUE", "frames_ml_in")


def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=INPUT_QUEUE, durable=True)

    cameras = [
        {
            "city": "Москва",
            "building": "ул. Ленина, д. 1",
            "auditorium_id": 1, 
            "auditorium_number": "101",
            "minio_object": "frame_000186.jpg",
        },
        {
            "city": "Питер",
            "building": "ул. Ритина, д. 2",
            "auditorium_id": 2, 
            "auditorium_number": "102",
            "minio_object": "frame_001721.jpg", 
        },
        {
            "city": "Новосиб",
            "building": "ул. Настина, д. 3",
            "auditorium_id": 3, 
            "auditorium_number": "103",
            "minio_object": "frame_002685.jpg",
        },
        {
            "city": "Якутск",
            "building": "ул. Миленина, д. 4",
            "auditorium_id": 4, 
            "auditorium_number": "104",
            "minio_object": "frame_002679.jpg",
        },
    ]

    base_time = datetime(2025, 11, 30, 12, 0, 0)

    for i, cam in enumerate(cameras, start=1):
        ts = (base_time + timedelta(minutes=i)).isoformat() + "Z"

        msg = {
            "city": cam["city"],
            "building": cam["building"],
            "auditorium_id": cam["auditorium_id"],
            "auditorium_number": cam["auditorium_number"],
            "timestamp": ts,
            "minio_bucket": "frames",
            "minio_object": cam["minio_object"],
        }

        body = json.dumps(msg, ensure_ascii=False).encode("utf-8")

        channel.basic_publish(
            exchange="",
            routing_key=INPUT_QUEUE,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2 
            ),
        )

        print(f"sent test message for camera {cam['auditorium_number']}: {msg}")

    connection.close()


if __name__ == "__main__":
    main()
