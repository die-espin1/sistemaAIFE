from flask import Flask, request, send_file, render_template, flash, redirect
import os, uuid
from processor.excel_service import generar_anexos

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():

    try:
        files = request.files.getlist("files")

        if not files:
            flash("No subiste archivos")
            return redirect("/")

        session = str(uuid.uuid4())
        upload_dir = f"uploads/{session}"
        os.makedirs(upload_dir, exist_ok=True)

        for f in files:
            f.save(os.path.join(upload_dir, f.filename))

        salida = f"outputs/{session}.xlsm"

        resultado = generar_anexos(upload_dir, "plantilla.xlsm", salida)

        if os.path.exists(resultado):
            return send_file(resultado, as_attachment=True)
        else:
            flash("No se generó el archivo")
            return redirect("/")

    except Exception as e:
        flash(str(e))
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)