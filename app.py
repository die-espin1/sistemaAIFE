from flask import Flask, request, send_file, render_template, session
import os, uuid

from processor.excel_service import generar_anexos
from processor.rag.rag_service import responder_pregunta, indexar_documentos
from processor.json_loader import cargar_json_seguro

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- CARPETAS ----------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- CONFIG ----------------
@app.route("/config", methods=["POST"])
def config():

    nit = request.form.get("nit")
    dui = request.form.get("dui")
    nombre = request.form.get("nombre")

    if not nit or not nombre:
        return {"error": "Datos incompletos"}, 400

    session["nit"] = nit
    session["dui"] = dui or ""
    session["nombre"] = nombre

    return {"status": "ok"}


# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():

    if "nit" not in session:
        return {"error": "Debe configurar contribuyente"}, 403

    files = request.files.getlist("files")

    if not files:
        return {"cantidad": 0}

    documentos = []

    for f in files:
        ruta = os.path.join("uploads", f.filename)
        f.save(ruta)

        dte = cargar_json_seguro(ruta)

        if dte:
            documentos.append(dte)

    # Guardar en sesión (fuente única)
    session["documentos"] = documentos

    # Indexar UNA SOLA VEZ
    indexar_documentos(documentos)

    return {"status": "ok", "cantidad": len(documentos)}


# ---------------- PREGUNTAR ----------------
@app.route("/preguntar", methods=["POST"])
def preguntar():

    if "documentos" not in session:
        return {"respuesta": "Primero debes cargar datos"}

    pregunta = request.form.get("pregunta")

    if not pregunta:
        return {"respuesta": "Pregunta vacía"}

    try:
        respuesta = responder_pregunta(pregunta)
        return {"respuesta": respuesta}
    except Exception:
        return {"respuesta": "Error al procesar la pregunta"}


# ---------------- GENERAR EXCEL ----------------
@app.route("/generar_excel", methods=["POST"])
def generar_excel():

    if "documentos" not in session:
        return {"error": "No hay datos cargados"}, 400

    salida = f"outputs/{uuid.uuid4()}.xlsm"

    try:
        ruta, inconsistencias = generar_anexos(
           session["documentos"],
           session.get("nit"),
           session.get("dui"),
           session.get("nombre"),
           salida
        )

        return send_file(ruta, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500


# ---------------- MAIN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)