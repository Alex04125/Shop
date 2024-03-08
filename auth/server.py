import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from validation import validation

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

server.config["SECRET_KEY"] = "about"


@server.route("/register", methods=["POST"])
def register():
    cur = mysql.connection.cursor()
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    if not email or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if validation.email_exists(email) is False:
        cur.execute(
            "INSERT INTO user (email, password) VALUES (%s, %s)", (email, password)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Registration successful"}), 200
    else:
        return jsonify({"error": "Username already exists"}), 400


@server.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    if validation.username_exists(email, password):
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            },
            server.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return token
    else:
        return "Wrong credentials", 403


@server.route("/validate", methods=["POST"])
def validate():
    token = request.headers["Authorization"]

    token = token.split(" ")[1]

    if not token:
        return "Missing credentials", 401

    try:
        decoded = jwt.decode(token, server.config["SECRET_KEY"], algorithms=["HS256"])
    except:
        return "not authorized", 403

    return decoded, 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)
