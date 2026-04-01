from flask import Flask, request, send_file, render_template, flash, redirect
import os, uuid
from processor.excel_service import generar_anexos
from processor.rag.rag_service import responder_pregunta
from processor.json_loader import cargar_json_seguro

app = Flask(__name__)
app.secret_key = "secret"


@app.route("/")
def index():
    return render_template("index.html")

    
@app.route("/preguntar", methods=["POST"])
def preguntar():

    pregunta = request.form.get("pregunta")

    respuesta = responder_pregunta(pregunta)

    return {"respuesta": respuesta}


@app.route("/generar_excel", methods=["POST"])
def generar_excel():

    ruta = generar_anexos("uploads")

    return send_file(ruta, as_attachment=True)


@app.route("/upload", methods=["POST"])
def upload():

    files = request.files.getlist("files")

    documentos = []

    for f in files:
        ruta = os.path.join("uploads", f.filename)
        f.save(ruta)

        dte = cargar_json_seguro(ruta)

        if dte:
            documentos.append(dte)

    from processor.rag.rag_service import indexar_documentos

    indexar_documentos(documentos)

    return {"status": "ok", "cantidad": len(documentos)}


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