"""Isolated Pilot 1 entrypoint shell for agentic workflow experiments."""

from __future__ import annotations

import argparse
import json

MAX_REQUEST_CHARS = 400
MAX_REQUEST_WORDS = 80
REPOSITORY_HINTS = {
    ".py",
    "app/",
    "code",
    "docs/",
    "file",
    "files",
    "function",
    "module",
    "repo",
    "repository",
    "route",
    "script",
    "scripts/",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the isolated Pilot 1 shell for one bounded repository-oriented request."
        )
    )
    parser.add_argument(
        "request",
        nargs="+",
        help="Bounded repository-oriented request text.",
    )
    return parser.parse_args()


def normalize_request(parts: list[str]) -> str:
    return " ".join(" ".join(parts).split())


def validate_request(request_text: str) -> list[str]:
    errors: list[str] = []
    lower = request_text.lower()
    words = request_text.split()

    if not request_text:
        errors.append("request must not be empty")
    if len(request_text) > MAX_REQUEST_CHARS:
        errors.append(f"request exceeds {MAX_REQUEST_CHARS} characters")
    if len(words) > MAX_REQUEST_WORDS:
        errors.append(f"request exceeds {MAX_REQUEST_WORDS} words")
    if not any(hint in lower for hint in REPOSITORY_HINTS):
        errors.append("request must be repository-oriented")
    return errors


def build_response(request_text: str, errors: list[str]) -> dict[str, object]:
    accepted = not errors
    if accepted:
        final_answer = (
            "Pilot shell accepted the request. Planning and tool execution are not "
            "enabled in Task 76."
        )
        reflection = (
            "This run validates input handling and response shape only; comparison "
            "value will improve once planning and read-only tool steps are added."
        )
    else:
        final_answer = "Pilot shell rejected the request due to input constraints."
        reflection = (
            "Input validation protects the pilot boundary and keeps runs bounded, "
            "but this run provides no repository analysis result."
        )

    return {
        "comparison_shape_version": "pilot1.v1",
        "pilot": "agentic_workflows",
        "task": "76",
        "entrypoint": "scripts/pilot_agentic_workflow.py",
        "accepted": accepted,
        "input": {
            "request": request_text,
            "constraints": {
                "max_chars": MAX_REQUEST_CHARS,
                "max_words": MAX_REQUEST_WORDS,
                "repository_oriented": True,
            },
        },
        "pilot_response": {
            "final_answer": final_answer,
            "ordered_steps": [],
            "tools_used": [],
            "files_inspected": [],
            "reflection": reflection,
        },
        "validation_errors": errors,
        "isolation": {
            "live_route_touched": False,
            "notes": [
                "Standalone script entrypoint for Pilot 1.",
                "No imports from live /ask route handling.",
            ],
        },
    }


def main() -> None:
    args = parse_args()
    request_text = normalize_request(args.request)
    errors = validate_request(request_text)
    response = build_response(request_text, errors)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
