from __future__ import annotations

from typing import Callable, List, Mapping, Sequence, Union, Any

from .config import LintConfig, load_config
from .models import LintIssue, Severity
from .rule_types import Rule, wrap_simple_rule
from .rules_registry import get_all_rules

SimpleRuleFn = Callable[[str], List[LintIssue]]
RuleLike = Union[Rule, SimpleRuleFn]


def _normalize_rules(rules: Sequence[RuleLike] | None) -> List[Rule]:
    if rules is None:
        return get_all_rules()

    normalised: List[Rule] = []
    for r in rules:
        if isinstance(r, Rule):
            normalised.append(r)
        else:
            normalised.append(
                wrap_simple_rule(
                    r,
                    rule_id=getattr(r, "rule_id", None)
                    or getattr(r, "__name__", "custom-rule"),
                    description=getattr(r, "__doc__", "") or "",
                    default_severity=getattr(r, "default_severity", Severity.WARNING),
                )
            )
    return normalised


def lint_prompt(
    prompt: str,
    rules: Sequence[RuleLike] | None = None,
    *,
    config: LintConfig | None = None,
    load_config_from_disk: bool = True,
) -> List[LintIssue]:
    """Lint *prompt* and return a list of :class:`LintIssue` objects.

    Parameters
    ----------
    prompt:
        Prompt text to analyse.
    rules:
        Optional sequence of :class:`Rule` objects or legacy
        ``(prompt: str) -> List[LintIssue]`` functions. If omitted, built‑in
        rules (and any installed plugin rules) are used.
    config:
        Optional :class:`LintConfig`. If not provided and
        ``load_config_from_disk`` is true, ``prompt-lint.toml`` is discovered
        by walking up from the current working directory.
    load_config_from_disk:
        If ``False``, skip automatic config discovery when *config* is
        ``None`` and use the default config instead.
    """
    rule_objs = _normalize_rules(rules)

    if config is None:
        if load_config_from_disk:
            config = load_config()
        else:
            config = LintConfig()

    issues: List[LintIssue] = []

    for rule in rule_objs:
        opts = config.get_rule_options(rule.id)
        if not opts.enabled:
            continue

        merged_options: dict[str, Any] = dict(rule.default_options)
        merged_options.update(opts.options)

        severity = opts.severity or rule.default_severity

        for issue in rule.checker(prompt, merged_options):
            # Normalise severity and rule id in case the checker did not set them.
            issue.rule_id = rule.id
            issue.severity = severity
            issues.append(issue)

    return issues
