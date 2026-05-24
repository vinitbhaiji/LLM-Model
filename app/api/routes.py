from fastapi import APIRouter
from pydantic import BaseModel
from app.core.logger import logger
from fastapi import UploadFile, File
from app.services.ingestion_service import (
    save_file,
    extract_text,
    chunk_text
)
from app.services.llm_service import generate_response
from app.services.embedding_service import generate_embeddings_batch
from app.database.vector_store import add_embeddings_batch
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.cache_service import (
    get_cached_response,
    cache_response
)
from fastapi.responses import StreamingResponse
from app.services.llm_service import stream_response

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: QueryRequest):

    logger.info(
        f"Received question: {request.question}"
    )

    try:

        cached_answer = get_cached_response(
            request.question
        )

        if cached_answer:

            logger.info("Cache hit")

            return {
                "question": request.question,
                "answer": cached_answer,
                "source": "cache"
            }

        chunks = retrieve_relevant_chunks(
            request.question
        )

        if not chunks:

            return {
                "answer": "No relevant information found"
            }

        context = "\n".join(
            chunk[:300] for chunk in chunks
        )

        prompt = f"""
        You are an AI assistant for answering questions
        based ONLY on provided context.

        Rules:
        - Only use provided context
        - If answer is not found, say:
          'I don't know based on provided data'
        - Be concise

        Context:
        {context}

        Question:
        {request.question}
        """

        answer = generate_response(prompt)

        cache_response(
            request.question,
            answer
        )

        logger.info(
            "RAG response generated"
        )

        return {
            "question": request.question,
            "answer": answer,
            "source": "rag"
        }

    except Exception as e:

        logger.error(
            f"Error: {str(e)}"
        )

        return {
            "error": str(e)
        }
    
@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    logger.info(f"Uploading file: {file.filename}")

    try:

        file_path = save_file(file)

        text = extract_text(file_path)

        chunks = chunk_text(text)

        embeddings = generate_embeddings_batch(chunks)
        add_embeddings_batch(chunks, embeddings)

        logger.info(
            f"Stored {len(chunks)} chunks in vector DB"
        )

        return {
            "filename": file.filename,
            "chunks": len(chunks),
            "status": "stored in vector DB"
        }

    except Exception as e:

        logger.error(f"Upload error: {str(e)}")

        return {
            "error": str(e)
        }
    
@router.post("/stream")
def stream_answer(request: QueryRequest):

    logger.info(
        f"Streaming question: {request.question}"
    )

    try:

        cached_answer = get_cached_response(
            request.question
        )

        if cached_answer:

            return {
                "answer": cached_answer,
                "source": "cache"
            }

        chunks = retrieve_relevant_chunks(
            request.question
        )

        if not chunks:

            return {
                "answer": "No relevant information found"
            }

        context = "\n".join(
            chunk[:300] for chunk in chunks
        )

        prompt = f"""
        You are an AI assistant.

        Use ONLY the provided context.

        Context:
        {context}

        Question:
        {request.question}
        """

        return StreamingResponse(
            stream_response(prompt),
            media_type="text/plain"
        )

    except Exception as e:

        logger.error(f"Streaming error: {str(e)}")

        return {
            "error": str(e)
        }