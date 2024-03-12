import pika
import os
import sys
import logging
from place import update_order
import mysql.connector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.environ.get("RABBITMQ_HOST", "rabbitmq"))
        )
        channel = connection.channel()
        cnx = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST"),
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DB"),
            port=os.environ.get("MYSQL_PORT"),
        )

        def callback(ch, method, properties, body):
            try:
                err = update_order.process_order(ch, method, properties, body, cnx)
                if err:
                    logger.error(f"Order processing failed: {err}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                else:
                    logger.info("Order processed successfully")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(f"Exception during order processing: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(
            queue=os.environ.get("ORDER_QUEUE"), on_message_callback=callback
        )

        logger.info("Waiting for messages. To exit press CTRL+C")

        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)


if __name__ == "__main__":
    main()
