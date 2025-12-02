from __future__ import annotations

import re
from typing import Any, List, Mapping

from .models import LintIssue, Severity
from .rule_types import Rule


# --- Generic rule primitives -------------------------------------------------


def conflicting_keywords_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    text = prompt.lower()
    group_a = [s.lower() for s in options.get("group_a", ())]
    group_b = [s.lower() for s in options.get("group_b", ())]

    found_a = [s for s in group_a if s in text]
    found_b = [s for s in group_b if s in text]

    if found_a and found_b:
        msg = options.get(
            "message",
            "Prompt contains conflicting instructions: "
            f"{', '.join(found_a)} vs {', '.join(found_b)}.",
        )
        return [
            LintIssue(
                rule_id=options.get("rule_id", "conflicting-keywords"),
                severity=Severity.WARNING,
                message=msg,
                data={"group_a": found_a, "group_b": found_b},
            )
        ]
    return []


def phrase_match_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    text = prompt.lower()
    phrases = [p.lower() for p in options.get("phrases", ())]
    matches = [p for p in phrases if p in text]
    if not matches:
        return []

    msg = options.get(
        "message",
        "Prompt contains discouraged phrases: " + ", ".join(matches),
    )
    return [
        LintIssue(
            rule_id=options.get("rule_id", "phrase-match"),
            severity=Severity.WARNING,
            message=msg,
            data={"phrases": matches},
        )
    ]


def must_contain_one_of_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    text = prompt.lower()
    needles = [n.lower() for n in options.get("needles", ())]
    if any(n in text for n in needles):
        return []

    msg = options.get(
        "message",
        "Prompt does not contain any required pattern.",
    )
    return [
        LintIssue(
            rule_id=options.get("rule_id", "missing-pattern"),
            severity=Severity.INFO,
            message=msg,
            data={"needles": needles},
        )
    ]


# --- More specialised checkers used for built‑in rules -----------------------

TASK_VERB_RE = re.compile(
    r"\b("
    r"write|explain|list|summarize|summarise|generate|create|build|design|"
    r"give|tell|compare|describe|analyze|analyse|outline"
    r")\b",
    re.IGNORECASE,
)

ROLE_HINT_RE = re.compile(
    r"\b("
    r"you are|you're|act as|your role is|you will act as"
    r")\b",
    re.IGNORECASE,
)


def vague_objective_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    extended_options = dict(options)
    if "phrases" not in extended_options:
        extended_options["phrases"] = [
            "etc.",
            "etc",
            "and so on",
            "and so forth",
        ]
    extended_options.setdefault(
        "message",
        "Prompt ends with vague objectives such as 'etc.' or 'and so on'.",
    )
    extended_options.setdefault("rule_id", "vague-objective")
    return phrase_match_checker(prompt, extended_options)


def multiple_tasks_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    max_tasks = int(options.get("max_tasks", 2))
    verbs = TASK_VERB_RE.findall(prompt)
    also_count = len(re.findall(r"\balso\b", prompt, flags=re.IGNORECASE))
    estimated_tasks = len(verbs) + also_count

    if estimated_tasks <= max_tasks:
        return []

    msg = options.get(
        "message",
        "Prompt may contain multiple tasks; consider splitting it into smaller prompts.",
    )
    return [
        LintIssue(
            rule_id=options.get("rule_id", "multiple-tasks"),
            severity=Severity.INFO,
            message=msg,
            data={"estimated_tasks": estimated_tasks},
        )
    ]


def missing_role_checker(prompt: str, options: Mapping[str, Any]) -> List[LintIssue]:
    if ROLE_HINT_RE.search(prompt):
        return []

    # Only flag if there appear to be instructions.
    if not TASK_VERB_RE.search(prompt):
        return []

    msg = options.get(
        "message",
        "Consider defining a clear role/persona for the model "
        "(e.g. 'You are an expert data analyst.').",
    )
    return [
        LintIssue(
            rule_id=options.get("rule_id", "missing-role"),
            severity=Severity.INFO,
            message=msg,
        )
    ]


# --- Concrete built‑in rules -------------------------------------------------


CONFLICTING_LENGTH_RULE = Rule(
    id="conflicting-length",
    description="Detects conflicting length instructions like 'brief' and 'detailed'.",
    default_severity=Severity.WARNING,
    checker=conflicting_keywords_checker,
    default_options={
        "rule_id": "conflicting-length",
        "group_a": ["brief", "short", "concise", "succinct"],
        "group_b": ["detailed", "thorough", "in depth", "extremely detailed"],
        "message": (
            "Prompt contains conflicting length instructions "
            "(e.g. both 'brief' and 'detailed')."
        ),
    },
    tags={"length", "style"},
)


UNBOUNDED_LENGTH_RULE = Rule(
    id="unbounded-length",
    description="Flags phrases that suggest unbounded output length.",
    default_severity=Severity.WARNING,
    checker=phrase_match_checker,
    default_options={
        "rule_id": "unbounded-length",
        "phrases": [
            "as much as you can",
            "write as much as you can",
            "as much detail as possible",
            "with infinite detail",
            "write as much as possible",
        ],
        "message": (
            "Prompt encourages unbounded output length "
            "(e.g. 'as much as you can', 'as much detail as possible')."
        ),
    },
    tags={"length"},
)


NO_FORMAT_SPECIFIED_RULE = Rule(
    id="no-format-specified",
    description="Warn when no explicit output format is given.",
    default_severity=Severity.INFO,
    checker=must_contain_one_of_checker,
    default_options={
        "rule_id": "no-format-specified",
        "needles": [
            "json",
            "yaml",
            "table",
            "markdown table",
            "bullets",
            "bullet points",
            "list of",
            "csv",
        ],
        "message": (
            "Prompt does not specify an explicit output format "
            "(e.g. JSON, list, table, bullet points)."
        ),
    },
    tags={"format"},
)


VAGUE_OBJECTIVE_RULE = Rule(
    id="vague-objective",
    description="Warns on vague endings like 'etc.' or 'and so on'.",
    default_severity=Severity.INFO,
    checker=vague_objective_checker,
    default_options={
        "rule_id": "vague-objective",
    },
    tags={"style"},
)


MULTIPLE_TASKS_RULE = Rule(
    id="multiple-tasks",
    description="Heuristic for 'too many tasks in one prompt'.",
    default_severity=Severity.INFO,
    checker=multiple_tasks_checker,
    default_options={
        "rule_id": "multiple-tasks",
        "max_tasks": 2,
    },
    tags={"structure"},
)


MISSING_ROLE_RULE = Rule(
    id="missing-role",
    description="Suggests defining a clear role/persona for the model.",
    default_severity=Severity.INFO,
    checker=missing_role_checker,
    default_options={
        "rule_id": "missing-role",
    },
    tags={"style"},
)


BUILTIN_RULES = [
    CONFLICTING_LENGTH_RULE,
    UNBOUNDED_LENGTH_RULE,
    NO_FORMAT_SPECIFIED_RULE,
    VAGUE_OBJECTIVE_RULE,
    MULTIPLE_TASKS_RULE,
    MISSING_ROLE_RULE,
]
