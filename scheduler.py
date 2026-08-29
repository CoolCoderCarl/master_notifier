import json
import logging
import time

import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import dynaconfig

# PostgreSQL
DB_HOST = dynaconfig.settings["DB_HOST"]
DB_TABL = dynaconfig.settings["DB_TABL"]
DB_USER = dynaconfig.settings["DB_USER"]
DB_PASS = dynaconfig.settings["DB_PASS"]

# Redis
REDIS_HOST = dynaconfig.settings["REDIS_HOST"]
REDIS_PORT = dynaconfig.settings["REDIS_PORT"]
REDIS_PASSWORD = dynaconfig.settings["REDIS_PASSWORD"]


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=5432,
        database=DB_TABL,
        user=DB_USER,
        password=DB_PASS,
    )


def get_redis_connection():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        # db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )


def get_ready_messages(connection):
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            """
SELECT
    id,
    client_name,
    n_method,
    n_text,
    n_time,
    priority
FROM notifications
WHERE n_time >= NOW()
ORDER BY priority DESC, n_time ASC;
"""
        )
        return cursor.fetchall()


def delete_message(connection, message_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
DELETE FROM notifications
WHERE id = %s
""",
            (message_id,),
        )

    connection.commit()


def send_to_redis(redis_client, message, id):
    """
    Send to redis
    :param redis_client:
    :param message:
    :param id: Message ID from DB
    :return:
    """
    data = json.dumps(
        dict(message),
        ensure_ascii=False,
        default=str,
    )
    logging.info(f"Sending message with ID {id}")
    redis_client.rpush("notifications", data)


def main():
    pg_connection = get_db_connection()
    redis_client = get_redis_connection()

    try:
        while True:
            messages = get_ready_messages(pg_connection)

            logging.info(f"Founded messages: {len(messages)}")

            for message in messages:
                try:
                    send_to_redis(redis_client, message, message["id"])

                    # Delete if Redis receive message
                    # delete_message(
                    #     pg_connection,
                    #     message["id"],
                    # )
                    # logging.info(f"Message {message['id']} "f"sent to Redis and deleted")

                except Exception as error:
                    logging.error(f"An error occurred {message['id']}: {error}")

            # Wait for 1 minute
            logging.info("Waiting for 1 minute...")
            time.sleep(60)

    finally:
        pg_connection.close()


if __name__ == "__main__":
    main()
