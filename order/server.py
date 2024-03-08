import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

if server.debug:
    # Debug-specific configuration (you can modify this as needed)
    server.config["MYSQL_HOST"] = "localhost"
    server.config["MYSQL_USER"] = "auth_user"
    server.config["MYSQL_PASSWORD"] = "1234"
    server.config["MYSQL_DB"] = "auth"
    server.config["MYSQL_PORT"] = 3306
else:
    # Production or other configuration
    server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
    server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
    server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
    server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
    server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


@server.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()

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
                return jsonify({"error": "Insuficient quanity"})
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

    return jsonify({"message": "Order placed successfuly", "order_id": order_id}), 200


@server.route("/order_details/<int:order_id>", methods=["GET"])
def order_details(order_id):
    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT order_id, order_date from orders where order_id = %s", (order_id,)
    )
    order_info = cur.fetchone()

    if order_info:
        order_id, order_date = order_info
        cur.execute(
            """SELECT op.id, p.name, op.quantity, op.total_price from order_products op
              inner join product p on op.id = p.id 
              where op.order_id =%s """,
            (order_id,),
        )
        products_info = cur.fetchall()

        order_details = {
            "order_id": order_id,
            "order_date": order_date,
            "products": [],
        }

        for product in products_info:
            product_id, product_name, quantity, total_price = product
            product_details = {
                "product_id": product_id,
                "product_name": product_name,
                "quantity": quantity,
                "total_price": total_price,
            }
            order_details["products"].append(product_details)
        cur.close()
        return jsonify(order_details), 200
    else:
        cur.close()
        return jsonify({"error": f"Order with ID {order_id} not found"}), 404


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
