import logging

import dynaconfig
import pika
import psycopg2
from datetime import datetime
import json

# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# DB settings
DB_HOST = dynaconfig.settings["DB_HOST"]
DB_USER = dynaconfig.settings["DB_USER"]
DB_PASS = dynaconfig.settings["DB_PASS"]
DB_TABL = dynaconfig.settings["DB_TABL"]

# RMQ settings
RMQ_HOST = dynaconfig.settings["RMQ_HOST"]
RMQ_USER = dynaconfig.settings["RMQ_USER"]
RMQ_PASS = dynaconfig.settings["RMQ_PASS"]
RMQ_QID = dynaconfig.settings["RMQ_QID"]

# RABBITMQ CONNECTION
rabbitmq_connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RMQ_HOST,
        credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    )
)

rabbitmq_channel = rabbitmq_connection.channel()

# POSTGRES CONNECTION
postgres_connection = psycopg2.connect(
    host=DB_HOST,
    port=5432,
    database=DB_TABL,
    user=DB_USER,
    password=DB_PASS
)

postgres_cursor = postgres_connection.cursor()


def callback(ch, method, properties, body):
    # print("Received:", body.decode())
    # ch.basic_ack(delivery_tag=method.delivery_tag)

    try:
        # JSON -> Python dict
        data = json.loads(body.decode())

        logging.info("Received:", data)

        # Get the JSON data
        client_name = data["client_name"]
        n_method = data["n_method"]
        n_text = data["n_text"]
        n_time = data["n_time"]
        priority = data["priority"]
        is_repeat = data["is_repeat"]

        r_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = """
            INSERT INTO notifications
                (client_name, n_method, n_text, n_time, r_time, priority, is_repeat)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        postgres_cursor.execute(
            query,
            (client_name, n_method, n_text, n_time, r_time, priority, is_repeat)
        )

        notification_id = postgres_cursor.fetchone()[0]

        postgres_connection.commit()

        print(f"Notification added, id = {notification_id}")

        # postgres_cursor.close()
        # postgres_connection.close()

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as error:

        logging.error("Error:", error)
        postgres_connection.rollback()
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


rabbitmq_channel.basic_consume(
    queue=RMQ_QID,
    on_message_callback=callback,
    auto_ack=False
)

logging.info("Waiting for messages in QID...")
rabbitmq_channel.start_consuming()












