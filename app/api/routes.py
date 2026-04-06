"""API routes for the initial FastAPI shell."""

import logging

from fastapi import APIRouter, HTTPException

from app.ai.llm_client import OllamaClientError, generate_answer
from app.ai.prompts import build_grounded_prompt
from app.api.request_classification import RequestClass, classify_request
from app.api.schemas import AskRequest, AskResponse
from app.retrieval.retriever import Retriever

router = APIRouter()
logger = logging.getLogger(__name__)
INSUFFICIENT_INFORMATION_ANSWER = "insufficient information"
GROUNDED_SOURCE = "grounded_retrieval"
NO_CONTEXT_SOURCE = "grounded_no_context"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    request_class = classify_request(payload.question)
    logger.info("ask_request classification=%s", request_class.value)

    try:
        retrieved_chunks = Retriever().retrieve(payload.question)
    except Exception as exc:
        logger.warning(
            "ask_outcome classification=%s outcome=retrieval_failure",
            request_class.value,
            exc_info=True,
        )
        raise HTTPException(status_code=502, detail="Retrieval service unavailable.") from exc

    logger.info(
        "ask_retrieval classification=%s has_context=%s retrieved_chunks=%d",
        request_class.value,
        bool(retrieved_chunks),
        len(retrieved_chunks),
    )

    if not retrieved_chunks:
        logger.info(
            "ask_outcome classification=%s outcome=grounded_no_context",
            request_class.value,
        )
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
        logger.warning(
            "ask_outcome classification=%s outcome=ollama_failure",
            request_class.value,
            exc_info=True,
        )
        raise HTTPException(status_code=502, detail="Ollama service unavailable.") from exc

    logger.info(
        "ask_outcome classification=%s outcome=grounded_answer",
        request_class.value,
    )
    return AskResponse(question=payload.question, answer=answer, source=GROUNDED_SOURCE)
