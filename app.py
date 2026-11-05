import os
import time
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, Length, Regexp, EqualTo

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

class FormularioRegistro(Form):
    usuario = StringField("Nombre de usuario", validators=[
        InputRequired(message="El usuario es obligatorio"),
        Length(min=5, max=20, message="Debe tener entre 5 y 20 caracteres"),
        Regexp(r"^[A-Za-z0-9]{5,20}$", message="Solo se permiten números y letras")
    ])
    password = PasswordField("Contraseña", validators=[
        InputRequired(message="La contraseña es obligatoria"),
        Length(min=8, message="Debe tener al menos 8 caracteres")
    ])
    confirmar_password = PasswordField("Confirmar contraseña", validators=[
        InputRequired(message="Debe confirmar la contraseña"),
        EqualTo("password", message="Las contraseñas no coinciden")
    ])

class FormularioFrase(Form):
    frase = StringField("Frase", validators=[
        InputRequired(message="La frase es obligatoria"),
        Length(min=10, max=100, message="La frase debe tener entre 10 y 100 caracteres")
    ])

@app.route("/", methods=["GET", "POST"])
def login():
    mensaje_error = ""
    mensaje_exito = ""
    login_usuario = ""
    reg_usuario = ""

    if request.args.get("expirado") == "1":
        mensaje_error = "La sesión ha caducado por superar el tiempo de inactividad."

    if request.method == "POST":
        accion = request.form.get("accion")
        conexion = get_conexion()
        cursor = conexion.cursor()

        if accion == "login":
            usuario = request.form.get("usuario", "").strip()
            password = request.form.get("password", "")
            login_usuario = usuario

            cursor.execute(
                "SELECT user_id, user_name, password_hash FROM usuarios WHERE LOWER(user_name) = LOWER(%s)",
                (usuario,)
            )
            usuario_encontrado = cursor.fetchone()

            if usuario_encontrado and usuario_encontrado[2]:
                hash_guardado = usuario_encontrado[2].encode("utf-8")
                password_bytes = password.encode("utf-8")

                if bcrypt.checkpw(password_bytes, hash_guardado):
                    session["user_id"] = usuario_encontrado[0]
                    session["usuario"] = usuario_encontrado[1]
                    session["ultimo_acceso"] = time.time()
                    session["tiempo_sesion"] = int(os.getenv("TIEMPO_SESION", 60))

                    cursor.execute(
                        "INSERT INTO accesos (user_id, fecha_inicio) VALUES (%s, %s) RETURNING acceso_id",
                        (usuario_encontrado[0], datetime.now())
                    )
                    session["acceso_id"] = cursor.fetchone()[0]
                    conexion.commit()

                    cursor.close()
                    conexion.close()
                    return redirect(url_for("frases"))
                else:
                    mensaje_error = "Usuario o contraseña incorrectos."
            else:
                mensaje_error = "Usuario o contraseña incorrectos."

        elif accion == "registro":
            form = FormularioRegistro(request.form)
            reg_usuario = request.form.get("usuario", "").strip()

            if not form.validate():
                mensaje_error = list(form.errors.values())[0][0]
            else:
                usuario_valido = form.usuario.data.strip()
                password_bytes = form.password.data.encode("utf-8")
                hash_texto = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

                cursor.execute(
                    "SELECT user_id FROM usuarios WHERE LOWER(user_name) = LOWER(%s)",
                    (usuario_valido,)
                )
                if cursor.fetchone():
                    mensaje_error = "Este usuario ya existe, intenta iniciar sesión."
                else:
                    cursor.execute(
                        "INSERT INTO usuarios (user_name, password, password_hash) VALUES (%s, %s, %s)",
                        (usuario_valido, "", hash_texto)
                    )
                    conexion.commit()
                    mensaje_exito = "Usuario registrado correctamente. Ya puedes iniciar sesión."
                    reg_usuario = ""

        cursor.close()
        conexion.close()

    return render_template(
        "login.html",
        error=mensaje_error,
        exito=mensaje_exito,
        login_usuario=login_usuario,
        reg_usuario=reg_usuario
    )

@app.route("/frases", methods=["GET", "POST"])
def frases():
    if "usuario" not in session or "user_id" not in session:
        return redirect(url_for("login"))

    ahora = time.time()
    ultimo_acceso = session.get("ultimo_acceso", ahora)
    tiempo_limite = session.get("tiempo_sesion", int(os.getenv("TIEMPO_SESION", 60)))

    conexion = get_conexion()
    cursor = conexion.cursor()

    if ahora - ultimo_acceso > tiempo_limite:
        acceso_id = session.get("acceso_id")
        if acceso_id:
            cursor.execute(
                "UPDATE accesos SET fecha_fin = %s, tipo_fin = %s WHERE acceso_id = %s",
                (datetime.now(), "inactividad", acceso_id)
            )
            conexion.commit()
        cursor.close()
        conexion.close()
        session.clear()
        return redirect(url_for("login", expirado="1"))

    session["ultimo_acceso"] = ahora
    usuario_actual = session["usuario"]
    user_id_actual = session["user_id"]
    error_frase = ""
    mensaje_exito = ""
    frase_enviada = ""

    if request.method == "POST":
        form_frase = FormularioFrase(request.form)
        frase_enviada = request.form.get("frase", "").strip()

        if not form_frase.validate():
            error_frase = list(form_frase.errors.values())[0][0]
        else:
            cursor.execute(
                "INSERT INTO frases (frase, user_id) VALUES (%s, %s)",
                (form_frase.frase.data.strip(), user_id_actual)
            )
            conexion.commit()
            mensaje_exito = "Frase guardada correctamente."
            frase_enviada = ""

    mis_frases = []
    lista_accesos = []
    es_admin = (usuario_actual.strip().lower() == "admin")

    if es_admin:
        cursor.execute("""
            SELECT f.frase, u.user_name 
            FROM frases f
            INNER JOIN usuarios u ON f.user_id = u.user_id
            ORDER BY f.frase_id DESC;
        """)
        for fila in cursor.fetchall():
            mis_frases.append(f"{fila[0]} (escrito por: {fila[1]})")

        cursor.execute("""
            SELECT u.user_name, a.fecha_inicio, a.fecha_fin, a.tipo_fin
            FROM accesos a
            INNER JOIN usuarios u ON a.user_id = u.user_id
            ORDER BY a.acceso_id DESC;
        """)
        lista_accesos = cursor.fetchall()
    else:
        cursor.execute(
            "SELECT frase FROM frases WHERE user_id = %s ORDER BY frase_id DESC",
            (user_id_actual,)
        )
        for fila in cursor.fetchall():
            mis_frases.append(fila[0])

    cursor.close()
    conexion.close()

    return render_template(
        "frases.html",
        usuario=usuario_actual,
        es_admin=es_admin,
        frases=mis_frases,
        accesos=lista_accesos,
        error=error_frase,
        exito=mensaje_exito,
        frase_previa=frase_enviada
    )

@app.route("/salir")
def salir():
    acceso_id = session.get("acceso_id")
    if acceso_id:
        conexion = get_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE accesos SET fecha_fin = %s, tipo_fin = %s WHERE acceso_id = %s",
            (datetime.now(), "voluntaria", acceso_id)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=8010)