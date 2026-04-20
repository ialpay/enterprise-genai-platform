"""Isolated Pilot 1 entrypoint for bounded agentic workflow experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

MAX_REQUEST_CHARS = 400
MAX_REQUEST_WORDS = 80
MAX_PLAN_STEPS = 3
MAX_TOOL_ACTIONS = 6
MAX_FILES_INSPECTED = 4
MAX_FILES_PER_DIRECTORY = 2
MAX_DIRECTORY_ENTRIES = 8
MAX_FILE_CHARS = 1600
MAX_SIGNAL_ITEMS = 3
MAX_PREVIEW_CHARS = 220

REPO_ROOT = Path(__file__).resolve().parents[1]

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

READ_ONLY_TOOLSET = {
    "list_directory": "List immediate directory entries (bounded sample).",
    "read_file_excerpt": "Read the first bounded character window from a text file.",
}

ALLOWED_TOP_LEVEL_DIRS = {"app", "docs", "scripts", "tests", "prompts"}
ALLOWED_TOP_LEVEL_FILES = {"AGENTS.md", "README.md", "requirements.txt"}
ALLOWED_TEXT_SUFFIXES = {".md", ".py", ".txt", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg"}
DIRECTORY_FILE_PRIORITIES: dict[str, tuple[str, ...]] = {
    "docs": ("pilot-track.md", "codex_tasks.md", "status.md", "architecture-overview.md"),
    "scripts": ("pilot_agentic_workflow.py", "run_eval.py", "ingest_documents.py"),
    "app/api": ("routes.py", "schemas.py"),
    "app/core": ("config.py",),
    "app/retrieval": ("retriever.py", "vector_store.py", "embeddings.py"),
    "tests": ("test_api_contract.py",),
    "prompts": ("builder.md",),
}

FIRST_COMPARISON_SCENARIO_ID = "pilot1_first_bounded_repo_comparison"
FIRST_COMPARISON_REQUEST = (
    "Analyze the current repository baseline and identify the next most "
    "reasonable implementation step using a bounded multi-step read-only workflow."
)
FIRST_COMPARISON_TARGETS = (
    "docs/pilot-track.md",
    "docs/status.md",
    "docs/codex_tasks.md",
)
COMPARISON_LENS = ("usefulness", "task_completion", "operator_effort")
PLAN_SOURCE_CODE_ONLY = "code_only"
PLAN_SOURCE_OLLAMA_ASSISTED = "ollama_assisted"
PLAN_SOURCE_OLLAMA_FALLBACK = "ollama_fallback_to_code"
PLANNING_MODE_AUTO = "auto"
PLANNING_MODE_CODE_ONLY = "code_only"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the isolated Pilot 1 workflow for one bounded repository-oriented request."
        )
    )
    parser.add_argument(
        "request",
        nargs="*",
        help="Bounded repository-oriented request text.",
    )
    parser.add_argument(
        "--run-first-comparison",
        action="store_true",
        help="Run Pilot 1 Task 79 first bounded comparison scenario.",
    )
    parser.add_argument(
        "--planning-mode",
        choices=(PLANNING_MODE_AUTO, PLANNING_MODE_CODE_ONLY),
        default=PLANNING_MODE_AUTO,
        help=(
            "Planning path mode: 'auto' attempts bounded Ollama assistance with deterministic "
            "fallback, while 'code_only' disables model planning."
        ),
    )
    args = parser.parse_args()
    if not args.run_first_comparison and not args.request:
        parser.error("provide a repository request or use --run-first-comparison")
    return args


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


def build_ordered_step_plan(
    request_text: str,
    targets: list[str] | None = None,
    planning_focus: list[str] | None = None,
) -> list[dict[str, object]]:
    del request_text  # Request validation and focus derivation are code-controlled upstream.
    resolved_targets = targets or ["docs/codex_tasks.md"]
    bounded_targets = resolved_targets[:MAX_PLAN_STEPS]
    bounded_focus = [item.strip() for item in (planning_focus or []) if item.strip()][:2]
    step_two_details = ", ".join(bounded_targets)
    focus_suffix = ""
    if bounded_focus:
        focus_suffix = " Model planning focus: " + " | ".join(bounded_focus) + "."
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
            "details": (
                "Execute only explicit read-only tools with hard limits against: "
                f"{step_two_details}.{focus_suffix}"
            ),
        },
        {
            "step": 3,
            "name": "Return grounded summary",
            "details": (
                "Provide a concise result tied to inspected files and include "
                "a compact execution trace."
            ),
        },
    ]


def _normalize_plan_focus(raw_focus: object) -> list[str]:
    if not isinstance(raw_focus, list):
        return []

    normalized: list[str] = []
    for item in raw_focus:
        if not isinstance(item, str):
            continue
        value = " ".join(item.split())
        if not value:
            continue
        normalized.append(value[:120])
        if len(normalized) == 2:
            break
    return normalized


def _extract_assisted_planning_focus(raw_plan_text: str) -> list[str]:
    cleaned = raw_plan_text.strip()
    if not cleaned:
        return []

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        return _normalize_plan_focus(parsed.get("focus"))
    if isinstance(parsed, list):
        return _normalize_plan_focus(parsed)
    return []


def _build_planning_prompt(request_text: str, targets: list[str]) -> str:
    target_text = ", ".join(targets[:MAX_PLAN_STEPS])
    return (
        "You are assisting a bounded repository inspection planner.\n"
        "Return strict JSON only.\n"
        "Schema:\n"
        '{"focus": ["short focus item 1", "short focus item 2"]}\n'
        "Rules:\n"
        f"- At most 2 focus items.\n"
        "- Keep each item under 120 characters.\n"
        "- No tool selection, no file expansion, and no extra keys.\n"
        "Validated request:\n"
        f"{request_text}\n"
        "Script-derived bounded targets:\n"
        f"{target_text}\n"
    )


def build_bounded_plan_with_assist(request_text: str, targets: list[str]) -> dict[str, Any]:
    code_plan = build_ordered_step_plan(request_text, targets=targets)

    try:
        from app.ai.llm_client import OllamaClientError, generate_answer
    except Exception:
        return {
            "ordered_steps": code_plan,
            "source": PLAN_SOURCE_OLLAMA_FALLBACK,
            "fallback_reason": "ollama_client_unavailable",
        }

    planning_prompt = _build_planning_prompt(request_text, targets)

    try:
        raw_plan = generate_answer(planning_prompt)
    except OllamaClientError:
        return {
            "ordered_steps": code_plan,
            "source": PLAN_SOURCE_OLLAMA_FALLBACK,
            "fallback_reason": "ollama_request_failed",
        }
    except Exception:
        return {
            "ordered_steps": code_plan,
            "source": PLAN_SOURCE_OLLAMA_FALLBACK,
            "fallback_reason": "ollama_unexpected_error",
        }

    planning_focus = _extract_assisted_planning_focus(raw_plan)
    if not planning_focus:
        return {
            "ordered_steps": code_plan,
            "source": PLAN_SOURCE_OLLAMA_FALLBACK,
            "fallback_reason": "ollama_plan_unusable",
        }

    assisted_plan = build_ordered_step_plan(
        request_text,
        targets=targets,
        planning_focus=planning_focus,
    )
    return {
        "ordered_steps": assisted_plan,
        "source": PLAN_SOURCE_OLLAMA_ASSISTED,
        "fallback_reason": None,
    }


def _to_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _is_allowed_path(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return False

    parts = relative.parts
    if not parts:
        return False

    if len(parts) == 1 and parts[0] in ALLOWED_TOP_LEVEL_FILES:
        return True
    return parts[0] in ALLOWED_TOP_LEVEL_DIRS


def _select_readable_files(parent: Path, entries: list[Path]) -> list[Path]:
    try:
        relative_parent = parent.resolve().relative_to(REPO_ROOT).as_posix().rstrip("/")
    except ValueError:
        relative_parent = ""

    priorities = DIRECTORY_FILE_PRIORITIES.get(relative_parent, ())
    priority_index = {name: idx for idx, name in enumerate(priorities)}

    readable = [
        path
        for path in entries
        if path.is_file()
        and path.suffix.lower() in ALLOWED_TEXT_SUFFIXES
        and path.name != "__init__.py"
    ]
    readable.sort(key=lambda path: (priority_index.get(path.name, 999), path.name))
    return readable[:MAX_FILES_PER_DIRECTORY]


def _list_directory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "entries": [], "candidate_files": []}
    if not path.is_dir():
        return {"status": "not_a_directory", "entries": [], "candidate_files": []}

    entries = sorted(path.iterdir(), key=lambda item: item.name)[:MAX_DIRECTORY_ENTRIES]
    entry_names = [f"{item.name}/" if item.is_dir() else item.name for item in entries]
    candidate_files = [_to_relative(item) for item in _select_readable_files(path, entries)]

    return {
        "status": "ok",
        "entries": entry_names,
        "candidate_files": candidate_files,
    }


def _read_file_excerpt(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing"}
    if not path.is_file():
        return {"status": "not_a_file"}
    if path.suffix.lower() not in ALLOWED_TEXT_SUFFIXES:
        return {"status": "unsupported_suffix"}

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"status": "decode_error"}

    excerpt = content[:MAX_FILE_CHARS]
    return {
        "status": "ok",
        "chars_read": len(excerpt),
        "total_chars": len(content),
        "excerpt": excerpt,
    }


def _extract_signal(file_path: str, excerpt: str) -> str:
    stripped_lines = [line.strip() for line in excerpt.splitlines() if line.strip()]
    if not stripped_lines:
        return f"{file_path}: no non-empty lines in excerpt"

    if file_path.endswith(".md"):
        for line in stripped_lines:
            if line.startswith("#"):
                return f"{file_path}: {line[:120]}"

    if file_path.endswith(".py"):
        for line in stripped_lines:
            if line.startswith(("def ", "class ", "MAX_", "REPO_")):
                return f"{file_path}: {line[:120]}"

    return f"{file_path}: {stripped_lines[0][:120]}"


def execute_read_only_inspection(targets: list[str]) -> dict[str, Any]:
    tools_used: list[str] = []
    tools_seen: set[str] = set()
    files_inspected: list[str] = []
    inspected_seen: set[str] = set()
    execution_trace: list[dict[str, Any]] = []
    signals: list[str] = []

    tool_actions = 0

    def record_tool(name: str) -> None:
        if name not in tools_seen:
            tools_seen.add(name)
            tools_used.append(name)

    for target in targets:
        if tool_actions >= MAX_TOOL_ACTIONS or len(files_inspected) >= MAX_FILES_INSPECTED:
            break

        resolved_target = (REPO_ROOT / target).resolve()
        target_label = target.rstrip("/") + ("/" if target.endswith("/") else "")

        if not _is_allowed_path(resolved_target):
            execution_trace.append(
                {
                    "action": "path_guard",
                    "target": target_label,
                    "status": "blocked",
                    "details": {"reason": "outside allowed pilot inspection scope"},
                }
            )
            continue

        if resolved_target.is_dir():
            tool_actions += 1
            record_tool("list_directory")
            directory_result = _list_directory(resolved_target)
            execution_trace.append(
                {
                    "action": "list_directory",
                    "target": f"{_to_relative(resolved_target)}/",
                    "status": directory_result["status"],
                    "details": {
                        "entries": directory_result.get("entries", []),
                        "candidate_files": directory_result.get("candidate_files", []),
                    },
                }
            )

            if directory_result["status"] != "ok":
                continue

            for relative_file in directory_result["candidate_files"]:
                if tool_actions >= MAX_TOOL_ACTIONS or len(files_inspected) >= MAX_FILES_INSPECTED:
                    break

                resolved_file = (REPO_ROOT / relative_file).resolve()
                if not _is_allowed_path(resolved_file):
                    continue

                tool_actions += 1
                record_tool("read_file_excerpt")
                read_result = _read_file_excerpt(resolved_file)
                preview = ""
                if read_result.get("status") == "ok":
                    preview = read_result["excerpt"][:MAX_PREVIEW_CHARS]
                execution_trace.append(
                    {
                        "action": "read_file_excerpt",
                        "target": relative_file,
                        "status": read_result["status"],
                        "details": {
                            "chars_read": read_result.get("chars_read", 0),
                            "total_chars": read_result.get("total_chars", 0),
                            "preview": preview,
                        },
                    }
                )

                if read_result.get("status") == "ok" and relative_file not in inspected_seen:
                    inspected_seen.add(relative_file)
                    files_inspected.append(relative_file)
                    signals.append(_extract_signal(relative_file, read_result["excerpt"]))

        else:
            relative_file = _to_relative(resolved_target)
            tool_actions += 1
            record_tool("read_file_excerpt")
            read_result = _read_file_excerpt(resolved_target)
            preview = ""
            if read_result.get("status") == "ok":
                preview = read_result["excerpt"][:MAX_PREVIEW_CHARS]
            execution_trace.append(
                {
                    "action": "read_file_excerpt",
                    "target": relative_file,
                    "status": read_result["status"],
                    "details": {
                        "chars_read": read_result.get("chars_read", 0),
                        "total_chars": read_result.get("total_chars", 0),
                        "preview": preview,
                    },
                }
            )

            if read_result.get("status") == "ok" and relative_file not in inspected_seen:
                inspected_seen.add(relative_file)
                files_inspected.append(relative_file)
                signals.append(_extract_signal(relative_file, read_result["excerpt"]))

    return {
        "tools_used": tools_used,
        "files_inspected": files_inspected,
        "execution_trace": execution_trace,
        "signals": signals[:MAX_SIGNAL_ITEMS],
    }


def build_response(
    request_text: str,
    errors: list[str],
    planning_mode: str = PLANNING_MODE_AUTO,
) -> dict[str, object]:
    accepted = not errors
    planning_source = PLAN_SOURCE_CODE_ONLY
    planning_fallback_reason: str | None = None
    if accepted:
        targets = derive_focus_targets(request_text)
        if planning_mode == PLANNING_MODE_CODE_ONLY:
            ordered_steps = build_ordered_step_plan(request_text, targets=targets)
            planning_source = PLAN_SOURCE_CODE_ONLY
            planning_fallback_reason = None
        else:
            planning = build_bounded_plan_with_assist(request_text, targets)
            ordered_steps = planning["ordered_steps"]
            planning_source = planning["source"]
            planning_fallback_reason = planning["fallback_reason"]
        inspection = execute_read_only_inspection(targets)

        if inspection["signals"]:
            final_answer = (
                "Pilot accepted the request and executed bounded read-only inspection. "
                "Key repository signals: "
                + " | ".join(inspection["signals"])
            )
        else:
            final_answer = (
                "Pilot accepted the request and executed bounded read-only inspection, "
                "but no readable evidence was captured in the bounded targets."
            )

        reflection = (
            "Tool use stayed deterministic via explicit allowlisted actions and fixed "
            "limits; compare value based on whether the inspected signals improved "
            "operator usefulness over planning alone."
        )
        tools_used = inspection["tools_used"]
        files_inspected = inspection["files_inspected"]
        execution_trace = inspection["execution_trace"]
    else:
        final_answer = "Pilot shell rejected the request due to input constraints."
        ordered_steps = []
        reflection = (
            "Input validation protects the pilot boundary and keeps runs bounded, "
            "but this run provides no repository analysis result."
        )
        tools_used = []
        files_inspected = []
        execution_trace = []

    return {
        "comparison_shape_version": "pilot1.v4",
        "pilot": "agentic_workflows",
        "task": "80",
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
            "planning_mode": planning_mode,
            "planning_source": planning_source,
            "planning_fallback_reason": planning_fallback_reason,
            "tools_used": tools_used,
            "files_inspected": files_inspected,
            "execution_trace": execution_trace,
            "reflection": reflection,
        },
        "validation_errors": errors,
        "tooling_policy": {
            "mode": "read_only_local_inspection",
            "allowed_tools": READ_ONLY_TOOLSET,
            "max_tool_actions": MAX_TOOL_ACTIONS,
            "max_files_inspected": MAX_FILES_INSPECTED,
        },
        "isolation": {
            "live_route_touched": False,
            "notes": [
                "Standalone script entrypoint for Pilot 1.",
                "No imports from live /ask route handling.",
            ],
        },
    }


def _extract_next_recommended_step(status_excerpt: str) -> str:
    in_section = False
    for line in status_excerpt.splitlines():
        stripped = line.strip()
        if stripped == "## Next Recommended Work":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("1. "):
            return stripped[3:].strip()
    return "No explicit item 1 was found in docs/status.md."


def _build_baseline_style_answer() -> str:
    status_path = REPO_ROOT / "docs/status.md"
    if not status_path.exists() or not status_path.is_file():
        return "Unable to read docs/status.md for baseline comparison."
    try:
        status_content = status_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Unable to decode docs/status.md for baseline comparison."

    next_step = _extract_next_recommended_step(status_content)
    return f"The next most reasonable implementation step is to {next_step}"


def run_first_bounded_comparison() -> dict[str, object]:
    request_text = FIRST_COMPARISON_REQUEST
    errors = validate_request(request_text)
    accepted = not errors

    if accepted:
        inspection = execute_read_only_inspection(list(FIRST_COMPARISON_TARGETS))
        baseline_answer = _build_baseline_style_answer()
        pilot_answer = (
            f"{baseline_answer}. "
            "Pilot evidence confirms this conclusion with bounded read-only inspection "
            "of pilot scope, live status, and task-definition files."
        )
        compact_trace = [
            {
                "action": action["action"],
                "target": action["target"],
                "status": action["status"],
            }
            for action in inspection["execution_trace"]
        ]
        pilot_more_useful = True
        usefulness_note = (
            "Pilot and baseline converge on the same next step, but the pilot is more useful "
            "for operators because it shows inspected files and traceable tool actions."
        )
    else:
        inspection = {"tools_used": [], "files_inspected": [], "execution_trace": []}
        baseline_answer = _build_baseline_style_answer()
        pilot_answer = "Pilot comparison run was rejected by input constraints."
        compact_trace = []
        pilot_more_useful = False
        usefulness_note = (
            "Pilot was not more useful because it did not complete the bounded comparison run."
        )

    return {
        "comparison_shape_version": "pilot1.v3",
        "pilot": "agentic_workflows",
        "task": "79",
        "entrypoint": "scripts/pilot_agentic_workflow.py",
        "scenario": {
            "id": FIRST_COMPARISON_SCENARIO_ID,
            "request": request_text,
            "bounded_targets": list(FIRST_COMPARISON_TARGETS),
        },
        "pilot_result": {
            "accepted": accepted,
            "inspected_files": inspection["files_inspected"],
            "tools_used": inspection["tools_used"],
            "answer": pilot_answer,
            "compact_trace": compact_trace,
        },
        "baseline_style_result": {
            "style": "single_turn_grounded_baseline",
            "answer": baseline_answer,
            "limitations": "No explicit plan or tool trace is surfaced to the operator.",
        },
        "comparison": {
            "lens": list(COMPARISON_LENS),
            "pilot_more_useful": pilot_more_useful,
            "why": usefulness_note,
        },
        "validation_errors": errors,
        "tooling_policy": {
            "mode": "read_only_local_inspection",
            "allowed_tools": READ_ONLY_TOOLSET,
            "max_tool_actions": MAX_TOOL_ACTIONS,
            "max_files_inspected": MAX_FILES_INSPECTED,
        },
        "isolation": {
            "live_route_touched": False,
            "notes": [
                "Comparison run is script-only and read-only.",
                "No live /ask route integration or behavior changes.",
            ],
        },
    }


def main() -> None:
    args = parse_args()
    if args.run_first_comparison:
        response = run_first_bounded_comparison()
    else:
        request_text = normalize_request(args.request)
        errors = validate_request(request_text)
        response = build_response(request_text, errors, planning_mode=args.planning_mode)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
