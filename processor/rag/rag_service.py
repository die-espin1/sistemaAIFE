from openai import OpenAI
from processor.rag.embeddings import generar_embedding
from processor.rag.vector_store import VectorStore
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

store = VectorStore()

def indexar_documentos(lista_dte):

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