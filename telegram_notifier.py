import asyncio
import json
import logging

import pika
from telegram import Bot

import dynaconfig

RMQ_HOST = dynaconfig.settings["RMQ_HOST"]
RMQ_USER = dynaconfig.settings["RMQ_USER"]
RMQ_PASS = dynaconfig.settings["RMQ_PASS"]
RMQ_QOT = dynaconfig.settings["RMQ_QOT"]

TELEGRAM_BOT_TOKEN = dynaconfig.settings["TELEGRAM_BOT_TOKEN"]
TELEGRAM_BOT_CHAT_ID = dynaconfig.settings["TELEGRAM_BOT_CHAT_ID"]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


async def send_to_telegram(bot: Bot, chat_id: int, text: str):
    """
    Send messages to telegram
    :param bot:
    :param chat_id:
    :param text:
    :return:
    """
    await bot.send_message(
        chat_id=chat_id,
        text=text,
    )


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    credentials = pika.PlainCredentials(
        RMQ_USER,
        RMQ_PASS,
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RMQ_HOST,
            port=5672,
            credentials=credentials,
        )
    )

    channel = connection.channel()

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    logging.info("Waiting for a messages RabbitMQ: %s", RMQ_QOT)

    def callback(ch, method, properties, body):
        try:
            # RabbitMQ -> JSON
            message = json.loads(body.decode("utf-8"))

            text = message["n_text"]
            message_id = message["id"]

            loop.run_until_complete(
                send_to_telegram(
                    bot,
                    TELEGRAM_BOT_CHAT_ID,
                    text,
                )
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logging.info(f"Message with ID: {message_id} sent to Telegram")

        except Exception as e:
            logging.exception("Error occurred while processing a message: %s", e)

            # Return messages to the queue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue=RMQ_QOT, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.warning("Stopping bot because of a Keyboard Interruption")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
