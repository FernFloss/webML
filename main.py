import json
import logging
import time

from dotenv import load_dotenv

# Load environment before reading Config so .env values are applied
load_dotenv()

import pika
from config import Config
from minio_client import delete_frame, get_frame_bytes
from detector import count_people_on_frame

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)


def process_message(ch, method, properties, body: bytes):

    try:
        msg = json.loads(body.decode("utf-8"))
        logging.info(f"received message: {msg}")

        camera_id = msg["id_camera"]
        timestamp = msg["timestamp"]
        bucket_raw = msg.get("minio_bucket") or Config.MINIO_DEFAULT_BUCKET
        obj_raw = msg["minio_object"]

        # If minio_bucket is a path (has '/' or ':'), treat it as prefix and keep objects in the default bucket.
        # Otherwise use bucket_raw as is and obj_raw as the key.
        if "/" in bucket_raw or ":" in bucket_raw:
            obj = f"{bucket_raw.strip('/')}/{obj_raw.lstrip('/')}"
            bucket = Config.MINIO_DEFAULT_BUCKET
            logging.warning(
                "minio_bucket '%s' is a path; using bucket '%s' and object '%s'",
                bucket_raw,
                bucket,
                obj,
            )
        else:
            bucket = bucket_raw
            obj = obj_raw

        image_bytes = get_frame_bytes(bucket, obj)

        people_count = count_people_on_frame(image_bytes)
        logging.info(
            f"Processed frame bucket={bucket} object={obj} "
            f"camera_id={camera_id} -> people_count={people_count}"
        )

        camera_event = {
            "id_camera": camera_id,
            "timestamp": timestamp,
            "person_count": people_count,
        }

        ch.basic_publish(
            exchange="",
            routing_key=Config.RABBITMQ_OUTPUT_QUEUE,
            body=json.dumps(camera_event).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2),  # persistent
        )
        logging.info(
            "published camera_event to '%s': %s",
            Config.RABBITMQ_OUTPUT_QUEUE,
            camera_event,
        )

        # Delete processed frame to save storage
        delete_frame(bucket, obj)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logging.exception(f"Error processing message: {e}")

        # Requeue message so it isn't lost (Kafka-like semantics: only drop on success)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():

    params = pika.URLParameters(Config.RABBITMQ_URL)
    connection = None
    for attempt in range(1, 11):
        try:
            connection = pika.BlockingConnection(params)
            break
        except Exception as e:
            logging.warning(f"RabbitMQ connection failed (attempt {attempt}): {e}")
            time.sleep(2 * attempt)

    if connection is None or connection.is_closed:
        logging.error("could not connect to RabbitMQ, exiting")
        return

    channel = connection.channel()

    channel.queue_declare(queue=Config.RABBITMQ_INPUT_QUEUE, durable=True)
    channel.queue_declare(queue=Config.RABBITMQ_OUTPUT_QUEUE, durable=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=Config.RABBITMQ_INPUT_QUEUE,
        on_message_callback=process_message,
    )

    logging.info(
        f"ML service started. "
        f"consuming from '{Config.RABBITMQ_INPUT_QUEUE}', "
        f"publishing to '{Config.RABBITMQ_OUTPUT_QUEUE}'."
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("received KeyboardInterrupt, stopping...")
    finally:
        if connection and not connection.is_closed:
            connection.close()


if __name__ == "__main__":
    main()
