from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_response
from app.core.logger import logger
from fastapi import UploadFile, File
from app.services.ingestion_service import (
    save_file,
    extract_text,
    chunk_text
)
from app.services.embedding_service import generate_embedding
from app.database.vector_store import add_embedding
from app.services.retrieval_service import retrieve_relevant_chunks

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: QueryRequest):

    logger.info(f"Received question: {request.question}")

    try:

        chunks = retrieve_relevant_chunks(request.question)

        if not chunks:
            
            return {
                "answer": "No relevant information found in documents"
            }

        context = "\n\n".join(chunks)

        prompt = f"""
        You are an AI assistant for answering questions based ONLY on provided context.
        
        Rules:
        - Only use the context below
        - If answer is not in context, say "I don't know based on provided data"
        - Do not make up answers
        - Be concise and precise

        Context:
        {context}

        Question:
        {request.question}
        """

        answer = generate_response(prompt)

        logger.info("RAG response generated")

        return {
            "question": request.question,
            "answer": answer,
            "context_used": len(chunks)
        }

    except Exception as e:

        logger.error(f"Error: {str(e)}")

        return {"error": str(e)}
    
@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    logger.info(f"Uploading file: {file.filename}")

    try:

        file_path = save_file(file)

        text = extract_text(file_path)

        chunks = chunk_text(text)

        for chunk in chunks:
            embedding = generate_embedding(chunk)
            
            if embedding:
                add_embedding(chunk, embedding)

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