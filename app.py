import os
from dotenv import load_dotenv
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session

# 1. Cargar las variables del archivo .env a la memoria del sistema
load_dotenv()

app = Flask(__name__)
# Leemos la clave de cifrado de cookies desde el .env
app.secret_key = os.getenv("SECRET_KEY", "clave_por_defecto_daw")

# 2. Función de conexión a PostgreSQL usando variables de entorno
def get_conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        accion = request.form.get("accion")
        usuario = request.form.get("usuario")
        password = request.form.get("password")
        confirmar_password = request.form.get("confirmar_password")

        conexion = get_conexion()
        cursor = conexion.cursor()

        if accion == "login":
            # Buscamos las credenciales exactas
            cursor.execute(
                "SELECT usuario FROM usuarios WHERE usuario = %s AND password = %s",
                (usuario, password)
            )
            usuario_encontrado = cursor.fetchone()

            if usuario_encontrado:
                session["usuario"] = usuario
                cursor.close()
                conexion.close()
                return redirect(url_for("frases"))
            else:
                mensaje = "Credenciales incorrectas. Inténtalo de nuevo o regístrate."

        elif accion == "registro":
            if confirmar_password != password:
                mensaje = "Las contraseñas deben coincidir."
            else:
                cursor.execute("SELECT usuario FROM usuarios WHERE usuario = %s", (usuario,))
                if cursor.fetchone():
                    mensaje = "Este usuario ya existe, intente iniciar sesión."
                else:
                    cursor.execute(
                        "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)",
                        (usuario, password)
                    )
                    conexion.commit()
                    mensaje = "Usuario registrado correctamente en la base de datos."

        cursor.close()
        conexion.close()

    return render_template("login.html", mensaje=mensaje)

@app.route("/frases", methods=["GET", "POST"])
def frases():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario_actual = session["usuario"]
    conexion = get_conexion()
    cursor = conexion.cursor()

    if request.method == "POST":
        nueva_frase = request.form.get("frase")
        if nueva_frase:
            cursor.execute(
                "INSERT INTO frases (frase, usuario) VALUES (%s, %s)",
                (nueva_frase, usuario_actual)
            )
            conexion.commit()

    # Si es admin, lee todas las frases indicando el autor; si no, solo las propias
    mis_frases = []
    if usuario_actual == "admin":
        cursor.execute("SELECT frase, usuario FROM frases")
        for fila in cursor.fetchall():
            mis_frases.append(f"{fila[0]} (escrito por: {fila[1]})")
    else:
        cursor.execute("SELECT frase FROM frases WHERE usuario = %s", (usuario_actual,))
        for fila in cursor.fetchall():
            mis_frases.append(fila[0])

    cursor.close()
    conexion.close()
    return render_template("frases.html", usuario=usuario_actual, frases=mis_frases)

@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)