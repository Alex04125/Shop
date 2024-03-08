import pika, os, sys
from place import update_order


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", heartbeat=60)
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = update_order.order(ch, method, properties, body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()
