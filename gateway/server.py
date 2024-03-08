import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from auth_service import access
import requests
import pika

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


# connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
# channel = connection.channel()


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


# # ORDER SERVICE
# @server.route("/place_order", methods=["POST"])
# def place_order():
#     data = request.get_json()
#     channel.basic_publish(
#         exchange="",
#         routing_key="video",
#         body=data,
#         properties=pika.BasicProperties(
#             delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
#         ),
#     )
#     return "Order placed, expect confiramtion."


# @server.route("/order_details/<int:order_id>", methods=["GET"])
# def order_details(order_id):
#     token = access.validate(request)

#     if not token:
#         return "Not authorized"

#     response = requests.post()

#     return response


# #####################################################################


# # PRODUCT SERVICE
# @server.route("/products", methods=["GET"])
# def get_all_products():
#     token = access.validate(request)

#     if not token:
#         return "Not authorized"

#     response = requests.post()

#     return response


# @server.route("/products/<int:product_id>", methods=["GET"])
# def get_product(product_id):
#     token = access.validate(request)

#     if not token:
#         return "Not authorized"

#     response = requests.post()

#     return response


# @server.route("/products", methods=["POST"])
# def create_product():
#     token = access.validate(request)

#     if not token:
#         return "Not authorized"

#     response = requests.post()

#     return response


#############################################################

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
