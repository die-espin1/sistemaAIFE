import numpy as np

class VectorStore:

    def __init__(self):
        self.embeddings = []
        self.textos = []

    def agregar(self, embedding, texto):
        self.embeddings.append(np.array(embedding))
        self.textos.append(texto)

    def buscar(self, embedding, k=5):

        embedding = np.array(embedding)

        similitudes = []

        for i, emb in enumerate(self.embeddings):
            score = np.dot(embedding, emb) / (
                np.linalg.norm(embedding) * np.linalg.norm(emb)
            )
            similitudes.append((score, i))

        similitudes.sort(reverse=True)

        indices = [i for _, i in similitudes[:k]]

        return [self.textos[i] for i in indices]