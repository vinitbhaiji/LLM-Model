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
from app.services.memory_service import (
    get_or_create_session,
    add_message,
    get_conversation_history
)

router = APIRouter()


class QueryRequest(BaseModel):

    question: str
    session_id: str | None = None

def build_prompt(
    session_id,
    question,
    context
):

    history = get_conversation_history(
        session_id
    )

    return f"""
    History:
    {history}
    
    Context:
    {context[:500]}
    
    Question:
    {question}
    
    Answer briefly and precisely.
    """

@router.post("/ask")
def ask_question(request: QueryRequest):

    try:

        session_id = get_or_create_session(
            request.session_id
        )

        cached_answer = get_cached_response(
            request.question
        )

        if cached_answer:

            return {
                "session_id": session_id,
                "answer": cached_answer,
                "source": "cache"
            }

        chunks = retrieve_relevant_chunks(
            request.question
        )

        context = "\n".join(
            chunk[:150] for chunk in chunks
        )

        add_message(
            session_id,
            "user",
            request.question
        )

        prompt = build_prompt(
            session_id,
            request.question,
            context
        )

        answer = generate_response(prompt)

        add_message(
            session_id,
            "assistant",
            answer
        )

        cache_response(
            request.question,
            answer
        )

        return {
            "session_id": session_id,
            "answer": answer,
            "source": "rag"
        }

    except Exception as e:

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

    try:

        session_id = get_or_create_session(
            request.session_id
        )

        chunks = retrieve_relevant_chunks(
            request.question
        )

        context = "\n".join(
            chunk[:150] for chunk in chunks
        )

        add_message(
            session_id,
            "user",
            request.question
        )

        prompt = build_prompt(
            session_id,
            request.question,
            context
        )

        return StreamingResponse(
            stream_response(prompt),
            media_type="text/plain",
            headers={
                "X-Session-ID": session_id
            }
        )

    except Exception as e:

        return {
            "error": str(e)
        }