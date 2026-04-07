"""Isolated Pilot 1 entrypoint shell for agentic workflow experiments."""

from __future__ import annotations

import argparse
import json

MAX_REQUEST_CHARS = 400
MAX_REQUEST_WORDS = 80
MAX_PLAN_STEPS = 3
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

FOCUS_TARGET_RULES = (
    (("route", "routes", "endpoint", "/ask", "/health", "api"), "app/api/"),
    (("config", "setting", "env", "environment"), "app/core/config.py"),
    (
        ("retrieval", "retriever", "qdrant", "embedding", "vector", "ingest"),
        "app/retrieval/",
    ),
    (("prompt", "grounded"), "app/ai/prompts.py"),
    (("test", "tests", "validation", "pytest"), "tests/"),
    (("script", "scripts", "pilot"), "scripts/"),
    (("doc", "docs", "architecture", "status", "task"), "docs/"),
)


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


def derive_focus_targets(request_text: str) -> list[str]:
    lower = request_text.lower()
    targets: list[str] = []
    for keywords, target in FOCUS_TARGET_RULES:
        if any(keyword in lower for keyword in keywords):
            targets.append(target)
    if not targets:
        targets.append("docs/codex_tasks.md")
    return targets[:MAX_PLAN_STEPS]


def build_ordered_step_plan(request_text: str) -> list[dict[str, object]]:
    targets = derive_focus_targets(request_text)
    step_two_details = ", ".join(targets)
    return [
        {
            "step": 1,
            "name": "Confirm bounded scope",
            "details": (
                "Restate the repository request and keep the workflow within "
                f"{MAX_PLAN_STEPS} planned steps."
            ),
        },
        {
            "step": 2,
            "name": "Inspect likely locations",
            "details": f"Read only the most relevant paths first: {step_two_details}.",
        },
        {
            "step": 3,
            "name": "Return grounded summary",
            "details": (
                "Provide a concise result tied to inspected files and clearly note "
                "remaining gaps."
            ),
        },
    ]


def build_response(request_text: str, errors: list[str]) -> dict[str, object]:
    accepted = not errors
    if accepted:
        final_answer = (
            "Pilot accepted the request and produced a bounded deterministic step "
            "plan. Tool execution is not enabled in Task 77."
        )
        ordered_steps = build_ordered_step_plan(request_text)
        reflection = (
            "Explicit short-horizon planning is now visible for inspection; "
            "comparison value should improve further once read-only tool execution "
            "is added."
        )
    else:
        final_answer = "Pilot shell rejected the request due to input constraints."
        ordered_steps = []
        reflection = (
            "Input validation protects the pilot boundary and keeps runs bounded, "
            "but this run provides no repository analysis result."
        )

    return {
        "comparison_shape_version": "pilot1.v1",
        "pilot": "agentic_workflows",
        "task": "77",
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
            "ordered_steps": ordered_steps,
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
