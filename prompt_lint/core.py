from __future__ import annotations

from typing import List, Callable

from .models import LintIssue, Severity
from .rules import ALL_RULES


RuleFunc = Callable[[str], List[LintIssue]]


def lint_prompt(prompt_text: str, rules: list[RuleFunc] | None = None) -> List[LintIssue]:
    """
    Lint a prompt and return a list of LintIssue objects.

    Parameters
    ----------
    prompt_text:
        The prompt string to analyze.
    rules:
        Optional list of rule functions. If not provided, uses ALL_RULES.

    Returns
    -------
    List[LintIssue]
        All issues emitted by the active rules.
    """
    active_rules: list[RuleFunc] = rules or ALL_RULES
    issues: List[LintIssue] = []

    for rule in active_rules:
        try:
            issues.extend(rule(prompt_text))
        except Exception as exc:  # pragma: no cover - defensive
            issues.append(
                LintIssue(
                    rule_id=f"rule-error:{getattr(rule, '__name__', 'unknown')}",
                    severity=Severity.ERROR,
                    message=f"Rule {rule!r} failed with error: {exc}",
                )
            )

    return issues
