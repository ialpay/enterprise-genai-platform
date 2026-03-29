"""Simple retrieval and RAG evaluation runner."""

from __future__ import annotations

from pathlib import Path
import json
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.routes import (
    HIDDEN_INSTRUCTION_PATTERNS,
    INJECTION_PATTERNS,
    ask,
)
from app.api.schemas import AskRequest

EVAL_PATH = PROJECT_ROOT / "data" / "evaluation" / "eval_questions.json"


def load_questions() -> list[dict[str, object]]:
    with EVAL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def extract_keywords(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [word for word in normalized.split() if len(word) > 2]


def keyword_list_matched(answer: str, keywords: list[str]) -> bool:
    if not keywords:
        return False
    normalized_answer = normalize_text(answer)
    matches = sum(1 for keyword in set(keywords) if keyword in normalized_answer)
    required = max(1, len(set(keywords)) // 2)
    return matches >= required


def phrase_list_matched(answer: str, phrases: list[str]) -> bool:
    normalized_answer = normalize_text(answer)
    return any(normalize_text(phrase) in normalized_answer for phrase in phrases if phrase)


def theme_matched(
    answer: str,
    expected_theme: str,
    expected_keywords: list[str],
    acceptable_phrases: list[str],
) -> bool:
    keywords = extract_keywords(expected_theme)
    if keyword_list_matched(answer, keywords):
        return True
    if keyword_list_matched(answer, expected_keywords):
        return True
    if phrase_list_matched(answer, acceptable_phrases):
        return True
    return not expected_theme


def classify_request(question: str) -> str:
    lowered = question.lower()
    if any(pattern in lowered for pattern in HIDDEN_INSTRUCTION_PATTERNS):
        return "hidden_instruction"
    if any(pattern in lowered for pattern in INJECTION_PATTERNS):
        return "suspicious_override"
    return "normal"


def main() -> None:
    questions = load_questions()
    print(f"Loaded {len(questions)} evaluation questions.")
    total_questions = len(questions)
    expected_type_hits = 0
    expected_file_hits = 0
    expected_theme_hits = 0
    acceptable_insufficient_count = 0
    request_class_matches = 0
    file_misses: list[tuple[str, str, list[str]]] = []
    theme_misses: list[tuple[str, str, str]] = []
    unacceptable_insufficient: list[tuple[str, str]] = []
    class_mismatches: list[tuple[str, str, str]] = []
    category_stats: dict[str, dict[str, int]] = {}
    request_class_stats: dict[str, dict[str, int]] = {}

    for item in questions:
        question_id = str(item.get("id"))
        question_text = str(item.get("question"))
        expected_source_type = str(item.get("expected_source_type"))
        expected_source_file = str(item.get("expected_source_file"))
        expected_theme = str(item.get("expected_answer_theme", ""))
        expected_keywords = item.get("expected_answer_keywords", [])
        acceptable_phrases = item.get("acceptable_answer_phrases", [])
        insufficient_allowed = bool(item.get("insufficient_information_allowed", False))
        category = str(item.get("category", "uncategorized"))
        expected_request_class = str(item.get("expected_request_class", "normal"))
        observed_request_class = classify_request(question_text)
        request_class_match = observed_request_class == expected_request_class

        response = ask(AskRequest(question=question_text))
        retrieved_sources = response.retrieved_sources
        retrieved_files = [source.source_file for source in retrieved_sources]
        retrieved_types = [source.source_type for source in retrieved_sources]
        expected_type_hit = expected_source_type in retrieved_types
        expected_file_hit = expected_source_file in retrieved_files
        theme_hit = theme_matched(
            response.answer,
            expected_theme,
            list(expected_keywords) if isinstance(expected_keywords, list) else [],
            list(acceptable_phrases) if isinstance(acceptable_phrases, list) else [],
        )
        insuff_present = "insufficient information" in normalize_text(response.answer)
        insuff_acceptable = (not insuff_present) or insufficient_allowed

        print("\n---")
        print(f"ID: {question_id}")
        print(f"Question: {question_text}")
        print(f"Answer: {response.answer}")
        print(f"Retrieved source files: {', '.join(retrieved_files) if retrieved_files else 'none'}")
        print(f"Category: {category}")
        print(f"Expected request class: {expected_request_class}")
        print(f"Observed request class: {observed_request_class}")
        print(f"Request class matched: {request_class_match}")
        print(f"Expected source type present: {expected_type_hit}")
        print(f"Expected source file present: {expected_file_hit}")
        print(f"Expected answer theme matched: {theme_hit}")
        print(f"Insufficient-information acceptable: {insuff_acceptable}")

        if expected_type_hit:
            expected_type_hits += 1
        if expected_file_hit:
            expected_file_hits += 1
        else:
            file_misses.append((question_id, expected_source_file, retrieved_files))
        if theme_hit:
            expected_theme_hits += 1
        else:
            theme_misses.append((question_id, expected_theme, response.answer))
        if insuff_present and insufficient_allowed:
            acceptable_insufficient_count += 1
        if insuff_present and not insufficient_allowed:
            unacceptable_insufficient.append((question_id, response.answer))
        if request_class_match:
            request_class_matches += 1
        else:
            class_mismatches.append((question_id, expected_request_class, observed_request_class))

        category_entry = category_stats.setdefault(
            category,
            {
                "total": 0,
                "type_hits": 0,
                "file_hits": 0,
                "theme_hits": 0,
                "insufficient_ok": 0,
                "class_matches": 0,
            },
        )
        category_entry["total"] += 1
        if expected_type_hit:
            category_entry["type_hits"] += 1
        if expected_file_hit:
            category_entry["file_hits"] += 1
        if theme_hit:
            category_entry["theme_hits"] += 1
        if insuff_present and insufficient_allowed:
            category_entry["insufficient_ok"] += 1
        if request_class_match:
            category_entry["class_matches"] += 1

        request_class_entry = request_class_stats.setdefault(
            expected_request_class,
            {"total": 0, "matches": 0},
        )
        request_class_entry["total"] += 1
        if request_class_match:
            request_class_entry["matches"] += 1

    type_hit_pct = (expected_type_hits / total_questions * 100) if total_questions else 0.0
    file_hit_pct = (expected_file_hits / total_questions * 100) if total_questions else 0.0
    theme_hit_pct = (expected_theme_hits / total_questions * 100) if total_questions else 0.0
    insuff_ok_pct = (
        acceptable_insufficient_count / total_questions * 100
        if total_questions
        else 0.0
    )
    request_class_match_pct = (
        request_class_matches / total_questions * 100 if total_questions else 0.0
    )

    print("\n=== Summary ===")
    print(f"Total questions: {total_questions}")
    print(f"Expected source type hits: {expected_type_hits}")
    print(f"Expected source file hits: {expected_file_hits}")
    print(f"Expected answer theme hits: {expected_theme_hits}")
    print(f"Acceptable insufficient-information responses: {acceptable_insufficient_count}")
    print(f"Request class match count: {request_class_matches}")
    print(f"Source type hit percentage: {type_hit_pct:.1f}%")
    print(f"Source file hit percentage: {file_hit_pct:.1f}%")
    print(f"Answer theme hit percentage: {theme_hit_pct:.1f}%")
    print(f"Acceptable insufficient-information percentage: {insuff_ok_pct:.1f}%")
    print(f"Request class match percentage: {request_class_match_pct:.1f}%")

    if category_stats:
        print("\n=== Category Summary ===")
        for category in sorted(category_stats.keys()):
            stats = category_stats[category]
            print(
                f"{category} | total: {stats['total']} | source type hits: {stats['type_hits']} "
                f"| source file hits: {stats['file_hits']} | answer theme hits: {stats['theme_hits']} "
                f"| acceptable insufficient: {stats['insufficient_ok']} | request class matches: {stats['class_matches']}"
            )

    if request_class_stats:
        print("\n=== Request Class Summary ===")
        for request_class in ("normal", "suspicious_override", "hidden_instruction"):
            stats = request_class_stats.get(request_class, {"total": 0, "matches": 0})
            total = stats["total"]
            matches = stats["matches"]
            percentage = (matches / total * 100) if total else 0.0
            print(
                f"{request_class} | total: {total} | request class matches: {matches} | percentage: {percentage:.1f}%"
            )

    if file_misses:
        print("\n=== Misses (Expected Source File) ===")
        for question_id, expected_file, retrieved_files in file_misses:
            retrieved = ", ".join(retrieved_files) if retrieved_files else "none"
            print(f"{question_id} | expected: {expected_file} | retrieved: {retrieved}")
    if theme_misses:
        print("\n=== Misses (Expected Answer Theme) ===")
        for question_id, expected_theme, answer in theme_misses:
            print(f"{question_id} | expected theme: {expected_theme} | answer: {answer}")
    if unacceptable_insufficient:
        print("\n=== Misses (Unacceptable Insufficient Information) ===")
        for question_id, answer in unacceptable_insufficient:
            print(f"{question_id} | answer: {answer}")
    if class_mismatches:
        print("\n=== Misses (Request Class Mismatch) ===")
        for question_id, expected_class, observed_class in class_mismatches:
            print(f"{question_id} | expected: {expected_class} | observed: {observed_class}")


if __name__ == "__main__":
    main()
