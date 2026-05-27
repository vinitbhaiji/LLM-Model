import chromadb

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


def add_embedding(chunk, embedding):

    collection.add(
        documents=[chunk],
        embeddings=[embedding],
        ids=[str(hash(chunk))]
    )


def search_embeddings(query_embedding, top_k=1):

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results["documents"][0]

def add_embeddings_batch(chunks, embeddings):

    ids = [
        str(hash(chunk))
        for chunk in chunks
    ]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )