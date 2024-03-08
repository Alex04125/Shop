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


@server.route("/products", methods=["GET"])
def get_all_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    return jsonify(products)


@server.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id = %s", (product_id,))
    product = cur.fetchone()
    if product:
        return jsonify(product)
    else:
        return jsonify({"error": "Product not found"}), 401


@server.route("/products", methods=["POST"])
def create_product():
    cur = mysql.connection.cursor()
    data = request.get_json()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    quantity = data["quantity"]
    category = data["category"]

    try:
        cur.execute(
            """INSERT INTO product (name, description, price, quantity, category)
            VALUES (%s, %s, %s, %s, %s)""",
            (name, description, price, quantity, category),
        )
        mysql.connection.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        new_product_id = cur.fetchone()[0]

        return jsonify(
            {"message": "Product successfully created", "product_id": new_product_id}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=3000)
