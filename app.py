from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# Clave necesaria para que Flask cifre las cookies de sesión en el navegador
app.secret_key = "clave_secreta_daw"

@app.route("/", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        accion = request.form.get("accion")
        usuario = request.form.get("usuario")
        password = request.form.get("password")
        confirmar_password = request.form.get("confirmar_password")

        if accion == "login":
            # Leemos usuarios.txt línea por línea buscando usuario:password
            with open("usuarios.txt", "r", encoding="utf-8") as f:
                credenciales = [linea.strip() for linea in f]
            
            if f"{usuario}:{password}" in credenciales:
                session["usuario"] = usuario  # Guardamos el usuario en sesión
                return redirect(url_for("frases"))
            else:
                mensaje = "Credenciales incorrectas. Inténtalo de nuevo o regístrate."

        elif accion == "registro":
            with open("usuarios.txt", "r", encoding="utf-8") as u:
                usuarios = u.read()
                if confirmar_password != password:
                    mensaje = "Las contraseñas deben coincidir."
                elif f"{usuario}" in usuarios:
                    mensaje = "Este usuario ya existe, intente iniciar sesión."
                else:
            # Añadimos el nuevo usuario al final del fichero ("a" = append)
                    with open("usuarios.txt", "a", encoding="utf-8") as f:
                        f.write(f"{usuario}:{password}\n")
                    mensaje = "Usuario registrado. Ahora puedes iniciar sesión."

    return render_template("login.html", mensaje=mensaje)

@app.route("/frases", methods=["GET", "POST"])
def frases():
    # Si no hay sesión activa, mandamos al usuario de vuelta al login
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario_actual = session["usuario"]

    # Si envía el formulario, guardamos la nueva frase junto a su usuario
    if request.method == "POST":
        nueva_frase = request.form.get("frase")
        if nueva_frase:
            with open("frases.txt", "a", encoding="utf-8") as f:
                f.write(f"{nueva_frase}:{usuario_actual}\n")

    # Leemos solo las frases que pertenecen al usuario conectado
    mis_frases = []
    with open("frases.txt", "r", encoding="utf-8") as f:
        for linea in f:
            if ":" in linea:
                texto_frase, autor = linea.strip().rsplit(":", 1)
                if autor == usuario_actual:
                    mis_frases.append(texto_frase)

    return render_template("frases.html", usuario=usuario_actual, frases=mis_frases)

@app.route("/salir")
def salir():
    session.clear()  # Borra los datos de la sesión actual
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)