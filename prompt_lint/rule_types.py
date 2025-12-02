from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Mapping, Set

from .models import LintIssue, Severity

CheckerFn = Callable[[str, Mapping[str, Any]], List[LintIssue]]


@dataclass
class Rule:
    """A single lint rule with metadata and configuration.

    Rules are small checker functions plus some metadata (id, severity,
    default options, tags). They can be configured via ``prompt-lint.toml``.
    """

    id: str
    description: str
    default_severity: Severity
    checker: CheckerFn
    default_options: Mapping[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)


def wrap_simple_rule(
    fn: Callable[[str], List[LintIssue]],
    *,
    rule_id: str | None = None,
    description: str = "",
    default_severity: Severity = Severity.WARNING,
) -> Rule:
    """Adapter for legacy ``prompt -> [LintIssue]`` rules.

    This keeps backwards compatibility with earlier versions of ``prompt-lint``
    where rules were plain functions that did not receive options.
    """
    rid = rule_id or getattr(fn, "__name__", "custom-rule")

    def checker(prompt: str, options):
        # ``options`` are ignored for legacy rules
        return fn(prompt)

    return Rule(
        id=rid,
        description=description or (fn.__doc__ or ""),
        default_severity=default_severity,
        checker=checker,
    )
