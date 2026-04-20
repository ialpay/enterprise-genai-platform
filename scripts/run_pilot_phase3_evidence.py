"""Pilot 1 Phase 3 bounded evidence runner for repeated planning stability checks."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT_SCRIPT_PATH = REPO_ROOT / "scripts" / "pilot_agentic_workflow.py"
DEFAULT_AUTO_ATTEMPTS = 3
MAX_AUTO_ATTEMPTS = 5
EXPECTED_MAX_PLAN_STEPS = 3

SCENARIOS: tuple[dict[str, str], ...] = (
    {
        "id": "pilot1_phase3_next_step_repeat",
        "request": (
            "Analyze the current repository baseline and identify the next most "
            "reasonable implementation step using a bounded multi-step read-only workflow."
        ),
    },
    {
        "id": "pilot1_phase3_live_governance_repeat",
        "request": (
            "Summarize current /ask governance behaviors and one unresolved risk using "
            "docs/status.md and docs/codex_tasks.md in a bounded repository workflow."
        ),
    },
    {
        "id": "pilot1_phase3_reliability_repeat",
        "request": (
            "Assess whether assisted planning is currently reliable using docs/pilot-track.md "
            "and scripts/pilot_agentic_workflow.py evidence fields in a bounded repository workflow."
        ),
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Pilot 1 Phase 3 bounded evidence scenarios with one code-only control "
            "and repeated auto attempts."
        )
    )
    parser.add_argument(
        "--auto-attempts",
        type=int,
        default=DEFAULT_AUTO_ATTEMPTS,
        help=f"Bounded number of auto runs per scenario (1-{MAX_AUTO_ATTEMPTS}).",
    )
    args = parser.parse_args()
    if args.auto_attempts < 1 or args.auto_attempts > MAX_AUTO_ATTEMPTS:
        parser.error(f"--auto-attempts must be between 1 and {MAX_AUTO_ATTEMPTS}")
    return args


def _run_pilot_request(request: str, planning_mode: str) -> dict[str, Any]:
    command = [
        sys.executable,
        str(PILOT_SCRIPT_PATH),
        "--planning-mode",
        planning_mode,
        request,
    ]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        return {
            "accepted": False,
            "pilot_response": {
                "planning_mode": planning_mode,
                "planning_source": "runner_subprocess_error",
                "planning_fallback_reason": "non_zero_exit",
                "tools_used": [],
                "files_inspected": [],
                "final_answer": "",
                "ordered_steps": [],
                "execution_trace": [],
            },
            "validation_errors": [f"subprocess returned non-zero exit: {result.returncode}"],
            "tooling_policy": {
                "allowed_tools": {},
                "max_tool_actions": 0,
                "max_files_inspected": 0,
            },
            "runner_stderr": stderr,
            "runner_stdout": stdout,
        }

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "accepted": False,
            "pilot_response": {
                "planning_mode": planning_mode,
                "planning_source": "runner_parse_error",
                "planning_fallback_reason": "invalid_json_output",
                "tools_used": [],
                "files_inspected": [],
                "final_answer": "",
                "ordered_steps": [],
                "execution_trace": [],
            },
            "validation_errors": ["pilot output was not valid JSON"],
            "tooling_policy": {
                "allowed_tools": {},
                "max_tool_actions": 0,
                "max_files_inspected": 0,
            },
            "runner_stderr": stderr,
            "runner_stdout": stdout,
        }

    if stderr:
        payload["runner_stderr"] = stderr
    return payload


def _evaluate_boundedness(payload: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    pilot_response = payload.get("pilot_response", {})
    tooling_policy = payload.get("tooling_policy", {})

    ordered_steps = pilot_response.get("ordered_steps", []) or []
    execution_trace = pilot_response.get("execution_trace", []) or []
    files_inspected = pilot_response.get("files_inspected", []) or []
    tools_used = pilot_response.get("tools_used", []) or []
    allowed_tools = set((tooling_policy.get("allowed_tools") or {}).keys())

    max_tool_actions = tooling_policy.get("max_tool_actions")
    if not isinstance(max_tool_actions, int):
        max_tool_actions = 0

    max_files_inspected = tooling_policy.get("max_files_inspected")
    if not isinstance(max_files_inspected, int):
        max_files_inspected = 0

    checks = {
        "request_accepted": bool(payload.get("accepted", False)),
        "no_validation_errors": not bool(payload.get("validation_errors", [])),
        "step_cap_ok": len(ordered_steps) <= EXPECTED_MAX_PLAN_STEPS,
        "tool_action_cap_ok": len(execution_trace) <= max_tool_actions,
        "file_cap_ok": len(files_inspected) <= max_files_inspected,
        "allowed_tools_only": all(tool_name in allowed_tools for tool_name in tools_used),
    }
    return all(checks.values()), checks


def _build_run_record(
    *,
    scenario_id: str,
    run_label: str,
    attempt_index: int,
    planning_mode: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    pilot_response = payload.get("pilot_response", {})
    boundedness_ok, boundedness_checks = _evaluate_boundedness(payload)

    return {
        "scenario_id": scenario_id,
        "run_label": run_label,
        "attempt_index": attempt_index,
        "planning_mode": planning_mode,
        "planning_source": pilot_response.get("planning_source"),
        "planning_fallback_reason": pilot_response.get("planning_fallback_reason"),
        "tools_used": pilot_response.get("tools_used", []),
        "files_inspected": pilot_response.get("files_inspected", []),
        "final_answer": pilot_response.get("final_answer", ""),
        "boundedness_ok": boundedness_ok,
        "boundedness_checks": boundedness_checks,
    }


def _normalize_answer(answer_text: str) -> str:
    return " ".join(answer_text.split()).strip().lower()


def _summarize_scenario_runs(
    *,
    control_run: dict[str, Any],
    auto_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    auto_sources = [run["planning_source"] for run in auto_runs]
    assisted_count = auto_sources.count("ollama_assisted")
    fallback_count = auto_sources.count("ollama_fallback_to_code")
    fallback_reasons = Counter(
        reason for reason in (run["planning_fallback_reason"] for run in auto_runs) if reason
    )
    boundedness_all_runs = control_run["boundedness_ok"] and all(
        run["boundedness_ok"] for run in auto_runs
    )

    auto_answer_set = {_normalize_answer(run["final_answer"]) for run in auto_runs}
    auto_files_set = {tuple(run["files_inspected"]) for run in auto_runs}
    auto_sources_set = set(auto_sources)

    control_trace_visible = bool(control_run["tools_used"] and control_run["files_inspected"])
    auto_trace_visible_count = sum(
        1 for run in auto_runs if run["tools_used"] and run["files_inspected"]
    )
    auto_runs_count = len(auto_runs)
    auto_trace_visible_rate = (
        round(auto_trace_visible_count / auto_runs_count, 3) if auto_runs_count else 0.0
    )
    auto_non_empty_answer_count = sum(1 for run in auto_runs if run["final_answer"].strip())
    auto_non_empty_answer_rate = (
        round(auto_non_empty_answer_count / auto_runs_count, 3) if auto_runs_count else 0.0
    )

    return {
        "auto_assisted_count": assisted_count,
        "auto_fallback_count": fallback_count,
        "auto_planning_source_counts": dict(Counter(auto_sources)),
        "auto_fallback_reason_counts": dict(fallback_reasons),
        "boundedness_all_runs": boundedness_all_runs,
        "repeat_consistency": {
            "auto_planning_source_consistent": len(auto_sources_set) == 1,
            "auto_final_answer_consistent": len(auto_answer_set) == 1,
            "auto_files_inspected_consistent": len(auto_files_set) == 1,
        },
        "operator_usefulness_indicators": {
            "control_trace_visible": control_trace_visible,
            "auto_trace_visible_rate": auto_trace_visible_rate,
            "auto_non_empty_final_answer_rate": auto_non_empty_answer_rate,
        },
    }


def run_phase3_evidence_round(auto_attempts: int) -> dict[str, Any]:
    scenario_reports: list[dict[str, Any]] = []
    aggregate_auto_sources: Counter[str] = Counter()
    aggregate_fallback_reasons: Counter[str] = Counter()
    all_runs_bounded = True

    for scenario in SCENARIOS:
        scenario_id = scenario["id"]
        request = scenario["request"]

        control_payload = _run_pilot_request(request=request, planning_mode="code_only")
        control_run = _build_run_record(
            scenario_id=scenario_id,
            run_label="control",
            attempt_index=0,
            planning_mode="code_only",
            payload=control_payload,
        )

        auto_runs: list[dict[str, Any]] = []
        for attempt_index in range(1, auto_attempts + 1):
            auto_payload = _run_pilot_request(request=request, planning_mode="auto")
            auto_run = _build_run_record(
                scenario_id=scenario_id,
                run_label="auto",
                attempt_index=attempt_index,
                planning_mode="auto",
                payload=auto_payload,
            )
            auto_runs.append(auto_run)

        scenario_summary = _summarize_scenario_runs(control_run=control_run, auto_runs=auto_runs)
        aggregate_auto_sources.update(scenario_summary["auto_planning_source_counts"])
        aggregate_fallback_reasons.update(scenario_summary["auto_fallback_reason_counts"])
        all_runs_bounded = all_runs_bounded and scenario_summary["boundedness_all_runs"]

        scenario_reports.append(
            {
                "scenario_id": scenario_id,
                "request": request,
                "control_run": control_run,
                "auto_runs": auto_runs,
                "summary": scenario_summary,
            }
        )

    total_auto_runs = len(SCENARIOS) * auto_attempts
    overall_consistency = {
        "all_scenarios_auto_source_consistent": all(
            report["summary"]["repeat_consistency"]["auto_planning_source_consistent"]
            for report in scenario_reports
        ),
        "all_scenarios_auto_answer_consistent": all(
            report["summary"]["repeat_consistency"]["auto_final_answer_consistent"]
            for report in scenario_reports
        ),
    }

    return {
        "round_id": "pilot1_phase3_repeated_assisted_planning_stability",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "scripts/pilot_agentic_workflow.py",
        "auto_attempts_per_scenario": auto_attempts,
        "scenario_count": len(SCENARIOS),
        "scenario_reports": scenario_reports,
        "summary": {
            "total_auto_runs": total_auto_runs,
            "overall_auto_planning_source_counts": dict(aggregate_auto_sources),
            "overall_auto_fallback_reason_counts": dict(aggregate_fallback_reasons),
            "overall_assisted_count": aggregate_auto_sources.get("ollama_assisted", 0),
            "overall_fallback_count": aggregate_auto_sources.get("ollama_fallback_to_code", 0),
            "overall_boundedness_invariants_held": all_runs_bounded,
            "repeat_consistency": overall_consistency,
        },
    }


def main() -> None:
    args = parse_args()
    result = run_phase3_evidence_round(auto_attempts=args.auto_attempts)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
