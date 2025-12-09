import json
import logging
import time
import pika
from config import Config
from minio_client import get_frame_bytes
from detector import count_people_on_frame

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)


def process_message(ch, method, properties, body: bytes):

    try:
        msg = json.loads(body.decode("utf-8"))
        logging.info(f"received message: {msg}")

        city = msg["city"]
        building = msg["building"]
        auditorium_id = msg["auditorium_id"]
        auditorium_number = msg["auditorium_number"]
        timestamp = msg["timestamp"]
        bucket = msg.get("minio_bucket") or Config.MINIO_DEFAULT_BUCKET
        obj = msg["minio_object"]

        image_bytes = get_frame_bytes(bucket, obj)

        people_count = count_people_on_frame(image_bytes)
        logging.info(f"Processed frame {bucket}/{obj} -> people_count={people_count}")

        camera_event = {
            "auditorium_id": auditorium_id, 
            "city": city,
            "building": building,
            "auditorium_number": auditorium_number,
            "timestamp": timestamp,
            "person_count": people_count,
        }

        ch.basic_publish(
            exchange="",
            routing_key=Config.RABBITMQ_OUTPUT_QUEUE,
            body=json.dumps(camera_event).encode("utf-8"),
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logging.exception(f"Error processing message: {e}")

        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


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
