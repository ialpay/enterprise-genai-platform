"""API routes for the initial FastAPI shell."""

from fastapi import APIRouter, HTTPException

from app.ai.llm_client import OllamaClientError, generate_answer
from app.api.schemas import AskRequest, AskResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    try:
        answer = generate_answer(payload.question)
    except OllamaClientError as exc:
        raise HTTPException(status_code=502, detail="Ollama service unavailable.") from exc
    return AskResponse(question=payload.question, answer=answer, source="ollama")
