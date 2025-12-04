import mysql.connector

def conectar():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Riascos1803",          # <-- SIN CONTRASEÑA
            database="consumo_energia",
            port=3307             # <-- PUERTO CORRECTO
        )
        return connection
    except Exception as e:
        print("Error al conectar:", e)
        return None
