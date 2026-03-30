"""API routes for the initial FastAPI shell."""

from fastapi import APIRouter, HTTPException

from app.ai.llm_client import OllamaClientError, generate_answer
from app.ai.prompts import build_grounded_prompt
from app.api.schemas import AskRequest, AskResponse
from app.retrieval.retriever import Retriever

router = APIRouter()

INSUFFICIENT_INFORMATION = "insufficient information"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    try:
        retriever = Retriever()
        retrieved_chunks = retriever.retrieve(payload.question, limit=5)
    except OllamaClientError as exc:
        raise HTTPException(status_code=502, detail="Ollama service unavailable.") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Retrieval failed.") from exc

    if not retrieved_chunks:
        return AskResponse(
            question=payload.question,
            answer=INSUFFICIENT_INFORMATION,
            source="rag",
        )

    prompt = build_grounded_prompt(
        question=payload.question,
        retrieved_chunks=retrieved_chunks,
    )

    try:
        answer = generate_answer(prompt)
    except OllamaClientError as exc:
        raise HTTPException(status_code=502, detail="Ollama service unavailable.") from exc

    return AskResponse(question=payload.question, answer=answer, source="rag")
