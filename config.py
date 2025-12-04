import os
import mysql.connector

def conectar():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        print("✔ Conexión exitosa a MySQL")
        return connection
    except Exception as e:
        print("❌ Error al conectar:", e)
        return None
