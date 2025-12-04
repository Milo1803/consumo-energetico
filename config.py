import os
import mysql.connector

def conectar():
    try:
        connection = mysql.connector.connect(
            host="mysql.railway.internal",
            port=3306,
            user="root",
            password="NnKKueYrSzNYFbgZuAZHKWKrdeeHJeox",
            database="railway"
        )
        return connection
    except Exception as e:
        print("Error al conectar:", e)
        return None

