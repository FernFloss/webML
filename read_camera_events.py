import json
import pika

RABBITMQ_URL = "amqp://rabbitmq_user:rabbitmq_pass@localhost:5672/"
OUTPUT_QUEUE = "camera_events"

def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=OUTPUT_QUEUE, durable=True)

    while True:
        method, properties, body = channel.basic_get(
            queue=OUTPUT_QUEUE,
            auto_ack=True
        )
        if method is None:
            print("сообщений больше нет")
            break

        msg = json.loads(body.decode("utf-8"))
        print(json.dumps(msg, ensure_ascii=False, indent=2))
        print(
            f"auditorium_number={msg.get('auditorium_number')}, "
            f"timestamp={msg.get('timestamp')}, "
            f"person_count={msg.get('person_count')}"
        )
        print("-" * 40)

    connection.close()

if __name__ == "__main__":
    main()