from db import conectar

db = conectar()
print("DB:", db)

if db:
    try:
        cursor = db.cursor()
        cursor.execute("SHOW TABLES;")
        print("Tablas:", cursor.fetchall())
    except Exception as e:
        print("Error haciendo consulta:", e)
else:
    print("Error: db es None (falló la conexión)")
