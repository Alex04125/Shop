import pika
import sys
import os
import logging
from notify import notification

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    try:
        # RabbitMQ connection
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()

        def callback(ch, method, properties, body):
            try:
                err = notification.notification(body)
                if err:
                    logger.error("Notification processing failed: %s", err)
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                else:
                    logger.info("Notification processed successfully")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception("Exception during notification processing: %s", e)
                ch.basic_nack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=os.environ.get("PURCHASE_QUEUE"), on_message_callback=callback
        )

        logger.info("Waiting for messages. To exit press CTRL+C")

        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    main()
