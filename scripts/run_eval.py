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

EVAL_PATH = PROJECT_ROOT / "data" / "evaluation" / "eval_questions.json"


def load_questions() -> list[dict[str, str]]:
    with EVAL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    routes.generate_answer = lambda prompt: "This is a placeholder response."
    questions = load_questions()
    total_questions = len(questions)
    matches = 0
    mismatches: list[tuple[str, str, str]] = []

    print(f"Loaded {total_questions} evaluation questions.")

    for item in questions:
        question_id = item.get("id", "")
        question_text = item.get("question", "")
        expected_answer = item.get("expected_answer", "")

        response = routes.ask(AskRequest(question=question_text))
        answer = response.answer
        matched = answer == expected_answer

        print("\n---")
        print(f"ID: {question_id}")
        print(f"Question: {question_text}")
        print(f"Expected answer: {expected_answer}")
        print(f"Returned answer: {answer}")
        print(f"Answer matched: {matched}")

        if matched:
            matches += 1
        else:
            mismatches.append((question_id, expected_answer, answer))

    match_pct = (matches / total_questions * 100) if total_questions else 0.0

    print("\n=== Summary ===")
    print(f"Total questions: {total_questions}")
    print(f"Answer matches: {matches}")
    print(f"Answer match percentage: {match_pct:.1f}%")

    if mismatches:
        print("\n=== Misses (Answer Mismatch) ===")
        for question_id, expected_answer, answer in mismatches:
            print(f"{question_id} | expected: {expected_answer} | got: {answer}")


if __name__ == "__main__":
    main()
