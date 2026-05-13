import numpy as np

from app.services.embedding_service import generate_embedding
from app.database.vector_store import load_db


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_chunks(query, top_k=3):

    query_embedding = generate_embedding(query)

    db = load_db()

    scored_chunks = []

    for item in db:

        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        scored_chunks.append(
            (score, item["text"])
        )

    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    top_chunks = [
        chunk for _, chunk in scored_chunks[:top_k]
    ]

    return top_chunks