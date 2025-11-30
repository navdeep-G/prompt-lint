from __future__ import annotations

import re
from typing import List

from .models import LintIssue, Severity


def conflicting_length_rule(prompt: str) -> List[LintIssue]:
    """
    Detects conflicting length instructions like:
    - 'brief' + 'detailed'
    - 'short' + 'comprehensive'
    """
    lower = prompt.lower()

    short_words = ["short", "brief", "concise", "succinct"]
    long_words = ["long", "detailed", "comprehensive", "in-depth", "thorough"]

    has_short = any(word in lower for word in short_words)
    has_long = any(word in lower for word in long_words)

    if has_short and has_long:
        return [
            LintIssue(
                rule_id="conflicting-length",
                severity=Severity.WARNING,
                message=(
                    "Prompt contains conflicting length instructions "
                    "(e.g. both 'brief' and 'detailed')."
                ),
            )
        ]

    return []


def unbounded_length_rule(prompt: str) -> List[LintIssue]:
    """
    Detects phrases that suggest unbounded or extremely long output.
    """
    lower = prompt.lower()

    phrases = [
        "as much as you can",
        "as much detail as possible",
        "infinite detail",
        "no limit",
        "write endlessly",
        "write forever",
        "never stop",
        "write as long as you can",
        "exhaustive detail",
    ]

    if any(p in lower for p in phrases):
        return [
            LintIssue(
                rule_id="unbounded-length",
                severity=Severity.WARNING,
                message=(
                    "Prompt encourages unbounded output length "
                    "(e.g. 'as much as you can', 'as much detail as possible')."
                ),
            )
        ]

    return []


def missing_format_rule(prompt: str) -> List[LintIssue]:
    """
    Warns if the prompt appears to request non-trivial output but doesn't specify a format.
    """
    lower = prompt.lower()

    format_keywords = [
        "json",
        "yaml",
        "yml",
        "xml",
        "markdown",
        "md",
        "table",
        "csv",
        "bullet",
        "bulleted list",
        "numbered list",
        "list of",
        "step-by-step",
    ]

    has_format = any(word in lower for word in format_keywords)

    # Heuristic: only warn if the prompt seems like it's asking for some work.
    is_tasky = bool(
        re.search(
            r"\b(write|explain|describe|generate|summarize|create|list|analyze)\b",
            lower,
        )
    )

    if not has_format and is_tasky:
        return [
            LintIssue(
                rule_id="no-format-specified",
                severity=Severity.INFO,
                message=(
                    "Prompt does not specify an explicit output format "
                    "(e.g. JSON, list, table, bullet points)."
                ),
            )
        ]

    return []


def vague_objective_rule(prompt: str) -> List[LintIssue]:
    """
    Warns on vague objectives like 'etc.' or 'and so on' that may leave the task underspecified.
    """
    lower = prompt.lower()
    if "etc." in lower or "and so on" in lower:
        return [
            LintIssue(
                rule_id="vague-objective",
                severity=Severity.INFO,
                message=(
                    "Prompt contains vague objectives (e.g. 'etc.', 'and so on') "
                    "that may lead to underspecified outputs."
                ),
            )
        ]

    return []


def multiple_tasks_rule(prompt: str) -> List[LintIssue]:
    """
    Heuristic to detect multiple tasks in one prompt.
    Example hint: multiple imperative verbs + 'also'.
    """
    lower = prompt.lower()

    verbs = re.findall(
        r"\b(write|explain|describe|list|summarize|analyze|generate|compare|contrast)\b",
        lower,
    )
    many_verbs = len(verbs) >= 2

    if many_verbs and "also" in lower:
        return [
            LintIssue(
                rule_id="multiple-tasks",
                severity=Severity.INFO,
                message=(
                    "Prompt appears to contain multiple tasks; consider splitting into"
                    " separate prompts or steps."
                ),
            )
        ]

    return []


def missing_role_rule(prompt: str) -> List[LintIssue]:
    """
    Suggests defining a role/persona if none appears to be present.
    E.g. 'You are a helpful assistant' / 'You are an expert X'.
    """
    lower = prompt.lower()

    # crude heuristic for a role definition
    role_patterns = [
        r"you are an? [a-z ]+expert",
        r"you are an? [a-z ]+assistant",
        r"you are an? [a-z ]+bot",
        r"you are a large language model",
    ]

    has_role = any(re.search(p, lower) for p in role_patterns)

    # Only warn if it looks like instructions are being given at all
    looks_like_instructions = ("you" in lower and "are" in lower) or "assistant" in lower

    if not has_role and looks_like_instructions:
        return [
            LintIssue(
                rule_id="missing-role",
                severity=Severity.INFO,
                message=(
                    "Prompt does not define an explicit role/persona for the model "
                    "(e.g. 'You are an expert technical writer.')."
                ),
            )
        ]

    return []


ALL_RULES = [
    conflicting_length_rule,
    unbounded_length_rule,
    missing_format_rule,
    vague_objective_rule,
    multiple_tasks_rule,
    missing_role_rule,
]
