from flask import Flask, request, send_file, render_template, session
import os, uuid
from pathlib import Path

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

    try:
        if "nit" not in session:
            return {"error": "Debe configurar contribuyente"}, 403

        files = request.files.getlist("files")

        print("📂 Archivos recibidos:", [f.filename for f in files])

        if not files:
            return {"status": "ok", "cantidad": 0, "ignorados": 0}

        # 🔥 Crear sesión de archivos
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

        ruta_sesion = os.path.join("uploads", session_id)
        os.makedirs(ruta_sesion, exist_ok=True)

        documentos = []
        ignorados = 0

        for f in files:
            try:
                if not f.filename.lower().endswith(".json"):
                    ignorados += 1
                    continue

                ruta = os.path.join(ruta_sesion, f.filename)
                f.save(ruta)

                dte = cargar_json_seguro(ruta)

                if dte:
                    documentos.append(dte)
                else:
                    print(f"⚠️ JSON inválido: {f.filename}")
                    ignorados += 1

            except Exception as e:
                print(f"❌ Error procesando {f.filename}: {str(e)}")
                ignorados += 1

        # 🔥 Indexar SOLO en memoria (no guardar en session)
        if documentos:
            try:
                indexar_documentos(documentos)
            except Exception as e:
                print("⚠️ Error indexando documentos:", str(e))

        return {
            "status": "ok",
            "cantidad": len(documentos),
            "ignorados": ignorados
        }

    except Exception as e:
        print("❌ ERROR GENERAL UPLOAD:", str(e))
        return {
            "error": "Error en carga de archivos",
            "detalle": str(e)
        }, 500


# ---------------- PREGUNTAR ----------------
@app.route("/preguntar", methods=["POST"])
def preguntar():

    if "session_id" not in session:
        return {"respuesta": "Primero debes cargar datos"}

    pregunta = request.form.get("pregunta")

    if not pregunta:
        return {"respuesta": "Pregunta vacía"}

    try:
        respuesta = responder_pregunta(pregunta)
        return {"respuesta": respuesta}

    except Exception as e:
        print("⚠️ Error en RAG:", str(e))
        return {"respuesta": "Error al procesar la pregunta"}


# ---------------- GENERAR EXCEL ----------------
@app.route("/generar_excel", methods=["POST"])
def generar_excel():

    if "session_id" not in session:
        return {"error": "No hay datos cargados"}, 400

    session_id = session.get("session_id")
    ruta_sesion = os.path.join("uploads", session_id)

    if not os.path.exists(ruta_sesion):
        return {"error": "No existen archivos para procesar"}, 400

    salida = f"outputs/{uuid.uuid4()}.xlsm"

    try:
        ruta, inconsistencias = generar_anexos(
            ruta_sesion,
            session.get("nit"),
            session.get("dui"),
            session.get("nombre"),
            salida
        )

        # 🔍 LOG DETALLADO
        if inconsistencias:
            print("⚠️ Inconsistencias detectadas:")
            for i in inconsistencias:
                print(i)

        return send_file(ruta, as_attachment=True)

    except Exception as e:
        print("❌ ERROR GENERANDO EXCEL:", str(e))

        return {
            "error": "Error generando Excel",
            "detalle": str(e)
        }, 500


# ---------------- MAIN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)