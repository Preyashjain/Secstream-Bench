"""Produce and consume a small broker health-check batch."""

import json
import os
import time

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic


BOOTSTRAP = os.getenv("BOOTSTRAP_SERVERS", "localhost:19092")
TOPIC = "secstream.broker-check"
COUNT = 1000


def main() -> None:
    admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
    try:
        admin.create_topics([NewTopic(TOPIC, num_partitions=1, replication_factor=1)])[TOPIC].result()
    except Exception as exc:
        if "ALREADY_EXISTS" not in str(exc):
            raise

    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    for number in range(COUNT):
        producer.produce(TOPIC, key=str(number), value=json.dumps({"number": number}))
        producer.poll(0)
    producer.flush()

    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": f"secstream-check-{time.time_ns()}",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([TOPIC])
    received = 0
    deadline = time.monotonic() + 30
    try:
        while received < COUNT and time.monotonic() < deadline:
            messages = consumer.consume(num_messages=100, timeout=1)
            for message in messages:
                if message.error() is not None:
                    raise RuntimeError(message.error())
                received += 1
    finally:
        consumer.close()

    if received != COUNT:
        raise RuntimeError(f"broker check received {received}/{COUNT} messages")
    print(f"PASS: produced and consumed {received} messages")


if __name__ == "__main__":
    main()