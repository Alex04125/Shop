import pika, mysql, jsonify, json, os


def order(channel, method, properties, body):
    message = "Order Placed"
    data = json.loads(body.decode("utf-8"))

    if "products" not in data or not data["products"]:
        return (
            jsonify({"error": "Products information is required in the request"}),
            400,
        )

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO orders () VALUES ()")
    mysql.connection.commit()
    order_id = cur.lastrowid

    for product in data["products"]:
        name = product["name"]
        quantity = product["quantity"]
        if not name or not quantity:
            return (
                jsonify(
                    {"error": "Product name and quantity are required for each product"}
                ),
                400,
            )
        cur.execute("SELECT id, price, quantity FROM product WHERE name = %s", (name,))
        product_info = cur.fetchone()
        if product_info:
            product_id, price, product_quantity = product_info
            total_price = price * quantity
            if quantity > product_quantity:
                message = f"{name} out of stock"
                break
            else:
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
                mysql.connection.commit()
        else:
            return jsonify({"error": f"Product {name} not found"}), 400

    order_data = {"order_id": order_id, "status": message}

    channel.basic_publish(
        exchange="",
        routing_key=os.environ.get("MP3_QUEUE"),
        body=json.dumps(order_data),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ),
    )
