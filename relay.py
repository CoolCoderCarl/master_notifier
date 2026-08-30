import json
import logging

import redis

import dynaconfig
from processing import QueueManager


class NotificationWorker:
    REDIS_HOST = dynaconfig.settings["REDIS_HOST"]
    REDIS_PORT = dynaconfig.settings["REDIS_PORT"]
    REDIS_PASSWORD = dynaconfig.settings["REDIS_PASSWORD"]

    QUEUE_BY_METHOD = {
        "Telegram": "QOT",
        "Email": "QOM",
    }

    def __init__(self):
        self.redis_client = redis.Redis(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=10,
        )
        self.queue_manager = QueueManager()

    def run(self):
        try:
            while True:
                result = self.redis_client.blpop("notifications", timeout=5)
                # result = self.redis.lrange("notifications", timeout=0)

                if not result:
                    continue

                _, notification_data = result

                try:
                    notification = json.loads(notification_data)
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON: {notification_data}")
                    continue

                n_method = notification.get("n_method")
                queue_name = self.QUEUE_BY_METHOD.get(n_method)

                if not queue_name:
                    logging.error(
                        f"Unknown n_method={n_method}, " f"notification={notification}"
                    )
                    continue

                self.queue_manager.send(queue_name, notification)

                logging.info(
                    f"Notification {notification.get('id')} " f"sent to {queue_name}"
                )

        finally:
            self.queue_manager.close()


if __name__ == "__main__":
    worker = NotificationWorker()
    worker.run()
