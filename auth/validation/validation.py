from flask_mysqldb import MySQL
from server import mysql


def username_exists(username, password):
    # Check if the given username exists in the database
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM user WHERE email = %s and password = %s", (username, password)
    )
    user = cur.fetchone()
    cur.close()

    return user is not None


def email_exists(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user is not None
