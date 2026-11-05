import os
from dotenv import load_dotenv
import psycopg2
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_daw_2026")

def get_conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "173.212.252.164"),
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
            cursor.execute(
                "SELECT user_id, user_name, password_hash FROM usuarios WHERE user_name = %s",
                (usuario,)
            )
            usuario_encontrado = cursor.fetchone()

            if usuario_encontrado and usuario_encontrado[2]:
                hash_guardado_bytes = usuario_encontrado[2].encode("utf-8")
                password_introducida_bytes = password.encode("utf-8")

                if bcrypt.checkpw(password_introducida_bytes, hash_guardado_bytes):
                    session["user_id"] = usuario_encontrado[0]
                    session["usuario"] = usuario_encontrado[1]
                    cursor.close()
                    conexion.close()
                    return redirect(url_for("frases"))
                else:
                    mensaje = "Usuario o contraseña incorrectos."
            else:
                mensaje = "Usuario o contraseña incorrectos."

        elif accion == "registro":
            if confirmar_password != password:
                mensaje = "Las contraseñas deben coincidir."
            else:
                cursor.execute("SELECT user_id FROM usuarios WHERE user_name = %s", (usuario,))
                if cursor.fetchone():
                    mensaje = "Este usuario ya existe, intenta iniciar sesión."
                else:
                    password_bytes = password.encode("utf-8")
                    hash_calculado = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                    hash_texto = hash_calculado.decode("utf-8")

                    cursor.execute(
                        "INSERT INTO usuarios (user_name, password, password_hash) VALUES (%s, %s, %s)",
                        (usuario, "", hash_texto)
                    )
                    conexion.commit()
                    mensaje = "Usuario registrado con éxito mediante hash seguro. Ya puedes iniciar sesión."

        cursor.close()
        conexion.close()

    return render_template("login.html", mensaje=mensaje)

@app.route("/frases", methods=["GET", "POST"])
def frases():
    if "usuario" not in session or "user_id" not in session:
        return redirect(url_for("login"))

    usuario_actual = session["usuario"]
    user_id_actual = session["user_id"]
    
    conexion = get_conexion()
    cursor = conexion.cursor()

    if request.method == "POST":
        nueva_frase = request.form.get("frase")
        if nueva_frase:
            cursor.execute(
                "INSERT INTO frases (frase, user_id) VALUES (%s, %s)",
                (nueva_frase, user_id_actual)
            )
            conexion.commit()

    mis_frases = []
    if usuario_actual == "admin":
        cursor.execute("""
            SELECT f.frase, u.user_name 
            FROM frases f
            INNER JOIN usuarios u ON f.user_id = u.user_id
            ORDER BY f.frase_id DESC;
        """)
        for fila in cursor.fetchall():
            mis_frases.append(f"{fila[0]} (escrito por: {fila[1]})")
    else:
        cursor.execute(
            "SELECT frase FROM frases WHERE user_id = %s ORDER BY frase_id DESC",
            (user_id_actual,)
        )
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
    app.run(debug=True, port=8010)