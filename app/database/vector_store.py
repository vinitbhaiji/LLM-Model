import json
import os

VECTOR_DB_PATH = "data/vector_store.json"


def load_db():

    if not os.path.exists(VECTOR_DB_PATH):

        return []

    with open(VECTOR_DB_PATH, "r") as f:

        return json.load(f)


def save_db(data):

    with open(VECTOR_DB_PATH, "w") as f:

        json.dump(data, f)


def add_embedding(chunk, embedding):

    db = load_db()

    db.append({
        "text": chunk,
        "embedding": embedding
    })

    save_db(db)