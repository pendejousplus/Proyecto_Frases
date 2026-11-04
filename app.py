from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
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
            with open("usuarios.txt", "r", encoding="utf-8") as f:
                credenciales = [linea.strip() for linea in f]
            
            if f"{usuario}:{password}" in credenciales:
                session["usuario"] = usuario
                return redirect(url_for("frases"))
            else:
                mensaje = "Credenciales incorrectas. Inténtalo de nuevo o regístrate."

        elif accion == "registro":
            with open("usuarios.txt", "r", encoding="utf-8") as u:
                lista_usuarios = [linea.strip().split(":")[0] for linea in u if ":" in linea]

            if confirmar_password != password:
                mensaje = "Las contraseñas deben coincidir."
            elif usuario in lista_usuarios:
                mensaje = "Este usuario ya existe, intente iniciar sesión."
            else:
                with open("usuarios.txt", "a", encoding="utf-8") as f:
                    f.write(f"{usuario}:{password}\n")
                mensaje = "Usuario registrado. Ahora puedes iniciar sesión."

    return render_template("login.html", mensaje=mensaje)

@app.route("/frases", methods=["GET", "POST"])
def frases():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario_actual = session["usuario"]

    if request.method == "POST":
        nueva_frase = request.form.get("frase")
        if nueva_frase:
            with open("frases.txt", "a", encoding="utf-8") as f:
                f.write(f"{nueva_frase}:{usuario_actual}\n")

    mis_frases = []
    with open("frases.txt", "r", encoding="utf-8") as f:
        for linea in f:
            if ":" in linea:
                texto_frase, autor = linea.strip().rsplit(":", 1)
                # Si es admin ve todas (indicando de quién es cada una); si no, solo las suyas
                if usuario_actual == "admin":
                    mis_frases.append(f"{texto_frase} (escrito por: {autor})")
                elif autor == usuario_actual:
                    mis_frases.append(texto_frase)

    return render_template("frases.html", usuario=usuario_actual, frases=mis_frases)

@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)