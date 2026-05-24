from app.services.embedding_service import (
    generate_embedding
)

from app.database.vector_store import (
    search_embeddings
)



def retrieve_relevant_chunks(query):

    query_embedding = generate_embedding(query)

    results = search_embeddings(query_embedding)

    return results