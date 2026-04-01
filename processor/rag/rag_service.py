from openai import OpenAI
from processor.rag.embeddings import generar_embedding
from processor.rag.vector_store import VectorStore
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("Falta OPENAI_API_KEY en variables de entorno")

client = OpenAI(api_key=api_key)

store = VectorStore()


def indexar_documentos(lista_dte):

    if not lista_dte:
        return

    for dte in lista_dte:

        texto = f"""
        Fecha: {dte.get("identificacion", {}).get("fecEmi")}
        Tipo: {dte.get("identificacion", {}).get("tipoDte")}
        Total: {dte.get("resumen", {}).get("montoTotalOperacion")}
        Cliente: {dte.get("receptor", {}).get("nombre")}
        """

        emb = generar_embedding(texto)
        store.agregar(emb, texto)


def responder_pregunta(pregunta):

    if not store.embeddings:
        return "No hay datos indexados aún"

    emb_pregunta = generar_embedding(pregunta)

    contextos = store.buscar(emb_pregunta)

    prompt = f"""
    Usa la siguiente información para responder:

    {contextos}

    Pregunta: {pregunta}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content