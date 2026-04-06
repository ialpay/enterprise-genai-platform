"""API routes for the initial FastAPI shell."""

from fastapi import APIRouter, HTTPException

from app.ai.llm_client import OllamaClientError, generate_answer
from app.ai.prompts import build_grounded_prompt
from app.api.request_classification import RequestClass, classify_request
from app.api.schemas import AskRequest, AskResponse
from app.retrieval.retriever import Retriever

router = APIRouter()
INSUFFICIENT_INFORMATION_ANSWER = "insufficient information"
GROUNDED_SOURCE = "grounded_retrieval"
NO_CONTEXT_SOURCE = "grounded_no_context"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    request_class = classify_request(payload.question)

    try:
        retrieved_chunks = Retriever().retrieve(payload.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Retrieval service unavailable.") from exc

    if not retrieved_chunks:
        return AskResponse(
            question=payload.question,
            answer=INSUFFICIENT_INFORMATION_ANSWER,
            source=NO_CONTEXT_SOURCE,
        )

    grounded_prompt = build_grounded_prompt(
        question=payload.question,
        retrieved_chunks=retrieved_chunks,
        suspicious=request_class == RequestClass.SUSPICIOUS_OVERRIDE,
        hidden_instruction=request_class == RequestClass.HIDDEN_INSTRUCTION_REQUEST,
    )

    try:
        answer = generate_answer(grounded_prompt)
    except OllamaClientError as exc:
        raise HTTPException(status_code=502, detail="Ollama service unavailable.") from exc
    return AskResponse(question=payload.question, answer=answer, source=GROUNDED_SOURCE)
