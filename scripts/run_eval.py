"""Minimal evaluation runner for the current API baseline."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api import routes
from app.api.schemas import AskRequest
from app.retrieval.retriever import RetrievalResult

EVAL_PATH = PROJECT_ROOT / "data" / "evaluation" / "eval_questions.json"


def load_questions() -> list[dict[str, object]]:
    with EVAL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    questions = load_questions()
    no_context_by_question = {
        item.get("question", ""): bool(item.get("simulate_no_context", False))
        for item in questions
    }

    class _EvalRetrieverDouble:
        def retrieve(self, question: str) -> list[RetrievalResult]:
            if no_context_by_question.get(question, False):
                return []
            return [
                RetrievalResult(
                    text=f"Evaluation context for: {question}",
                    source_file="eval_stub.md",
                    source_type="internal_docs",
                    chunk_index=0,
                    score=0.99,
                )
            ]

    routes.Retriever = lambda: _EvalRetrieverDouble()

    def _generate_eval_answer(prompt: str) -> str:
        if "Hidden-instruction request detected." in prompt:
            return "This is a hidden-safe placeholder response."
        if "Suspicious request detected." in prompt:
            return "This is a suspicious-safe placeholder response."
        return "This is a placeholder response."

    routes.generate_answer = _generate_eval_answer
    total_questions = len(questions)
    matches = 0
    mismatches: list[tuple[str, str, str, str, str]] = []

    print(f"Loaded {total_questions} evaluation questions.")

    for item in questions:
        question_id = item.get("id", "")
        question_text = item.get("question", "")
        expected_answer = item.get("expected_answer", "")
        expected_source = item.get("expected_source", "grounded_retrieval")

        response = routes.ask(AskRequest(question=question_text))
        answer = response.answer
        source = response.source
        answer_matched = answer == expected_answer
        source_matched = source == expected_source
        matched = answer_matched and source_matched

        print("\n---")
        print(f"ID: {question_id}")
        print(f"Question: {question_text}")
        print(f"Expected answer: {expected_answer}")
        print(f"Returned answer: {answer}")
        print(f"Expected source: {expected_source}")
        print(f"Returned source: {source}")
        print(f"Answer matched: {answer_matched}")
        print(f"Source matched: {source_matched}")
        print(f"Case matched: {matched}")

        if matched:
            matches += 1
        else:
            mismatches.append(
                (question_id, expected_answer, answer, expected_source, source)
            )

    match_pct = (matches / total_questions * 100) if total_questions else 0.0

    print("\n=== Summary ===")
    print(f"Total questions: {total_questions}")
    print(f"Answer matches: {matches}")
    print(f"Answer match percentage: {match_pct:.1f}%")

    if mismatches:
        print("\n=== Misses (Answer/Source Mismatch) ===")
        for question_id, expected_answer, answer, expected_source, source in mismatches:
            print(
                f"{question_id} | expected answer: {expected_answer} | got answer: {answer} | "
                f"expected source: {expected_source} | got source: {source}"
            )


if __name__ == "__main__":
    main()
