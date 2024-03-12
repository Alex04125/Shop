import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from auth_service import access
from product_service import product
from order_service import order
import requests
import pika
import json

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


connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


# AUTH SERVICE
@server.route("/login", methods=["POST"])
def login():
    token = access.login(request)
    if token:
        return token
    else:
        return "Wrong credentials"


@server.route("/register", methods=["POST"])
def register():
    registered = access.register(request)

    if registered:
        return jsonify({"message": "Successfuly registered"})
    else:
        return jsonify({"message": "Unsuccessful"})


##############################################################


# ORDER SERVICE
@server.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()
    try:
        # body_bytes = str(data).encode("utf-8")
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("ORDER_QUEUE"),
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        return "Order placed, expect confirmation."
    except Exception as err:
        print(err)
        return f"Internal server error{err}", 500


@server.route("/order_details/<int:order_id>", methods=["GET"])
def order_details(order_id):
    token = access.validate(request)

    if not token:
        return "Not authorized"

    response, code = order.order_details(request, order_id)

    if code == 200:
        response = response.json()
        return jsonify(response)
    else:
        return "Failed to find order"


# #####################################################################


# PRODUCT SERVICE
@server.route("/products", methods=["GET"])
def get_products():
    token = access.validate(request)

    if not token:
        return "Not authorized"

    products, code = product.get_all_products(request)

    if code == 200:
        products = products.get_json()
        return jsonify(products)
    else:
        return "Failed to get products"


@server.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    token = access.validate(request)

    if not token:
        return "Not authorized"

    products, code = product.get_product(request, product_id)

    if code == 200:
        products = products.get_json()
        return jsonify(products)
    else:
        return "Failed to get product", code


@server.route("/products", methods=["POST"])
def create_product():
    token = access.validate(request)

    if not token:
        return "Not authorized"

    response, code = product.create_product(request)

    if code == 200:
        return response
    else:
        response

    return response


############################################################

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
