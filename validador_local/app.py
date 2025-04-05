from flask import Flask, request, render_template, redirect

app = Flask(__name__)

@app.route("/")
def index():
    # A futuro podés agregar validaciones como IP o timestamp
    return render_template("proximidad.html")

@app.route("/validar", methods=["POST"])
def validar():
    # Si pasa la validación local, redirige a la app principal
    return redirect("https://karma-costume-holder-seniors.trycloudflare.com", code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
