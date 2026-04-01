from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("Falta OPENAI_API_KEY en variables de entorno")

client = OpenAI(api_key=api_key)


def generar_embedding(texto):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return response.data[0].embedding