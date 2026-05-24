import numpy as np

from app.services.embedding_service import (
    generate_embedding
)

semantic_cache = []


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def get_cached_response(
    question,
    threshold=0.90
):

    query_embedding = generate_embedding(
        question
    )

    for item in semantic_cache:

        similarity = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        if similarity >= threshold:

            cached_answer = item["answer"]

            if (cached_answer and "error" not in cached_answer.lower()):
                
                return cached_answer


    return None


def cache_response(question, answer):

    if not answer:
        return

    error_keywords = [
        "error",
        "failed",
        "exception",
        "connection refused",
        "llm error"
    ]

    answer_lower = answer.lower()

    if any(
        keyword in answer_lower
        for keyword in error_keywords
    ):
        return

    embedding = generate_embedding(
        question
    )

    semantic_cache.append({
        "question": question,
        "embedding": embedding,
        "answer": answer
    })