from flask import Flask, render_template, request, redirect, url_for, jsonify
from config import conectar

app = Flask(__name__)

# ------------------------------
#   PÁGINA PRINCIPAL
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------
#   REGISTRAR USUARIO
# ------------------------------
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    db = conectar()
    cursor = db.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        tarifa = request.form["tarifa"]

        cursor.execute("INSERT INTO usuarios(nombre, tipo_tarifa) VALUES (%s, %s)",
                       (nombre, tarifa))
        db.commit()

    cursor.execute("SELECT id_usuario, nombre, tipo_tarifa FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/eliminar_usuario", methods=["POST"])
def eliminar_usuario():
    id_usuario = request.form["id_usuario"]

    db = conectar()
    cursor = db.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    db.commit()
    cursor.close()
    db.close()

    return redirect("/usuarios")


# ------------------------------
#   REGISTRAR APARATO
# ------------------------------
@app.route("/aparatos", methods=["GET", "POST"])
def aparatos():
    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT id_usuario, nombre FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.execute("""
        SELECT a.id_aparato, a.nombre_aparato, a.potencia_w, a.horas_uso, u.nombre
        FROM aparatos a
        JOIN usuarios u ON a.id_usuario = u.id_usuario
        ORDER BY u.nombre
    """)
    lista_aparatos = cursor.fetchall()

    if request.method == "POST":
        id_usuario = request.form["id_usuario"]
        nombre = request.form["nombre"]
        potencia = request.form["potencia"]
        horas = request.form["horas"]

        cursor.execute("""
            INSERT INTO aparatos(id_usuario, nombre_aparato, potencia_w, horas_uso)
            VALUES (%s, %s, %s, %s)
        """, (id_usuario, nombre, potencia, horas))
        db.commit()

        cursor.close()
        db.close()
        return render_template("aparato_exito.html", nombre=nombre)

    cursor.close()
    db.close()
    return render_template("aparatos.html", usuarios=usuarios, lista_aparatos=lista_aparatos)


@app.route("/eliminar_aparato/<int:id_aparato>", methods=["POST"])
def eliminar_aparato(id_aparato):
    db = conectar()
    cursor = db.cursor()
    cursor.execute("DELETE FROM aparatos WHERE id_aparato = %s", (id_aparato,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})


# ------------------------------
#   CÁLCULO GENERAL
# ------------------------------
@app.route("/calcular", methods=["GET"])
def calcular():
    db = conectar()
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            a.nombre_aparato, 
            a.potencia_w, 
            a.horas_uso, 
            t.precio_kwh,
            u.nombre
        FROM aparatos a
        JOIN usuarios u ON a.id_usuario = u.id_usuario
        JOIN tarifas t ON t.tipo_tarifa = u.tipo_tarifa
    """)
    datos = cursor.fetchall()

    cursor.close()
    db.close()

    if not datos:
        return "No hay datos suficientes para calcular consumo."

    consumo_total = 0
    costo_total = 0

    for aparato in datos:
        nombre, potencia, horas, precio_kwh, usuario = aparato
        consumo = (potencia / 1000) * horas * 30
        costo = consumo * precio_kwh

        consumo_total += consumo
        costo_total += costo

    return render_template(
        "calcular.html",
        datos=datos,
        consumo_total=round(consumo_total, 2),
        costo=round(costo_total, 0)
    )


# ------------------------------
#   CÁLCULO POR USUARIO
# ------------------------------
@app.route("/calcular_usuario", methods=["GET", "POST"])
def calcular_usuario():
    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT id_usuario, nombre FROM usuarios")
    usuarios = cursor.fetchall()

    resultados = None

    if request.method == "POST":
        id_usuario = request.form["id_usuario"]

        cursor.execute("""
            SELECT a.nombre_aparato, a.potencia_w, a.horas_uso, t.precio_kwh
            FROM aparatos a
            JOIN usuarios u ON a.id_usuario = u.id_usuario
            JOIN tarifas t ON t.tipo_tarifa = u.tipo_tarifa
            WHERE a.id_usuario = %s
        """, (id_usuario,))

        aparatos = cursor.fetchall()

        aparatos_resultado = []
        consumo_total_dia = 0
        consumo_total_mes = 0
        costo_total_dia = 0
        costo_total_mes = 0

        labels = []
        valores_kwh_mes = []
        valores_costo_mes = []

        for nombre, potencia, horas, precio_kwh in aparatos:
            consumo_dia = (potencia / 1000) * horas
            consumo_mes = consumo_dia * 30
            costo_dia = consumo_dia * precio_kwh
            costo_mes = consumo_mes * precio_kwh

            consumo_total_dia += consumo_dia
            consumo_total_mes += consumo_mes
            costo_total_dia += costo_dia
            costo_total_mes += costo_mes

            aparatos_resultado.append({
                "nombre": nombre,
                "potencia": potencia,
                "horas": horas,
                "consumo_dia": round(consumo_dia, 3),
                "consumo_mes": round(consumo_mes, 3),
                "costo_dia": round(costo_dia),
                "costo_mes": round(costo_mes)
            })

            labels.append(nombre)
            valores_kwh_mes.append(round(consumo_mes, 3))
            valores_costo_mes.append(round(costo_mes))

        cursor.execute("SELECT nombre FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        nombre_usuario = cursor.fetchone()[0]

        resultados = {
            "usuario": nombre_usuario,
            "aparatos": aparatos_resultado,
            "valor_kwh": precio_kwh,
            "consumo_total_dia": round(consumo_total_dia, 3),
            "consumo_total_mes": round(consumo_total_mes, 3),
            "costo_total_dia": round(costo_total_dia),
            "costo_total_mes": round(costo_total_mes),
            "labels": labels,
            "valores_kwh_mes": valores_kwh_mes,
            "valores_costo_mes": valores_costo_mes
        }

    cursor.close()
    db.close()

    return render_template("calcular_usuario.html", usuarios=usuarios, resultados=resultados)


# ------------------------------
#   REPORTE MENSUAL
# ------------------------------
@app.route("/reporte", methods=["GET", "POST"])
def reporte():
    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT id_usuario, nombre FROM usuarios")
    usuarios = cursor.fetchall()

    datos = None

    if request.method == "POST":
        id_usuario = request.form["id_usuario"]

        cursor.execute("""
            SELECT a.nombre_aparato, a.potencia_w, a.horas_uso, t.precio_kwh
            FROM aparatos a
            JOIN usuarios u ON a.id_usuario = u.id_usuario
            JOIN tarifas t ON t.tipo_tarifa = u.tipo_tarifa
            WHERE a.id_usuario = %s
        """, (id_usuario,))

        aparatos = cursor.fetchall()

        reporte_aparatos = []
        consumo_total = 0
        costo_total = 0

        for nombre, potencia, horas, precio_kwh in aparatos:
            consumo = (potencia / 1000) * horas * 30
            costo = consumo * precio_kwh

            consumo_total += consumo
            costo_total += costo

            reporte_aparatos.append({
                "nombre": nombre,
                "potencia": potencia,
                "horas": horas,
                "consumo": round(consumo, 2),
                "costo": round(costo, 0)
            })

        cursor.execute("SELECT nombre FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        nombre_usuario = cursor.fetchone()[0]

        datos = {
            "usuario": nombre_usuario,
            "aparatos": reporte_aparatos,
            "consumo_total": round(consumo_total, 2),
            "costo_total": round(costo_total, 0)
        }

    cursor.close()
    db.close()

    return render_template("reporte.html", usuarios=usuarios, datos=datos)


# ------------------------------
#   SERVIDOR
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
