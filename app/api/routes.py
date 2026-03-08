"""API routes for the initial FastAPI shell."""

from fastapi import APIRouter

from app.api.schemas import AskRequest, AskResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    _ = payload
    return AskResponse(answer="This is a placeholder response.")
