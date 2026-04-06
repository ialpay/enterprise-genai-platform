"""Deterministic request classification helpers for `/ask`."""

from __future__ import annotations

from enum import StrEnum


class RequestClass(StrEnum):
    NORMAL = "normal"
    SUSPICIOUS_OVERRIDE = "suspicious_override"
    HIDDEN_INSTRUCTION_REQUEST = "hidden_instruction_request"


HIDDEN_INSTRUCTION_TERMS = (
    "system prompt",
    "developer prompt",
    "hidden instruction",
    "hidden prompt",
    "internal prompt",
)

SUSPICIOUS_OVERRIDE_TERMS = (
    "ignore all rules",
    "ignore previous instructions",
    "override instructions",
    "bypass safety",
    "jailbreak",
)


def classify_request(question: str) -> RequestClass:
    lowered = question.lower()

    if any(term in lowered for term in HIDDEN_INSTRUCTION_TERMS):
        return RequestClass.HIDDEN_INSTRUCTION_REQUEST

    if any(term in lowered for term in SUSPICIOUS_OVERRIDE_TERMS):
        return RequestClass.SUSPICIOUS_OVERRIDE

    return RequestClass.NORMAL
