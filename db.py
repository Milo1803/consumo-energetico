import os
import mysql.connector

def conectar():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 3306)
        )
        return connection
    except Exception as e:
        print("Error al conectar:", e)
        return None
