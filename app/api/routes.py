from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_response

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(request: QueryRequest):

    answer = generate_response(
        request.question
    )

    return {
        "question": request.question,
        "answer": answer
    }