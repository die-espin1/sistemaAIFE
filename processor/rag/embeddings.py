from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # ← ESTO FALTABA

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_embedding(texto):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return response.data[0].embedding