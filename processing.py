import pika
import dynaconfig
import json

RMQ_HOST = dynaconfig.settings["RMQ_HOST"]
RMQ_USER = dynaconfig.settings["RMQ_USER"]
RMQ_PASS = dynaconfig.settings["RMQ_PASS"]
RMQ_QID = dynaconfig.settings["RMQ_QID"]


def send_to_qid(data):
    """
    Send notification data to RabbitMQ QID queue.
    :param data:
    :return:
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RMQ_HOST,
            port=5672,
            virtual_host="/",
            credentials=pika.PlainCredentials(
                username=RMQ_USER,
                password=RMQ_PASS
            )
        )
    )
    try:
        channel = connection.channel()

        body = json.dumps(data)

        channel.basic_publish(
            exchange="",
            routing_key=RMQ_QID,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json"
            )
        )
    finally:
        connection.close()


if __name__ == '__main__':
    pass
