from sentence_transformers import SentenceTransformer

from app.core.logger import logger

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text):

    try:

        embedding = model.encode(text)

        return embedding.tolist()

    except Exception as e:

        logger.error(f"Embedding error: {str(e)}")

        return None