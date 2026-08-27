import json
import time
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import dynaconfig


class QueueManager:
    def __init__(self):
        self.host = dynaconfig.settings["RMQ_HOST"]
        self.user = dynaconfig.settings["RMQ_USER"]
        self.password = dynaconfig.settings["RMQ_PASS"]

        self.queues = {
            "QID": dynaconfig.settings["RMQ_QID"],
            "QOT": dynaconfig.settings["RMQ_QOT"],
            "QOM": dynaconfig.settings["RMQ_QOM"],
        }

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=5672,
                virtual_host="/",
                credentials=pika.PlainCredentials(
                    username=self.user,
                    password=self.password,
                ),
                heartbeat=60,
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=2,
            )
        )

        self.channel = self.connection.channel()

    def send(self, queue_name, data):
        queue = self.queues.get(queue_name)

        if not queue:
            raise ValueError(f"Unknown queue: {queue_name}")

        self.channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json",
            ),
        )

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
