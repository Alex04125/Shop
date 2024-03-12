import pika
import json
import os
import mysql.connector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_order(channel, method, properties, body, cnx):
    cur = None
    message = "Order placed"
    logger.info(body)
    try:
        order_data = json.loads(body)
        logger.info("Received order data: %s", order_data)

        if "products" not in order_data or not order_data["products"]:
            logger.warning("Products information is required in the request")
            return "Products information is required in the request", 400

        # Insert a new order into the database
        try:
            cur = cnx.cursor()
            cur.execute("INSERT INTO orders () VALUES ()")
            cnx.commit()
            order_id = cur.lastrowid
            logger.info("Order created successfully. Order ID: %s", order_id)
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise

        # Process each product in the order
        for product in order_data["products"]:
            name = product["name"]
            quantity = product["quantity"]

            # Fetch product information from the database
            try:
                cur.execute(
                    "SELECT id, price, quantity FROM product WHERE name = %s", (name,)
                )
                product_info = cur.fetchone()
            except Exception as e:
                logger.error(f"Failed to fetch product information: {e}")
                raise

            if product_info:
                product_id, price, product_quantity = product_info
                total_price = price * quantity

                # Check if the product is in stock
                if quantity > product_quantity:
                    message = f"{name} is out of stock"
                    logger.warning(message)
                    break
                else:
                    # Update product quantity and record order details
                    try:
                        updated_quantity = product_quantity - quantity
                        cur.execute(
                            "UPDATE product SET quantity = %s WHERE id = %s",
                            (updated_quantity, product_id),
                        )
                        cur.execute(
                            """
                            INSERT INTO order_products (order_id, id, quantity, total_price)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (order_id, product_id, quantity, total_price),
                        )
                        cnx.commit()
                        logger.info(
                            "Product %s added to order %s. Quantity: %s, Total Price: %s",
                            name,
                            order_id,
                            quantity,
                            total_price,
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to update product and record order details: {e}"
                        )
                        raise
            else:
                message = f"Product {name} not found"
                logger.warning(message)
                return message, 400

        # Publish a message to RabbitMQ indicating order status
        order_status = {"order_id": order_id, "status": message}
        message_body = json.dumps(order_status)

        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("PURSCHASE_QUEUE"),
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        logger.info("Order processed successfully")

    except Exception as e:
        logger.error(f"Failed to process order: {e}")
        return f"Failed to process order: {e}", 500

    finally:
        try:
            cur.close()
        except Exception as e:
            logger.error(f"Failed to close cursor: {e}")
